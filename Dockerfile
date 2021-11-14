FROM python:3.9-slim-buster

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN apt update && apt upgrade -y && apt install git -y \
    && pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . /code
RUN chmod +x entrypoint.sh
ENTRYPOINT [ "sh", "entrypoint.sh" ]