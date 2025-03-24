import os

# 모듈 import 전에 환경 변수 설정
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_DB", "0")

import pytest
import fakeredis.aioredis

import app.endpoints.session as session_module


@pytest.fixture(autouse=True)
def override_redis_client(monkeypatch):
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(session_module, "redis_client", fake_redis)
