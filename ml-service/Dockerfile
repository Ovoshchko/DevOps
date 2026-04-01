FROM python:3.11-slim

WORKDIR /srv/ml-service

COPY ml-service/pyproject.toml /srv/ml-service/pyproject.toml

RUN pip install --no-cache-dir /srv/ml-service

COPY ml-service /srv/ml-service

ENV PYTHONPATH=/srv/ml-service

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
