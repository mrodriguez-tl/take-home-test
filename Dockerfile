FROM python:3.9-slim

RUN apt-get update && apt-get clean

COPY poetry.lock pyproject.toml ./

RUN set -ex \
  && poetry export --without-hashes --format requirements.txt > requirements.txt \
  && pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .

USER app