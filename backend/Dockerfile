FROM python:3.11-slim AS builder

WORKDIR /srv/backend

COPY pyproject.toml .
COPY app ./app

RUN pip install --no-cache-dir --prefix=/install .


FROM python:3.11-slim

WORKDIR /srv/backend

COPY --from=builder /install /usr/local
COPY app ./app

ENV PYTHONPATH=/srv/backend
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
