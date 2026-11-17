"""모델 직렬화와 누락된 게임 구성요소의 안전한 실패를 검증한다."""
from unittest.mock import MagicMock

import pytest

from app.game.action_handler import ActionHandler
from app.game.card_manager import CardManager
from app.game.game_manager import GameManager
from app.models.card import Card
from app.models.player import Player
from app.models.role import Role
from app.utils.constants import CardType, Role as RoleEnum, TurnState
from app.websocket.connection_manager import ConnectionManager
from app.websocket.message_handler import MessageHandler


def test_role_input_and_invalid_default():
    sheriff = Role(RoleEnum.SHERIFF)
    assert Role(sheriff).role == RoleEnum.SHERIFF
    assert Role(RoleEnum.OUTLAW.value).role == RoleEnum.OUTLAW
    assert Role('존재하지 않는 역할').role == RoleEnum.SHERIFF


def test_default_fields_and_private_hand_serialization():
    manager = GameManager()
    game = manager.create_game('fixture')
    player = Player.create('alice', 'Alice', RoleEnum.SHERIFF, 0)
    card = Card(id='fixture-card', card_type=CardType.BANG, name='fixture')
    player.add_card(card)
    assert player.treasure is None
    assert game.current_player_id is None
    assert game.pending_action is None
    assert player.to_dict()['hand'][0]['id'] == card.id
    assert player.to_dict(hide_hand=True)['hand'] == []
    assert player.to_dict(hide_hand=True)['handCount'] == 1
    assert str(card) == 'fixture'


def test_missing_player_is_rejected_before_action():
    manager = GameManager()
    game = manager.create_game('fixture')
    turn_manager = MagicMock()
    turn_manager.can_play_card.return_value = True
    turn_manager.can_end_turn.return_value = True
    handler = ActionHandler(game, turn_manager, CardManager())
    assert not handler.handle_use_card('missing', {'card_id': 'fixture'})['success']
    game.turn_state = TurnState.RESPOND
    assert not handler.handle_respond_attack('missing', {'card_id': 'fixture'})['success']
    assert not handler.handle_end_turn('missing')['success']
    turn_manager.end_turn.assert_not_called()


@pytest.mark.asyncio
async def test_missing_card_manager_yields_protocol_error():
    manager = GameManager()
    manager.create_game('fixture')
    manager.card_managers.pop('fixture')
    connections = ConnectionManager()
    connections.player_games['alice'] = 'fixture'
    handler = MessageHandler(manager, connections)
    result = await handler.handle_player_action('alice', {'action': {'type': 'END_TURN'}})
    assert result['success'] is False
    assert result['error_code'] == 'CARD_MANAGER_NOT_FOUND'
    assert connections.get_player_game('missing') is None
