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
- Uses [Poetry] for dependency management.
- Automated code formatting and linting with [pre-commit] and [ruff].
- Pagination support for listing comments.
- Fully type annotated code for better IDE support and code quality.

## Requirements

Manual installation:

- Python 3.10 or higher.
- [Poetry] for dependency management.
- Up and running [PostgreSQL] instance (locally or remotely).

Using Docker:

- [Docker]
- [Docker-Compose]
