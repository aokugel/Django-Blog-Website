# syntax=docker/dockerfile:1
# Production-ready image (not used in production yet; see README). All config comes from
# env vars at runtime. Migrations are a one-off command, never run on container start:
#   docker run --rm --env-file <file> <image> python manage.py migrate
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /bin/
# The venv lives outside /code so docker-compose's dev bind mount (.:/code) can't hide it.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/venv PATH="/venv/bin:$PATH" WEB_CONCURRENCY=3
WORKDIR /code
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev
COPY . .
RUN SECRET_KEY=collectstatic-only python manage.py collectstatic --noinput
RUN useradd --system app
USER app
EXPOSE 8000
# --no-control-socket: gunicorn 25.1+ otherwise opens an admin socket in $HOME, which we don't use
CMD ["gunicorn", "mysite.wsgi", "--bind", "0.0.0.0:8000", "--no-control-socket"]
