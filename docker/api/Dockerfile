
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

COPY ./server /app

WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "fastapi", "run", "main.py"]
