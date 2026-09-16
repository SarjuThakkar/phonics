#!/usr/bin/env python3
"""The one non-static piece of this site: a place to put recordings.

Everything else here is files on a disk. This exists so that recording the 93
letter sounds on a phone doesn't mean ferrying 93 downloads off the phone by
hand -- /record.html posts each take straight here and it is live immediately.

Deliberately small, and deliberately suspicious of its own input, because it is
a write path on a public hostname:

  * a bearer token is required for every write
  * the filename is never taken from the client -- the id is looked up in the
    speech index and the extension comes from the content type, so there is no
    path to traverse and no name to inject
  * uploads are capped, and only audio types are accepted
  * nothing else on the box is reachable: it writes into one directory

Reads (which ids exist) are open, because that is already public: the audio
files themselves are served to every visitor by nginx.
"""

from __future__ import annotations

import json
import os
import pathlib
import re

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_413_REQUEST_ENTITY_TOO_LARGE

WEB = pathlib.Path(os.environ.get("PHONICS_WEB", "/web"))
HUMAN = WEB / "audio" / "human"
INDEX = WEB / "data" / "speech-index.json"
MANIFEST = WEB / "data" / "audio-manifest.json"

TOKEN = os.environ.get("UPLOAD_TOKEN", "")
MAX_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", 8 * 1024 * 1024))

# What a browser's MediaRecorder actually produces, plus the formats a file
# might arrive in if recorded elsewhere. The extension comes from this table,
# never from the uploaded filename.
TYPES = {
    "audio/mp4": "m4a",
    "audio/m4a": "m4a",
    "audio/x-m4a": "m4a",
    "audio/aac": "m4a",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/wave": "wav",
    "audio/flac": "flac",
}
PLAYABLE = {".mp3", ".m4a", ".ogg", ".oga", ".wav", ".webm", ".aac", ".flac"}

app = FastAPI(title="phonics recordings", docs_url=None, redoc_url=None)


def speech_index() -> dict[str, dict]:
    """Read fresh every time: lessons get authored while this is running."""
    try:
        return {e["id"]: e for e in json.loads(INDEX.read_text())["entries"]}
    except Exception:
        return {}


def require_token(request: Request) -> None:
    if not TOKEN:
        raise HTTPException(503, "no upload token configured on the server")
    supplied = request.headers.get("authorization", "")
    if not supplied.startswith("Bearer ") or supplied[7:].strip() != TOKEN:
        raise HTTPException(HTTP_401_UNAUTHORIZED, "bad or missing token")


def rebuild_manifest() -> dict:
    """Same shape tools/build_audio_manifest.py writes, kept in step with it."""
    index = speech_index()
    files: dict[str, str] = {}
    for path in sorted(HUMAN.iterdir()) if HUMAN.exists() else []:
        if path.name.startswith(".") or path.suffix.lower() not in PLAYABLE:
            continue
        if path.stem in index:
            files[path.stem] = path.name
    text = {
        re.sub(r"\s+", " ", index[i]["text"].strip().lower()): i
        for i in files
        if index[i]["kind"] != "sound"
    }
    manifest = {"count": len(files), "files": files, "text": text}
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


@app.get("/healthz")
def healthz() -> JSONResponse:
    return JSONResponse({"ok": True, "recorded": len(rebuild_manifest()["files"])})


@app.get("/api/recordings")
def list_recordings() -> JSONResponse:
    """Which ids have audio. Lets the record page show progress on any device --
    the checklist follows the recordings, not the browser."""
    manifest = rebuild_manifest()
    return JSONResponse({"count": manifest["count"], "files": manifest["files"]})


@app.post("/api/recordings/{recording_id}")
async def upload(recording_id: str, file: UploadFile,
                 _: None = Depends(require_token)) -> JSONResponse:
    index = speech_index()
    if recording_id not in index:
        # Not just validation: this is what stops a filename being anything
        # other than one of the ids we generated.
        raise HTTPException(404, f"unknown recording id: {recording_id}")

    content_type = (file.content_type or "").split(";")[0].strip().lower()
    ext = TYPES.get(content_type)
    if not ext:
        raise HTTPException(415, f"unsupported audio type: {content_type or 'unknown'}")

    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            f"recording larger than {MAX_BYTES // 1024 // 1024}MB")
    if not data:
        raise HTTPException(400, "empty recording")

    HUMAN.mkdir(parents=True, exist_ok=True)
    # A re-record replaces the old take, whatever format it was in.
    for old in HUMAN.glob(f"{recording_id}.*"):
        if old.suffix.lower() in PLAYABLE:
            old.unlink()

    target = HUMAN / f"{recording_id}.{ext}"
    target.write_bytes(data)
    manifest = rebuild_manifest()
    return JSONResponse({
        "ok": True,
        "id": recording_id,
        "file": target.name,
        "bytes": len(data),
        "recorded": manifest["count"],
    })


@app.delete("/api/recordings/{recording_id}")
def delete(recording_id: str, _: None = Depends(require_token)) -> JSONResponse:
    if recording_id not in speech_index():
        raise HTTPException(404, f"unknown recording id: {recording_id}")
    removed = []
    for path in HUMAN.glob(f"{recording_id}.*"):
        if path.suffix.lower() in PLAYABLE:
            path.unlink()
            removed.append(path.name)
    manifest = rebuild_manifest()
    return JSONResponse({"ok": True, "removed": removed, "recorded": manifest["count"]})


@app.post("/api/check")
def check(_: None = Depends(require_token)) -> JSONResponse:
    """Lets the record page tell a good token from a bad one before recording."""
    return JSONResponse({"ok": True})
