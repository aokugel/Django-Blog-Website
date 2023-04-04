# syntax=docker/dockerfile:1
FROM python:3.9.15-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /code/

RUN --mount=type=secret,id=AZURE_STORAGE_ACCOUNT
RUN --mount=type=secret,id=BLOB_MEDIA_KEY
RUN --mount=type=secret,id=BLOB_STATIC_KEY
RUN export AZURE_STORAGE_ACCOUNT=$(cat /run/secrets/AZURE_STORAGE_ACCOUNT)
RUN export BLOB_MEDIA_KEY=$(cat /run/secrets/BLOB_MEDIA_KEY)
RUN export BLOB_STATIC_KEY=$(cat /run/secrets/BLOB_STATIC_KEY)


RUN python manage.py collectstatic --noinput