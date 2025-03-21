#!/bin/sh

uvicorn app.main:app --host $FASTAPI_HOST --port $FASTAPI_PORT
