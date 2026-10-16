#!/usr/bin/env bash
# Deploy the latest code on the production box: run from the repo, as the gunicorn service user.
# For a local dry run without a systemd unit: RESTART_CMD=true ./deploy.sh
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"  # uv's default install location, for non-login shells (ssh, cron)
cd "$(dirname "$0")"
git pull --ff-only
uv sync --frozen --no-dev
uv run --no-sync python manage.py migrate --noinput
uv run --no-sync python manage.py collectstatic --noinput
${RESTART_CMD:-sudo systemctl restart gunicorn}
