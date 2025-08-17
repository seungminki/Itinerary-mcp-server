FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /workspace

COPY . .

RUN uv sync

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python3"]