"""
애플리케이션 설정 관리.

.env 로드는 pydantic_settings.BaseSettings가 수행합니다.
python-dotenv는 별도 로드가 필요할 때만 사용하면 됩니다.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 애플리케이션 기본 설정
    APP_NAME: str = "장부의 무게 API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # WebSocket 설정
    WS_MAX_CONNECTIONS: int = 100
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # 게임 설정
    MAX_PLAYERS: int = 7
    MIN_PLAYERS: int = 4
    
    # CORS 설정
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()

