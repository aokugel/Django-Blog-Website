# My Django Blog

### Overview

This is my django code repository for anthonykugel.com.  The website is written using the django web framework.  Frontend assets are written in html, css, and javascript.  The website itself is running on AWS.  The web server is running on nginx on an ec2 instance, the database is on Postgresql running on AWS RDS.  I registered the domain using aws route 53.

### Features

- Dynamic Post content
- Intricate Comment System
- A sleek and modern design
- REST Api integration

### Usage & Details
The website runs all on aws.  The web layer runs on nginx, which is running in an ec2 instance running ubuntu.  Nginx communiates with django via a unix socket running on gunicorn.
The database is running on postgresql running on aws rds.  This is a diagram of the architecture:
![Architecture diagram](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/images/con-VPC-sec-grp.png)

### Development
Dependencies are managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`); uv installs the pinned Python version from `.python-version` if needed.

```sh
export DEBUG=1                                   # local dev only; also supplies an insecure dev SECRET_KEY
docker-compose up -d db                          # local Postgres on localhost:5432
uv sync                                          # create .venv with locked dependencies
uv run python manage.py migrate
uv run python manage.py loaddata sample          # sample posts/comments; never run in production
uv run python manage.py runserver
uv run python manage.py test
```

Or run everything in Docker: `docker-compose up --build`. To add or upgrade a dependency, use `uv add <package>` or `uv lock --upgrade-package <package>`, and commit `uv.lock`.

### Deployment
Production deploys with `git pull` on the EC2 box: [deploy.sh](deploy.sh) pulls, runs `uv sync --frozen --no-dev`, migrates, collects static files, and restarts gunicorn. Run it from the repo as the gunicorn service user. The `Dockerfile` is production-ready but not yet used in production.

### Configuration
All settings come from environment variables, read from a `.env` file at the repo root if present. Copy [.env.example](.env.example) to `.env` and fill it in.

| Variable | Required in production | Default |
|---|---|---|
| `SECRET_KEY` | yes | none (an insecure dev key only when `DEBUG=1`) |
| `ALLOWED_HOSTS` | yes | `localhost,127.0.0.1` |
| `STATIC_ROOT` | yes (nginx's static dir) | `./staticfiles` |
| `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | yes | local docker-compose Postgres |
| `DEBUG` | no, leave unset | off |

`docker-compose.yml` is for local development only and sets `DEBUG=1` itself.

### ChangeLog & Roadmap
I might eventually incorporate a Dashboard using plotly.  This would be a good way to utilize python's data visualization capabilities.

### Credits
I would not have been able to make this website with the help of djangocentral.com.  Frontend css and javascript leveraged with https://getbootstrap.com/ and https://bootswatch.com/.
