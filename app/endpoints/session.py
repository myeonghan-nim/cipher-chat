import uuid

from fastapi import APIRouter, HTTPException
from redis.exceptions import RedisError

from app.core.redis import redis_client
from app.core.logging import logger

router = APIRouter()

SESSION_EXPIRATION_SECONDS = 3600


@router.post("/create", summary="채팅 세션 생성", status_code=201)
async def create_session():
    try:
        # 새로운 UUID 생성
        session_id = str(uuid.uuid4())
        # Redis에 세션 상태 저장 (예: "active") 및 만료 시간 설정
        await redis_client.set(session_id, "active", ex=SESSION_EXPIRATION_SECONDS)
    except RedisError as e:
        # Redis 연결 문제나 명령 실행 중 에러가 발생한 경우 500 에러 반환
        logger.error(f"Redis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Redis is not normal")
    except Exception as e:
        # 그 외의 예외 처리
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error")
    return {"session_id": session_id}


@router.post("/close", summary="채팅 세션 종료", status_code=200)
async def close_session(session_id: str):
    try:
        # Redis에서 세션 존재 여부 확인
        exists = await redis_client.exists(session_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Session not found")
        # 세션 삭제
        await redis_client.delete(session_id)
    except RedisError as e:
        # Redis 관련 에러 발생 시 500 에러 반환
        logger.error(f"Redis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Redis is not normal")
    except HTTPException as e:
        # HTTPException 발생 시 해당 에러 반환
        logger.error(f"HTTPException: {str(e)}")
        raise e
    except Exception as e:
        # 그 외의 예외 처리
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error")
    return {"message": f"Session {session_id} closed"}
