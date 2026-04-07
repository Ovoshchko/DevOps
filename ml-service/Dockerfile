FROM python:3.11-slim AS builder

WORKDIR /srv/ml-service

COPY pyproject.toml .
COPY app ./app
COPY models ./models

RUN pip install --no-cache-dir --prefix=/install .


FROM python:3.11-slim

WORKDIR /srv/ml-service

COPY --from=builder /install /usr/local
COPY app ./app
COPY models ./models

ENV PYTHONPATH=/srv/ml-service
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
