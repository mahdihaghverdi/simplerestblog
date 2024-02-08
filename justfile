#!/usr/bin/env just --justfile


run:
  database_url='postgresql+asyncpg://postgres:postgres@0.0.0.0:5432' \
  api_version='v1' \
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
