<div align="center">
<h1><a href="https://github.com/mahdihaghverdi/simplerestblog"><b>SimpleRESTBlog</b></a></h1>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white" alt="Python">
</a>
<a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
</a>
</div>

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
    - [1. Clone the repository](#1-clone-the-repository)
    - [2. Install dependencies](#2-install-dependencies)
    - [3. Configure environment variables](#3-configure-environment-variables)
        - [FastAPI Application](#fastapi-application)
        - [MongoDB](#mongodb)
        - [Authentication](#authentication)
    - [4. Run the application](#4-run-the-application)
        - [Using Docker (Recommended)](#using-docker-recommended)
        - [Manually](#manually)
- [Documentation and Usage](#documentation-and-usage)
- [Project Structure, Modifications and Best Practices](#project-structure-modifications-and-best-practices)
    - [Creating new API routes](#creating-new-api-routes)
    - [FastAPI Best Practices](#fastapi-best-practices)
- [Stack](#stack)
- [License](#license)

## Introduction

_SimpleRESTBlog_ is a fast, fully async and reliable blog system RESTful API built with Python and [FastAPI] framework.
It uses the open source [PostgreSQL] database for storage.

## Features

- Fully async and non-blocking.
- Uses [FastAPI] framework for API development
- Uses [PostgreSQL] as data store for users, drafts, posts and comments.
- Extensible architecture for adding new API endpoints and services.
- Descriptive and well-documented code.
- OAuth2 (with hashed passwords and JWT tokens) based user authentication.
- TOTP for two-factor authentication using authenticator apps like Google Authenticator.
- Uses [Poetry] for dependency management.
- Automated code formatting and linting with [pre-commit] and [ruff].
- Pagination support for listing comments.
- Fully type annotated code for better IDE support and code quality.

## Requirements

Manual installation:

- Python 3.10 or higher.
- [Poetry] for dependency management.
- Up and running [PostgreSQL] instance.
- Up and running [Redis] instance.

Using Docker:

- [Docker]
- [Docker-Compose]

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mahdihaghverdi/simplerestblog.git
```

### 2. Install dependencies

⚠️ **Skip this step if you want to use docker for running the application.**

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
