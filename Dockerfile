# base image
FROM python:3.10-slim-bullseye AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# builder image
FROM python-base AS builder

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        wget \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python3 - && \
    chmod a+x "${POETRY_HOME}/bin/poetry"

WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml README.md ./
COPY info_gpt info_gpt
RUN poetry install --with=api

# final image
FROM python-base AS production

ENV FASTAPI_ENV=production
EXPOSE 8000

# copy only the already create virtualenv
COPY --from=builder $VENV_PATH $VENV_PATH
RUN . "${VENV_PATH}/bin/activate"

WORKDIR /app

# Create user with the name poetry
RUN groupadd -g 1500 poetry && \
    useradd -m -u 1500 -g poetry poetry

COPY --chown=poetry:poetry info_gpt info_gpt
COPY --chown=poetry:poetry .db .db
USER poetry

CMD [ "gunicorn", "info_gpt.api.app:app", "--worker-class uvicorn.workers.UvicornWorker", "--bind 0.0.0.0:8000", "--workers 4"]
