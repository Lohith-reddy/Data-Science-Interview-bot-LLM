FROM python:3.11-buster as builder

RUN curl -sSL https://install.python-poetry.org | python - && pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root \
    && pip uninstall poetry -y

FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=.venv \
    PATH="/app/.venv/bin:$PATH"

# vectorDB will be hosted on cloud

COPY --from=builder /app/.venv /app/.venv
COPY streamlit_app.py utils.py chatbot_helper.py docs pyproject.toml README.md .env /app/

EXPOSE 8501

CMD ["streamlit", "run", "/app/streamlit_app.py"]