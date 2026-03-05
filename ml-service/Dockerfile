FROM python:3.11-slim

WORKDIR /srv/ml-service

RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.30.0 \
    pydantic==2.7.4

COPY ml-service /srv/ml-service

ENV PYTHONPATH=/srv/ml-service

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
