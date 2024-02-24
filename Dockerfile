FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update
RUN python -m pip install --upgrade pip

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY update-dns-record update-dns-record

ENTRYPOINT ["python", "-m", "update-dns-record"]