# Recorded voice

Drop audio files here, named after an id from `web/data/speech-index.json`:

    sound-sh.mp3
    word-cat.mp3
    line-a-fat-rat-did-9f21c3.mp3

Then run `python3 tools/build_audio_manifest.py`. The site plays a recording
wherever one exists and falls back to the browser voice everywhere else, so
partial coverage is genuinely useful — and the 93 `sound-*` files are worth far
more than all the rest, because an isolated letter sound is the one thing
speech synthesis cannot do at all.

The easy way to make them is `/record.html` on the site itself: it walks the
list, records from the microphone, and saves each file already named correctly.

Any format a browser can play works (.mp3, .m4a, .ogg, .wav, .webm).
