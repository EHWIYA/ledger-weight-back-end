# Pydantic 개념 (초보자용)

Pydantic은 **데이터 검증·설정** 라이브러리입니다. 이 프로젝트에서 모델과 설정에 사용됩니다.

---

## 1. 모델 클래스

### 이게 뭔가요?
**필드 타입과 기본값**을 정의하는 클래스입니다. 들어오는 데이터가 타입에 맞는지 자동 검증하고, JSON 등으로 직렬화할 수 있습니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `app/models/game.py` — Game
- `app/models/player.py` — Player
- `app/models/card.py` — Card
- `app/models/role.py` — Role

### 예시
```python
from pydantic import BaseModel

class Player(BaseModel):
    id: str
    name: str
    hp: int = 4
    max_hp: int = 4
```

---

## 2. BaseSettings (설정)

### 이게 뭔가요?
**환경 변수**와 `.env` 파일을 읽어 Pydantic 모델로 로드하는 기능입니다.

### 이 프로젝트에서 어떻게 쓰나요?
- `app/config.py`: `Settings(BaseSettings)` — HOST, PORT, CORS_ORIGINS, WS_MAX_CONNECTIONS 등

### 예시
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8088
    env_file = ".env"

settings = Settings()
```

---

## 3. Enum과 함께 사용

### 주의사항
`use_enum_values = True`를 쓰면 Enum이 **자동으로 값(str)**으로 변환됩니다. 이 경우 `role.value`처럼 접근하면 에러가 납니다. 이 프로젝트에서는 `Role`, `GameState` 등을 Enum으로 정의하고, 모델에서 사용할 때 이 점을 고려합니다.
