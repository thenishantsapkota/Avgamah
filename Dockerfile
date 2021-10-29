# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster

WORKDIR /app
RUN apt update && apt upgrade -y && apt install git -y
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
