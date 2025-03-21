#!/bin/sh

envsubst '${FASTAPI_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

nginx -g "daemon off;"
