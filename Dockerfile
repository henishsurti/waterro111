FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
# Only what the server needs: no demo database, tests or launcher scripts in the image.
COPY backend/app.py backend/backup.py backend/
COPY database.sql index.html ./
COPY assets assets
RUN useradd --system --uid 10001 app && mkdir -p /app/data /backups && chown app /app/data /backups
USER app
ENV AQUAFLOW_DB=/app/data/aquaflow.db
WORKDIR /app/backend
EXPOSE 8799
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8799/api/health',timeout=3)"
# One worker on purpose: sign-in sessions are held in memory.
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8799","--workers","1","--proxy-headers","--forwarded-allow-ips","*"]
