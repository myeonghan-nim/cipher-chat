import os

import redis.asyncio as redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB")),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
    ssl=True,
    ssl_certfile="/etc/ssl/certs/redis.crt",
    ssl_keyfile="/etc/ssl/private/redis.key",
    ssl_ca_certs="/etc/ssl/certs/ca.crt",
    # hostname 검증 옵션
    ssl_check_hostname=False,
)
