#!/usr/bin/env just --justfile


run:
  uvicorn src.web.app:app --reload

database:
  docker run \
    --name psql-dev \
    --rm \
    --detach \
    --env POSTGRES_USER=postgres \
    --env POSTGRES_PASSWORD=postgres \
    --env POSTGRES_DB=fastblog_db \
    -p 5432:5432 \
    -v fastblog-data:/var/lib/postgresql/data \
     postgres

test-database:
  docker run \
    --name testdatabase \
    --rm \
    --detach \
    --tmpfs=/data \
    --env POSTGRES_USER=postgres \
    --env POSTGRES_PASSWORD=postgres \
    --env POSTGRES_DB=fastblog_db \
    --env PGDATA=/data \
    -p 5433:5432 \
     postgres

test:
  pytest --no-header tests -v

test-with-cov:
  pytest --no-header --cov=src --cov-report=html --cov-report=term-missing tests -vv
