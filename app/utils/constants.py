"""
게임 상수 정의
"""

from enum import Enum
from typing import Dict, List

# ==================== 역할 (Role) ====================
class Role(str, Enum):
    """플레이어 역할"""
    SHERIFF = "상단주"  # Sheriff
    DEPUTY = "원로원"  # Deputy
    OUTLAW = "적도 세력"  # Outlaw
    RENEGADE = "야망가"  # Renegade


# ==================== 카드 무늬 (Suit) ====================
class Suit(str, Enum):
    """카드 무늬"""
    SPADES = "검"  # ♠
    CLUBS = "책"  # ♣
    HEARTS = "치유"  # ♥
    DIAMONDS = "돈"  # ♦


# ==================== 카드 숫자 (Rank) ====================
class Rank(str, Enum):
    """카드 숫자"""
    ACE = "상"  # A
    KING = "대"  # K
    QUEEN = "중"  # Q
    JACK = "소"  # J


# ==================== 카드 타입 ====================
class CardType(str, Enum):
    """카드 타입"""
    # 공격 카드
    BANG = "정산"  # Bang!
    MISSED = "회피"  # Missed!
    GATLING = "전원 견제"  # Gatling
    INDIANS = "패거리 습격"  # Indians
    DUEL = "승부"  # Duel
    
    # 회복 카드
    BEER = "비상금"  # Beer
    
    # 무기 카드
    VOLCANIC = "연속 상환 요구"  # Volcanic
    WINCHESTER = "독점 상권 선언"  # Winchester
    
    # 장착 카드
    SCOPE = "첩보원"  # Scope
    BARREL = "신의 한 수"  # Barrel
    MUSTANG = "세력권 경계"  # Mustang
    JAIL = "영업 금지"  # Jail
    
    # 특수 카드
    PANIC = "강제 압류"  # Panic!
    SALOON = "공개 연회"  # Saloon
    GENERAL_STORE = "자선 경매"  # General Store


# ==================== 게임 상태 ====================
class GameState(str, Enum):
    """게임 상태"""
    WAITING = "대기 중"  # 플레이어 대기
    STARTING = "시작 중"  # 게임 시작 준비
    IN_PROGRESS = "진행 중"  # 게임 진행 중
    FINISHED = "종료"  # 게임 종료


class TurnState(str, Enum):
    """턴 상태"""
    DRAW = "드로우"  # 카드 뽑기 단계
    PLAY_CARD = "카드 사용"  # 카드 사용 단계
    RESPOND = "대응"  # 공격 대응 단계
    END_TURN = "턴 종료"  # 턴 종료


# ==================== 액션 타입 ====================
class ActionType(str, Enum):
    """플레이어 액션 타입"""
    USE_CARD = "USE_CARD"  # 카드 사용
    RESPOND_ATTACK = "RESPOND_ATTACK"  # 공격 대응
    END_TURN = "END_TURN"  # 턴 종료
    DRAW_CARD = "DRAW_CARD"  # 카드 뽑기
    USE_TREASURE = "USE_TREASURE"  # 보물 사용 (능동형)
    SELECT_STEAL_CARD = "SELECT_STEAL_CARD"  # 천청 방울: 강탈 카드 선택
    SELECT_DRAW_ORDER = "SELECT_DRAW_ORDER"  # 우선 전표: 드로우/위/아래 배치 선택
    GENERAL_STORE_PICK = "GENERAL_STORE_PICK"  # 자선 경매: 공개 카드 중 1장 선택


# ==================== 보물 (Treasure) ====================
# 보물 이름 상수 (보물 명칭 -> 원작 캐릭터)
TREASURE_NAMES = {
    "만능 통보": "Lucky Duke",  # 판정 시 카드 2장 중 유리한 쪽 선택
    "천청 방울": "Jesse James",  # 강탈(뽑기) 강화
    "만국 지도": "Rose Doolan",  # 모든 상대와의 거리 -1
    "안개 병풍": "Paul Regret",  # 다른 플레이어가 나를 볼 때 거리 +1
    "비단 갑옷": "Jourdonnais",  # 판정 문양 '검'이면 자동 회피 + 드로우
    "응징의 패": "El Gringo",  # 피해를 입혔을 때 역강탈
    "화수분": "Suzy Lafayette",  # 손패 0장이 되는 즉시 2장 드로우
    "반전 금화": "Calamity Janet",  # 정산 ↔ 회피 교차 사용
    "이중 장부": "Bart Cassidy",  # 재력 손실 시 드로우 (턴당 2회 제한)
    "우선 전표": "Kit Carlson",  # 덱 상단 3장 조작
    "유산 상자": "Vulture Sam",  # 탈락자 카드/보물 획득
    "기록 파편": "Pedro Ramirez",  # 버림 더미 상단이 '돈'이면 턴 시작 시 회수
    "낙인 인장": "Slab the Killer",  # 내 정산 방어에 회피 2장 필요 (조건부)
    "황금 연갑": "Willy the Kid",  # 턴당 정산 무제한 (추가 코스트)
    "생명 장부": "Sid Ketchum",  # 서로 다른 문양 2장 버리고 재력 1 회복
    "황금 주판": "Black Jack",  # 두 번째 드로우 카드가 '돈'이면 1장 추가 드로우
}

# ==================== 게임 규칙 상수 ====================
INITIAL_HP = {
    Role.SHERIFF: 5,  # 상단주: 재력 5
    Role.DEPUTY: 4,  # 원로원: 재력 4
    Role.OUTLAW: 3,  # 적도 세력: 재력 3
    Role.RENEGADE: 4,  # 야망가: 재력 4
}

DEFAULT_RANGE = 1  # 기본 영향력 (사거리)

# ==================== 게임 설정 ====================
# 플레이어 수 제한
MIN_PLAYERS: int = 4
MAX_PLAYERS: int = 7

# WebSocket 설정
WS_MAX_CONNECTIONS: int = 100
WS_HEARTBEAT_INTERVAL: int = 30

# ==================== 카드 덱 구성 ====================
# BANG! 게임 규칙 기반 카드 덱 구성
CARD_DECK_CONFIG: Dict[CardType, int] = {
    # 공격 카드
    CardType.BANG: 25,  # 정산
    CardType.MISSED: 12,  # 회피
    CardType.GATLING: 1,  # 전원 견제
    CardType.INDIANS: 2,  # 패거리 습격
    CardType.DUEL: 3,  # 승부
    
    # 회복 카드
    CardType.BEER: 6,  # 비상금
    
    # 무기 카드
    CardType.VOLCANIC: 2,  # 연속 상환 요구 (영향력 1)
    CardType.WINCHESTER: 1,  # 독점 상권 선언 (영향력 5)
    
    # 장착 카드
    CardType.SCOPE: 1,  # 첩보원 (영향력 +1)
    CardType.BARREL: 1,  # 신의 한 수
    CardType.MUSTANG: 1,  # 세력권 경계
    CardType.JAIL: 3,  # 영업 금지
    
    # 특수 카드
    CardType.PANIC: 4,  # 강제 압류
    CardType.SALOON: 1,  # 공개 연회
    CardType.GENERAL_STORE: 1,  # 자선 경매
}

# 카드별 상세 정보 (이름, 설명, 영향력 등)
CARD_DETAILS: Dict[CardType, Dict[str, any]] = {
    CardType.BANG: {
        "name": "정산",
        "description": "기본 공격 카드. 대상에게 재력 1 피해를 입힙니다.",
        "range": 1,
    },
    CardType.MISSED: {
        "name": "회피",
        "description": "공격을 회피합니다.",
        "range": 1,
    },
    CardType.GATLING: {
        "name": "전원 견제",
        "description": "모든 플레이어에게 공격합니다. 회피 카드로 방어 가능.",
        "range": 0,  # 모든 플레이어 대상
    },
    CardType.INDIANS: {
        "name": "패거리 습격",
        "description": "모든 플레이어에게 공격합니다. 정산 카드로 방어 가능.",
        "range": 0,
    },
    CardType.DUEL: {
        "name": "승부",
        "description": "1대1 카드 결투를 시작합니다.",
        "range": 1,
    },
    CardType.BEER: {
        "name": "비상금",
        "description": "재력을 1 회복합니다.",
        "range": 0,
    },
    CardType.VOLCANIC: {
        "name": "연속 상환 요구",
        "description": "영향력 1. 정산 카드를 무제한으로 사용할 수 있습니다.",
        "range": 1,
    },
    CardType.WINCHESTER: {
        "name": "독점 상권 선언",
        "description": "영향력 5. 최대 사거리 무기입니다.",
        "range": 5,
    },
    CardType.SCOPE: {
        "name": "첩보원",
        "description": "영향력 +1 증가합니다.",
        "range": 0,
    },
    CardType.BARREL: {
        "name": "신의 한 수",
        "description": "공격 시 카드를 뽑아 방어할 수 있습니다.",
        "range": 0,
    },
    CardType.MUSTANG: {
        "name": "세력권 경계",
        "description": "상대의 공격 영향력 +1 요구합니다.",
        "range": 0,
    },
    CardType.JAIL: {
        "name": "영업 금지",
        "description": "대상의 다음 턴을 제한합니다.",
        "range": 1,
    },
    CardType.PANIC: {
        "name": "강제 압류",
        "description": "사거리 1 내의 플레이어 카드 1장을 강탈합니다.",
        "range": 1,
    },
    CardType.SALOON: {
        "name": "공개 연회",
        "description": "모든 플레이어의 재력을 1 회복합니다.",
        "range": 0,
    },
    CardType.GENERAL_STORE: {
        "name": "자선 경매",
        "description": "모든 플레이어가 카드를 1장씩 순서대로 획득합니다.",
        "range": 0,
    },
}

