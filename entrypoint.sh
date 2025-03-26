#!/bin/sh

uvicorn app.main:app \
        --host $FASTAPI_HOST \
        --port $FASTAPI_PORT \
        --ssl-certfile /etc/ssl/certs/fastapi.crt \
        --ssl-keyfile /etc/ssl/private/fastapi.key
