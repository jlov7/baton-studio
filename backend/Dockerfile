FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock alembic.ini ./
COPY migrations ./migrations
COPY baton_substrate ./baton_substrate
RUN uv sync --frozen --no-dev

EXPOSE 8787

CMD ["uv", "run", "uvicorn", "baton_substrate.api.main:app", "--host", "0.0.0.0", "--port", "8787"]
