#!/bin/sh

envsubst '${REDIS_PORT} ${REDIS_PASSWORD}' < /opt/bitnami/redis/etc/redis.conf.template > /opt/bitnami/redis/etc/redis.conf

redis-server /opt/bitnami/redis/etc/redis.conf
