# Polympics Server

## Setup

This project requires Python3.9+ (Python 4 is not acceptable). Depending on your operating system, you may be able to install it from your package manager, an external PPA (like deadsnakes), or [the official website](https://python.org/download).

This project uses `pipenv` to manage dependencies. To get started, you'll need to install `pipenv` from PyPI, eg:
```bash
$ python3 -m pip install pipenv
```

Once you have `pipenv` installed, you can create a virtual enviroment and install the project's dependencies with
```bash
$ pipenv shell
$ pipenv install
```
To additionally install development dependencies, do
```bash
$ pipenv install -d
```
You can then run a development server (**not appropriate for production**) with
```bash
$ uvicorn polympics_server:application
```
You can set the host and port to bind on with `--port` and `--host`.

TODO: Add set up instructions for production with `gunicorn` and `apache` or `nginx`.

## Configuration

Configuration goes in the same dir as this README, in a file named `config.json`. The available options are as follows:

| Field             | Default       | Description                                  |
|:------------------|:--------------|:---------------------------------------------|
| `debug`           | `false`       | Whether to run FastAPI in debug mode.        |
| `max_session_age` | `"30d"`       | How long user auth sessions last.            |
| `db_name`         | `"polympics"` | The PostgreSQL database to connect to.       |
| `db_user`         | `"polympics"` | The user to use to connect to the database.  |
| `db_host`         | `"127.0.0.1"` | The host of the database to connect to.      |
| `db_port`         | `5432`        | The port to connect to on the database host. |
| `db_password`     | Required      | The password for the database.               |
| `db_log_level`    | `"INFO"`      | The level of logs for Peewee to output.      |
| `discord_api_url` | ``https://discord.com/api/v8`` | The URL of the Discord API. |
| `discord_cdn_url` | ``https://cdn.discordapp.com`` | The URL of the Discord CDN. |

## CLI

You can access the server management CLI from the command line by running (with pipenv enabled):
```bash
$ python -m polympics_server
```
The following subcommands are available

- `apps`
  - `create`
  - `edit`
  - `delete`
  - `list`
  - `view`
- `sessions`
  - `prune`
- `migrations`
  - `apply`
  - `list`

Use `--help` on any command for more information about what it does and how to use it, for example:
```bash
$ python -m polympics_server apps edit --help
```

## API

To see automatically generated docs, run the server as described above and visit http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc.

TODO: Better docs, document pagination and authentication.
