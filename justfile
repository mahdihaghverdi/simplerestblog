#!/usr/bin/env just --justfile

run:
  database_url='' api_version='v1' uvicorn src.web.app:app --reload
