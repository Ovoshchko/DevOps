FROM python:3.11-slim

WORKDIR /srv

RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.30.0 \
    pydantic==2.7.4 \
    httpx==0.27.0 \
    influxdb-client==1.43.0

COPY backend /srv/backend

ENV PYTHONPATH=/srv

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
