FROM python:3.11-slim

WORKDIR /srv

COPY backend /srv/backend

RUN pip install --no-cache-dir /srv/backend

ENV PYTHONPATH=/srv

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
