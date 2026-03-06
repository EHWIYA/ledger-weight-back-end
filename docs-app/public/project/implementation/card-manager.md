# 카드 관리자 (CardManager) 구현 문서

## 개요
카드 덱 생성, 셔플, 드로우, 버리기 등의 카드 관리 로직을 담당하는 CardManager 클래스의 구현 문서입니다.

## 구현 내용

### 파일
- `app/game/card_manager.py` - CardManager 클래스
- `app/utils/constants.py` - 카드 덱 구성 및 상세 정보

## 의사결정 기록

### 1. 카드 덱 구성 방식
**선택한 방식**: 상수로 정의된 카드 타입별 개수 기반 생성

**이유**:
- 게임 규칙 변경 시 상수만 수정하면 됨
- 타입 안정성 보장
- 명확한 카드 구성 관리

**코드 예시**:
```python
# app/utils/constants.py
CARD_DECK_CONFIG: Dict[CardType, int] = {
    CardType.BANG: 25,  # 정산
    CardType.MISSED: 12,  # 회피
    CardType.BEER: 6,  # 비상금
    # ... 나머지 카드들
}
```

### 2. 카드 ID 생성 방식
**선택한 방식**: `{카드타입}_{순번}` 형식

**이유**:
- 고유성 보장
- 디버깅 용이
- 카드 타입 식별 용이

**코드 예시**:
```python
card_id = f"{card_type.value}_{card_counter:03d}"
# 예: "정산_001", "회피_012"
```

### 3. 무늬와 숫자 할당 방식
**선택한 방식**: 정산, 회피, 비상금 카드에만 무늬와 숫자 할당

**이유**:
- 원작 BANG! 게임 규칙 준수
- 특수 카드는 무늬/숫자 불필요
- 순환 방식으로 균등 분배

**코드 예시**:
```python
if card_type in [CardType.BANG, CardType.MISSED, CardType.BEER]:
    suits = [Suit.SPADES, Suit.CLUBS, Suit.HEARTS, Suit.DIAMONDS]
    ranks = [Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK]
    
    suit_index = (card_counter // len(ranks)) % len(suits)
    rank_index = card_counter % len(ranks)
    
    suit = suits[suit_index]
    rank = ranks[rank_index]
```

### 4. 덱 재생성 로직
**선택한 방식**: 버림 더미를 덱으로 재생성 (맨 위 카드 제외)

**이유**:
- BANG! 게임 규칙 준수
- 덱이 비어있을 때 자동 처리
- 맨 위 카드 보존 (게임 규칙)

**코드 예시**:
```python
def reshuffle_discard_pile(self) -> None:
    """버림 더미를 덱으로 재생성"""
    if not self.discard_pile:
        return
    
    # 맨 위 카드 제외
    top_card = self.discard_pile.pop() if self.discard_pile else None
    
    # 나머지 카드를 덱으로 이동
    self.deck = self.discard_pile.copy()
    self.discard_pile.clear()
    
    # 맨 위 카드 다시 추가
    if top_card:
        self.discard_pile.append(top_card)
    
    # 덱 셔플
    self.shuffle()
```

## 주요 메서드

### 덱 생성
- `create_deck()`: 전체 카드 덱 생성
- `create_full_deck_and_shuffle()`: 덱 생성 및 셔플 (편의 메서드)

### 카드 드로우
- `draw_card()`: 카드 1장 뽑기
- `draw_cards(count)`: 카드 여러 장 뽑기

### 카드 버리기
- `discard_card(card)`: 카드 1장 버리기
- `discard_cards(cards)`: 카드 여러 장 버리기

### 덱 관리
- `shuffle()`: 덱 셔플
- `reshuffle_discard_pile()`: 버림 더미를 덱으로 재생성
- `reset()`: 초기화

### 조회
- `get_deck_count()`: 덱 카드 수
- `get_discard_count()`: 버림 더미 카드 수
- `get_discard_top()`: 버림 더미 맨 위 카드 조회

## 사용 예시

```python
from app.game.card_manager import CardManager

# 카드 관리자 생성
card_manager = CardManager()

# 덱 생성 및 셔플
deck = card_manager.create_full_deck_and_shuffle()

# 카드 뽑기
card = card_manager.draw_card()

# 카드 버리기
card_manager.discard_card(card)

# 덱이 비어있을 때 재생성
if card_manager.get_deck_count() == 0:
    card_manager.reshuffle_discard_pile()
```

## 트러블슈팅

### 이슈: 덱 재생성 시 맨 위 카드 처리
**문제**: BANG! 게임 규칙상 버림 더미의 맨 위 카드는 덱 재생성 시 제외해야 함

**해결**: 
- 맨 위 카드를 별도로 보관
- 나머지 카드만 덱으로 이동
- 셔플 후 맨 위 카드 다시 추가

**결과**: 게임 규칙 준수하며 덱 재생성 가능

## 성능 고려사항

### 1. 카드 생성 최적화
- 덱 생성은 게임 시작 시 1회만 수행
- 약 80장의 카드 생성 (O(n) 시간 복잡도)

### 2. 셔플 최적화
- Python의 `random.shuffle()` 사용 (Fisher-Yates 알고리즘)
- O(n) 시간 복잡도

### 3. 덱 재생성 최적화
- 리스트 복사 사용 (`copy()`)
- 불필요한 메모리 할당 최소화

### 4. 향후 개선 가능 사항
- 대량 게임 룸 지원 시 카드 풀 공유 고려
- 카드 생성 캐싱 (동일한 덱 재사용)

## 카드 덱 구성

총 **80장**의 카드로 구성:

| 카드 타입 | 개수 | 설명 |
|----------|------|------|
| 정산 | 25 | 기본 공격 카드 |
| 회피 | 12 | 기본 방어 카드 |
| 전원 견제 | 1 | 모두 공격 |
| 패거리 습격 | 2 | 모두 공격 |
| 승부 | 3 | 1대1 결투 |
| 비상금 | 6 | 재력 회복 |
| 연속 상환 요구 | 2 | 무기 (영향력 1) |
| 독점 상권 선언 | 1 | 무기 (영향력 5) |
| 첩보원 | 1 | 장착 (영향력 +1) |
| 신의 한 수 | 1 | 장착 (카드 뽑기 방어) |
| 세력권 경계 | 1 | 장착 (공격 영향력 +1) |
| 영업 금지 | 3 | 장착 (턴 제한) |
| 강제 압류 | 4 | 특수 (카드 강탈) |
| 공개 연회 | 1 | 특수 (모두 회복) |
| 자선 경매 | 1 | 특수 (카드 분배) |

## 다음 단계
- [ ] 게임 매니저에서 CardManager 통합
- [ ] 카드 드로우 로직 테스트
- [ ] 덱 재생성 로직 테스트

