FROM python:3.11-slim as builder

WORKDIR /srv/backend

COPY backend/pyproject.toml /srv/backend/pyproject.toml

RUN pip install --no-cache-dir --prefix=/install /srv/backend

COPY backend /srv/backend


FROM python:3.11-slim

COPY --from=builder /install /usr/local
COPY backend /srv/backend

ENV PYTHONPATH=/srv/backend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
