#!/usr/bin/env just --justfile


run:
  uvicorn src.app:app --reload

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

cache-database:
  docker run \
    --name redis-dev \
    --rm \
    --detach \
    -p 6379:6379 \
    redis

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

ltree:
  docker exec -it testdatabase psql -U postgres -c "create extension if not exists ltree;"

test:
  pytest --no-header tests -v --disable-warnings

test-with-cov:
  pytest --durations=10 --no-header --cov=src --cov-report=html --cov-report=term-missing tests -v --disable-warnings
