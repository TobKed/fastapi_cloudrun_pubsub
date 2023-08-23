FROM python:3.11-slim-bookworm as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

######################################################
# BASE STAGE
######################################################
FROM python-base as builder-base
RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        curl \
        libpq-dev && \
        rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

RUN poetry install --only main

######################################################
# DEVELOPMENT STAGE
######################################################
FROM python-base as development
WORKDIR $PYSETUP_PATH

RUN apt-get update && \
        rm -rf /var/lib/apt/lists/*

COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

COPY ./compose/start_api_dev /start_api_dev
RUN chmod +x /start_api_dev

COPY ./compose/start_worker_dev /start_worker_dev
RUN chmod +x /start_worker_dev

RUN poetry install --only dev
COPY . /app
WORKDIR /app
CMD ["/start_api_dev"]

######################################################
# PRODUCTION STAGE
######################################################
FROM python-base as production
RUN apt-get update && \
        rm -rf /var/lib/apt/lists/*
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

COPY ./compose/start_api /start_api
RUN chmod +x /start_api

COPY ./compose/start_worker /start_worker
RUN chmod +x /start_worker

COPY . /app
WORKDIR /app
CMD ["/start_api"]
