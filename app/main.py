"""
FastAPI 애플리케이션 진입점
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.game.game_manager import GameManager
from app.websocket.connection_manager import ConnectionManager
from app.websocket.message_handler import MessageHandler
from app.security.auth import get_player_id_from_token

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="장부의 무게 - WebSocket 기반 실시간 카드 게임 서버",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 인스턴스
game_manager = GameManager()
connection_manager = ConnectionManager()
message_handler = MessageHandler(game_manager, connection_manager)

# 프로젝트 문서 대시보드 (Astro 빌드 결과물 서빙)
docs_path = Path(__file__).parent.parent / "docs-app" / "dist"


@app.get("/docs-view/_astro/{file_path:path}")
async def serve_docs_astro_assets(file_path: str):
    """Astro 빌드 CSS/JS 등 _astro 하위 정적 파일 서빙 (StaticFiles 404 방지)"""
    full_path = docs_path / "_astro" / file_path
    if full_path.is_file():
        media_type = "text/css" if file_path.endswith(".css") else "application/javascript" if file_path.endswith(".js") else None
        return FileResponse(full_path, media_type=media_type)
    raise HTTPException(status_code=404, detail="Not found")


app.mount("/docs-view", StaticFiles(directory=str(docs_path), html=True), name="docs-view")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTPException을 JSON 응답으로 통일."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """미처리 예외를 500 응답으로 통일 (상세 노출 방지)."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "장부의 무게 API 서버",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


async def run_ws_message_loop(
    websocket: WebSocket,
    player_id: str,
    connection_manager: ConnectionManager,
    message_handler: MessageHandler,
) -> None:
    """WebSocket 메시지 수신 루프 (PING/PONG, handle_message, ERROR 응답)."""
    while True:
        try:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "PING":
                await connection_manager.send_personal_message(
                    {
                        "type": "PONG",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    player_id,
                )
                continue
            result = await message_handler.handle_message(player_id, message)
            if result.get("success") is not None:
                await connection_manager.send_personal_message(
                    {"type": "ACTION_RESPONSE", "data": result},
                    player_id,
                )
        except json.JSONDecodeError:
            await connection_manager.send_personal_message(
                {
                    "type": "ERROR",
                    "code": "INVALID_JSON",
                    "message": "잘못된 JSON 형식입니다.",
                },
                player_id,
            )
        except WebSocketDisconnect:
            break


@app.websocket("/lobby/{game_id}")
async def lobby_websocket_endpoint(
    websocket: WebSocket,
    game_id: str,
    player: str = Query(..., description="플레이어 이름"),
    token: Optional[str] = Query(
        default=None, description="인증 토큰 (선택, JWT 등)"
    ),
):
    """
    로비 WebSocket 엔드포인트
    
    플레이어 이름을 받아 서버에서 플레이어 ID를 자동 생성하고,
    연결과 동시에 게임에 자동 참가 처리합니다.
    
    Args:
        websocket: WebSocket 연결
        game_id: 게임 ID
        player: 플레이어 이름 (쿼리 파라미터)
    """
    # 토큰 기반 플레이어 ID 추출 (있다면 우선 사용)
    player_id_from_token = get_player_id_from_token(token)

    # 플레이어 ID 자동 생성 (UUID, 토큰이 없거나 유효하지 않은 경우)
    player_id = player_id_from_token or str(uuid.uuid4())
    
    # 연결 수락
    success = await connection_manager.connect(websocket, player_id)
    if not success:
        await websocket.close(code=1008, reason="최대 연결 수 초과")
        return
    
    try:
        # 연결 성공 메시지 전송 (플레이어 ID 포함)
        await connection_manager.send_personal_message(
            {
                "type": "CONNECTION_ESTABLISHED",
                "message": "로비에 연결되었습니다.",
                "player_id": player_id,
                "player_name": player,
                "game_id": game_id,
            },
            player_id,
        )
        
        # 자동 게임 참가 처리
        join_result = await message_handler.handle_join_game(
            player_id,
            {
                "type": "JOIN_GAME",
                "game_id": game_id,
                "player_name": player,
            }
        )
        
        # 참가 실패 시 에러 메시지 전송
        if not join_result.get("success"):
            await connection_manager.send_personal_message(
                {
                    "type": "ERROR",
                    "code": join_result.get("error_code", "JOIN_GAME_FAILED"),
                    "message": join_result.get("message", "게임 참가에 실패했습니다."),
                },
                player_id,
            )
            await websocket.close(code=1008, reason=join_result.get("message", "게임 참가 실패"))
            return
        
        # 메시지 수신 루프
        await run_ws_message_loop(
            websocket, player_id, connection_manager, message_handler
        )
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(player_id)


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    player_id: str,
    token: Optional[str] = Query(
        default=None, description="인증 토큰 (선택, JWT 등)"
    ),
):
    """
    WebSocket 엔드포인트 (기존 호환성 유지)
    
    Args:
        websocket: WebSocket 연결
        player_id: 플레이어 ID
    """
    # 토큰이 있는 경우, 토큰 기반 플레이어 ID와 경로 파라미터 일치 여부 확인
    auth_player_id = get_player_id_from_token(token)
    if auth_player_id is not None and auth_player_id != player_id:
        await websocket.close(
            code=1008,
            reason="인증 실패: 플레이어 ID가 토큰과 일치하지 않습니다.",
        )
        return

    # 경로 파라미터 대신 토큰에서 추출한 ID를 우선 사용
    if auth_player_id:
        player_id = auth_player_id

    # 연결 수락
    success = await connection_manager.connect(websocket, player_id)
    if not success:
        await websocket.close(code=1008, reason="최대 연결 수 초과")
        return
    
    try:
        # 연결 성공 메시지 전송
        await connection_manager.send_personal_message(
            {
                "type": "CONNECTION_ESTABLISHED",
                "message": "연결이 성공적으로 설정되었습니다.",
                "player_id": player_id,
            },
            player_id,
        )
        
        # 메시지 수신 루프
        await run_ws_message_loop(
            websocket, player_id, connection_manager, message_handler
        )
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(player_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

