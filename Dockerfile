# Root Dockerfile for Railway (the API service). Building with Docker bypasses
# nixpacks+mise (which was failing on python@3.11.9 attestation verification).
# Vercel deploys apps/web separately and ignores this file.
FROM python:3.11-slim

WORKDIR /srv

# Deps first for layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code + the shared packages/ tree (main.py imports from repo root).
COPY apps/api ./apps/api
COPY packages ./packages

ENV PYTHONPATH=/srv
EXPOSE 8000

# Railway injects $PORT; default to 8000 for local `docker run`.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir apps/api"]
