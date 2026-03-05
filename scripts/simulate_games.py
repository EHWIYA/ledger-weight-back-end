"""
간단한 규칙 기반 AI를 사용해 여러 판의 게임을 자동 시뮬레이션하는 스크립트.

주의: 이 스크립트는 내부 테스트/밸런스 체크용이며, 실제 서비스 경로와는 분리된 유틸리티입니다.
"""

import os
import sys
import random
from typing import Dict

# 프로젝트 루트를 PYTHONPATH에 추가
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.game.game_manager import GameManager
from app.game.turn_manager import TurnManager
from app.game.action_handler import ActionHandler
from app.utils.constants import ActionType, GameState, TurnState


def run_single_game(game_manager: GameManager, player_count: int = 4) -> Dict:
    """단일 게임을 AI끼리 돌리고 결과 요약을 반환합니다."""
    game = game_manager.create_game()
    game_id = game.id

    # 플레이어 생성 (전부 봇)
    for i in range(player_count):
        player_id = f"bot_{i+1}"
        player_name = f"Bot_{i+1}"
        game_manager.add_player_to_game(game_id, player_id, player_name)

    # 게임 시작
    started = game_manager.start_game(game_id)
    if not started:
        return {"success": False, "reason": "FAILED_TO_START"}

    card_manager = game_manager.get_card_manager(game_id)
    turn_manager = TurnManager(game, card_manager)
    action_handler = ActionHandler(game, turn_manager, card_manager)

    max_turns = 500

    # 첫 번째 턴 시작 (드로우 및 턴 상태 설정)
    if game.current_player_id:
        turn_manager.start_turn(game.current_player_id)

    while game.state == GameState.IN_PROGRESS and game.turn_number <= max_turns:
        # 먼저 대응 단계가 있는지 처리
        if game.turn_state == TurnState.RESPOND and game.defending_player_id:
            defender = game.get_player(game.defending_player_id)
            if defender and defender.is_alive:
                # 가능한 경우 회피 카드를 사용, 없으면 포기
                card_to_use = None
                for c in defender.hand:
                    if c.is_missed() or c.is_bang():
                        card_to_use = c
                        break
                if card_to_use:
                    action_handler.handle_action(
                        ActionType.RESPOND_ATTACK,
                        defender.id,
                        {"card_id": card_to_use.id},
                    )
                else:
                    action_handler.handle_respond_attack_failed(defender.id)
            continue

        current = turn_manager.get_current_player()
        if not current or not current.is_alive:
            # 안전장치: 다음 플레이어로 이동
            if not turn_manager.move_to_next_player():
                break
            continue

        # 간단한 AI: 공격 가능하면 아무나 공격, 아니면 비상금/장착, 그 외 턴 종료
        acted = False
        for card in list(current.hand):
            if card.is_bang():
                # 임의의 유효 타깃 찾기
                targets = [
                    p for p in game.get_alive_players()
                    if p.id != current.id
                ]
                if not targets:
                    continue
                target = random.choice(targets)
                result = action_handler.handle_action(
                    ActionType.USE_CARD,
                    current.id,
                    {"card_id": card.id, "target_id": target.id},
                )
                acted = True
                break
            elif card.is_beer():
                result = action_handler.handle_action(
                    ActionType.USE_CARD,
                    current.id,
                    {"card_id": card.id},
                )
                acted = True
                break

        # 특별한 액션이 없으면 턴 종료
        action_handler.handle_action(ActionType.END_TURN, current.id, {})

        # 승리 조건 체크
        win_info = game_manager.check_win_condition(game_id)
        if win_info:
            return {
                "success": True,
                "winner_role": win_info.get("winner_role"),
                "winner_id": win_info.get("winner_id"),
                "turns": game.turn_number,
            }

    return {
        "success": False,
        "reason": "MAX_TURNS_REACHED",
        "turns": game.turn_number,
    }


def simulate(n: int = 100, player_count: int = 4) -> None:
    """여러 판 시뮬레이션을 돌리고 역할별 승리 횟수를 출력합니다."""
    gm = GameManager()
    stats: Dict[str, int] = {}
    failures: Dict[str, int] = {}

    for _ in range(n):
        result = run_single_game(gm, player_count=player_count)
        role = result.get("winner_role")
        if role:
            stats[role] = stats.get(role, 0) + 1
        else:
            reason = result.get("reason", "UNKNOWN")
            failures[reason] = failures.get(reason, 0) + 1

    print(f"Simulated {n} games (players={player_count})")
    for role, count in stats.items():
        print(f"- {role}: {count} wins")
    if failures:
        print("Failures:")
        for reason, count in failures.items():
            print(f"- {reason}: {count} games")


if __name__ == "__main__":
    simulate(50, player_count=4)

