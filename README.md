<div align="center">
<h1><a href="https://github.com/mahdihaghverdi/simplerestblog"><b>SimpleRESTBlog</b></a></h1>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
</a>
<a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white">
</a>
<a href="https://www.postgresql.org">
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white">
</a>
<a href="https://www.sqlalchemy.org/">
    <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white">
</a>
<a href="https://www.redis.io">
    <img src="https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white">
</a>
<a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/badge/ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black">
</a>
<a href="https://support.google.com/accounts/answer/1066447?hl=en&co=GENIE.Platform%3DAndroid">
    <img src="https://img.shields.io/badge/Google Authenticator-4285F4?style=for-the-badge&logo=googleauthenticator&logoColor=white">
</a>
</div>

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Project Structure, Implementation details and Best Practices](#project-structure-implementation-details-and-best-practices)
  - [Structure](#structure)
  - [Implementation details](#implementation-details)
    - [Database Design](#database-design)
    - [Data Layer](#data-layer)
    - [Authentication](#authentication)
    - [Authorization](#authorization)
    - [Architecture](#architecture)
- [Requirements](#requirements)
- [Setup](#setup)
    - [1. Clone the repository](#1-clone-the-repository)
    - [2. Install dependencies](#2-install-dependencies)
    - [3. Configure environment variables](#3-configure-environment-variables)
        - [FastAPI Application](#fastapi-application)
        - [PostgreSQL](#postgresql)
        - [Redis](#redis)
        - [Authentication](#authentication-1)
    - [4. Run the application](#4-run-the-application)
        - [Manually](#manually)
- [Documentation and Usage](#documentation-and-usage)
- [Stack](#stack)
- [License](#license)

## Introduction

_SimpleRESTBlog_ is a fast, fully async and reliable blog system RESTful API built with Python and [FastAPI] framework.
It uses the open source [PostgreSQL] database for storage.

## Features

- Fully async and non-blocking.
- Uses [FastAPI] framework for API development
- Uses [PostgreSQL] as data store for users, drafts, posts and comments.
- Fully layered and decoupled code.
- Extensible architecture for adding new API endpoints and services.
- Descriptive and well-documented code.
- OAuth2 (with hashed passwords and JWT tokens) based user authentication.
- TOTP for two-factor authentication using authenticator apps like Google Authenticator.
- Uses [Poetry] for dependency management.
- Automated code formatting and linting with [pre-commit] and [ruff].
- Pagination support for listing comments.
- Fully type annotated code for better IDE support and code quality.

## Project Structure, Implementation details and Best Practices

### Structure
Structure of `simplerestblog` package containing main files and folders of the application is consistent and straightforward
and just by looking at module names it gives you an idea of what's inside it!

```
simplerestblog
├── alembic                 # Migration utility
├── src                     # Primary app
│   ├── core                # config, ACL, DB, depends, schemas, security, ...
│   ├── repository          # Data layer: Repository and ORM stuff
│   ├── service             # Service layer: the business logic
│   ├── web                 # API layer: routes
│   ├── app.py              # Main FastAPI app
│   ├── __init__.py
│   └── __main__.py         # Runs the uvicorn server
├── tests                   # App tests
├── alembic.ini             # Migration settings
└── pyproject.toml
```

### Implementation details
#### Database Design
At the core of many businesses, a good database design helps the reliability and data normalization
and avoid wasting disk usage.

The database design and considerations of _SRB_ is discussed below.

Tables:
```
users
+------------------+----------+------+---------+-----------+------+-----+----+
| username: UNIQUE | password | role | created | totp_hash | name | ... | id | <------------+
+------------------+----------+------+---------+-----------+------+-----+----+              |
                                                                          ^^                |
                                                                          ||-----------+    |
                                                                          |            |    |
drafts                                                                    |            |    |
+----+-------+------+---------+------------+--------------+---------+--------------+   |    |
| id | title | body | updated | draft_hash | is_published | created | username: FK |   |    |
+----+-------+------+---------+------------+--------------+---------+--------------+   |    |
  ^                                                                                    |    |
  |----------------------------+              +----------------------------------------+    |
                               |              |                                             |
posts                          |              |                                             |
+------+---------------+--------------+--------------+----+                                 |
| slug | published: DT | draft_id: FK | username: FK | id |                                 |
+------+---------------+--------------+--------------+----+                                 |
                                                       ^^                                   |
                         +-----------------------------||                                   |
                         |                              |----+                              |
association_table        |                                   |                              |
+----+------------+-------------+                            |                              |
| id | tag_id: FK | post_id: FK |                            |                              |
+----+------------+-------------+                            |                              |
                |                                            |                              |
                |                                            |                              |
tags            |                                            |                              |
+----+-----+    |                                            |                              |
| id | tag | <--+                                            |                              |
+----+-----+                                                 |                              |
                                                             |                              |
comments                                                     |                              |
+----+---------+-------------+---------------+---------+-------------+---------------+--------------+
| id | comment | path: LTree | commented: DT | updated | post_id: FK | parent_id: FK | username: FK |
+----+---------+-------------+---------------+---------+-------------+---------------+--------------+
  ^                                                                         |
  |-------------------------------------------------------------------------+
```

As you can see, data is normalized.
Some design considerations of the database design:
1. Each post's details are stored in the `drafts` table. This is good because if someone wants to _unpublish_ and edit
 the post, the `is_published` columns of the `drafts` table will be `false` and there is no need to delete post details and reinsert them into database (if they were stored in `posts` table _separately_)
2. Retrieving the comments is done by using the [PostgreSQL] feature [LTree] (which is a very fast, builtin type for hierarchical tree-like data)

#### Data Layer
The data layer of the application has repositories for different database tables.

- In each method of the repositories queries are generated using [SQLAlchemy] query builder functions and methods,
to have full control over the generated query and more important database hits.

#### Authentication
- _SRB_ uses _access_ and _refresh_ `JWT` tokens to implement authentication.

  Signing up is a simple `username`, `password` flow.
- 2FA:

  _SRB_ has builtin support for _TOTP_ two-factor authentication using qr-code and authenticator apps like: [Google Authenticator]

#### Authorization
Most routes of _SRB_ are protected (i.e. you have to be logged in and provide your access token)
However _SRB_ implements different layer of permissions for routes which in short is the _ACL_.
_SRB_ handle the ACL and route access permission with JWT tokens.

For example if I am the superuser or admin of _SRB_ I can delete any user comments with the route that user uses to remove his/her comment. Also, if a users attempts to delete some other user's comment, it is now allowed.

#### Architecture
_SRB_ is designed as a layered system. There are three layers: Data layer, Service layer and API layer which are fully decoupled.
 and upper layers are not aware of the details in the lower layers which is achieved with dependency injection.

## Requirements

Manual installation:

- Python 3.10 or higher.
- [Poetry] for dependency management.
- Up and running [PostgreSQL] instance.
- Up and running [Redis] instance.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mahdihaghverdi/simplerestblog.git
```

### 2. Install dependencies

You need to configure [Poetry] to place the virtual environment in the project directory. To do so, run the following
command:

```bash
poetry config --local virtualenvs.in-project true
```

Then, install dependencies:

```bash
poetry install
```

### 3. Configure environment variables

You can see the table of all environment variables below. Those marked with `*` are required and **MUST** be set before
running the application. Rest of them are optional and have default values.

**Note:** To set any of these environment variables below, you **MUST** prefix them with `SRB_` and then set them
in your shell or in a `.env` file placed at the root directory.
For example, to set `DEBUG` environment variable, you can do the following:

```bash
export SRB_DEBUG=True
```

Also note that **ALL** environment variables are **CASE SENSITIVE**.

#### FastAPI Application

| Name          | Description                       | Default |        Type        |
|---------------|:----------------------------------|:-------:|:------------------:|
| `API_VERSION` | API version 1 prefix              |  `v1`   |      `string`      |
| `DEBUG`       | Debug mode for development        | `False` |     `boolean`      |


#### PostgreSQL

| Name     | Description             |                        Default                        |   Type   |
|----------|:------------------------|:-----------------------------------------------------:|:--------:|
| `PG_DB`  | Postgres database name  |                     `fastblog_db`                     | `string` |
| `PG_URL` | Postgres connection URL | `postgresql+asyncpg://postgres:postgres@0.0.0.0:5432` | `string` |


#### Redis

| Name              | Description                   |         Default         |   Type   |
|-------------------|:------------------------------|:-----------------------:|:--------:|
| `REDIS_CACHE_URL` | Redis instance connection URL | `redis://@0.0.0.0:6379` | `string` |


#### Authentication

| Name                           | Description                              |                              Default                              |   Type    |
|--------------------------------|:-----------------------------------------|:-----------------------------------------------------------------:|:---------:|
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | Access token expiration time in minutes  |                          `120` (2 hours)                          | `integer` |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token expiration time in minutes |                          `2880` (2 days)                          | `integer` |
| `SECRET_KEY`*                  | Secret key for signing JWT tokens        | 64 random characters generated by `openssl rand -hex 64` command. | `string`  |
| `TFA_EXPIRE_MINUTES`           | TOTP expiration time                     |                               `15`                                | `string`  |


### 4. Run the application

After setting all the required and optional environment variables in `.env.example` file, copy it to `.env` file so that
it's usable both by Docker and _Shortify_ app.

Run the following commands to start up the services:

#### Manually

An up & running [PostgreSQL] and [Redis] instance are required.

```bash
python -m src
```

If the `SHORTIFY_DEBUG` environment variable is set to `True`, the application will be run in debug mode and will be
reloaded automatically on code changes.

Now your application is available at `http://localhost:8000/`.

## Documentation and Usage

After running the application, you can access the OpenAPI (Swagger) documentation at `/api/v1/docs` endpoint.

## Stack

Frameworks and technologies used in _Shortify_

- [FastAPI] (Web framework)
- [PostgreSQL] (Database)
- [Redis] (In-memory DB for 2FA)
- [SQLAlchemy] (ORM)
- [poetry] (Dependency Management)
- [pre-commit] (Git hook)
- [ruff] (Linter & Formatter)
-
## License

This project is licensed under the terms of the [GPL-3.0] license.

<p align="center">&mdash; ⚡ &mdash;</p>

[FastAPI]: https://github.com/tiangolo/fastapi "Modern, high-performance, web framework for building APIs with Python."
[PostgreSQL]: https://www.postgresql.org/ "The world's most advanced open source database."
[Poetry]: https://python-poetry.org/ "Python dependency management and packaging made easy."
[pre-commit]: https://pre-commit.com/ "A framework for managing and maintaining multi-language pre-commit hooks."
[black]: https://github.com/psf/black "The uncompromising Python code formatter."
[GPL-3.0]: https://www.gnu.org/licenses/gpl-3.0.en.html "GNU General Public License v3.0"
[structlog]: https://www.structlog.org/en/stable/ "Structured logging for Python."
[logging]: https://docs.python.org/3/library/logging.html "Logging facility for Python."
[secrets]: https://docs.python.org/3/library/secrets.html "Generate secure random numbers for managing secrets."
[uvicorn]: https://www.uvicorn.org/ "The lightning-fast ASGI server."
[gunicorn]: https://gunicorn.org/ "A Python WSGI HTTP Server for UNIX."
[VSCode]: https://code.visualstudio.com/ "Redefined and optimized code editor for building and debugging modern web and cloud applications."
[fastapi-best-practices]: https://github.com/zhanymkanov/fastapi-best-practices "Opinionated list of best practices and conventions."
[full-stack-fastapi-postgresql]: https://github.com/tiangolo/full-stack-fastapi-postgresql "Full stack, modern web application generator. Using FastAPI, PostgreSQL as database, Docker, automatic HTTPS and more."
[pydantic]: https://github.com/pydantic/pydantic "Data parsing and validation using Python type hints."
[beanie]: <https://github.com/roman-right/beanie> "Python ODM for MongoDB."
[isort]: <https://github.com/PyCQA/isort> "A Python utility / library to sort imports."
[mypy]: https://github.com/python/mypy "Optional static typing for Python."
[ruff]: https://github.com/charliermarsh/ruff "An extremely fast Python linter, written in Rust."
[Docker]: https://github.com/docker/
[Docker-Compose]: https://github.com/docker/compose "Define and run multi-container applications with Docker."
[LTree]: https://www.postgresql.org/docs/current/ltree.html ""
[SQLAlchemy]: https://www.sqlalchemy.org/ "he Python SQL Toolkit and Object Relational Mapper"
[Google Authenticator]: https://support.google.com/accounts/answer/1066447?hl=en&co=GENIE.Platform%3DAndroid "Google authenticator"
