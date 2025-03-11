FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


ENV POETRY_VERSION=2.1.1
RUN pip install poetry==$POETRY_VERSION

WORKDIR /fstorage

COPY README.md pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi

COPY fstorage/ fstorage/
COPY migrations/ migrations/
COPY alembic.ini alembic.ini

COPY fstorage/config/.env.example fstorage/config/.env

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["sh", "/entrypoint.sh"]