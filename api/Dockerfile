FROM oven/bun:latest AS frontend-build

WORKDIR /app
COPY ui ./ui
WORKDIR /app/ui
RUN bun install
RUN bun run build

FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

# Install runtime libraries for OpenCV and MuJoCo (OSMesa)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libosmesa6-dev \
    && rm -rf /var/lib/apt/lists/*

ENV UV_PROJECT_ENVIRONMENT=/app/.venv

COPY api/pyproject.toml api/uv.lock api/README.md ./

RUN uv sync --locked --no-dev

COPY api/ /app/

COPY --from=frontend-build /app/ui/dist /static/ui

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
