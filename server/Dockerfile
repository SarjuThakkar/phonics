# The recordings upload endpoint. Serves nothing to visitors; the audio files
# themselves are served by the nginx container from the same directory.
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir "fastapi==0.115.*" "uvicorn[standard]==0.32.*" \
    "python-multipart==0.0.*"

COPY app.py .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
