"""Synthetic, in-process ASGI checks; only run against an isolated image.

The caller must provide a container with no host network, ports, volumes or
production environment. No real user data or credentials are used.
"""
import asyncio
import json
import subprocess
import sys

from app.main import app, connection_manager, game_manager


class Socket:
    def __init__(self, player):
        self.player = player
        self.incoming = asyncio.Queue()
        self.outgoing = asyncio.Queue()
        self.task = None

    async def start(self):
        scope = {
            "type": "websocket", "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1", "scheme": "ws", "path": f"/ws/{self.player}",
            "raw_path": f"/ws/{self.player}".encode(), "query_string": b"",
            "headers": [], "client": ("synthetic", 1), "server": ("synthetic", 80),
            "subprotocols": [], "root_path": "",
        }
        await self.incoming.put({"type": "websocket.connect"})
        self.task = asyncio.create_task(app(scope, self.incoming.get, self.outgoing.put))
        assert (await self.receive_event())["type"] == "websocket.accept"
        assert (await self.receive_message())["type"] == "CONNECTION_ESTABLISHED"

    async def receive_event(self):
        return await asyncio.wait_for(self.outgoing.get(), timeout=5)

    async def receive_message(self):
        event = await self.receive_event()
        assert event["type"] == "websocket.send", event
        return json.loads(event["text"])

    async def send(self, message):
        await self.incoming.put({"type": "websocket.receive", "text": json.dumps(message)})

    async def until(self, kind):
        for _ in range(12):
            message = await self.receive_message()
            if message.get("type") == kind:
                return message
        raise AssertionError(f"missing message: {kind}")

    async def close(self):
        await self.incoming.put({"type": "websocket.disconnect", "code": 1000})
        await asyncio.wait_for(self.task, timeout=5)


async def main():
    game_id = "synthetic-isolation-game"
    assert game_manager.get_game(game_id) is None
    first = Socket("synthetic-alice")
    second = Socket("synthetic-bob")
    await first.start()
    await first.send({"type": "JOIN_GAME", "game_id": game_id, "player_name": "Alice"})
    assert (await first.until("ACTION_RESPONSE"))["data"]["success"] is True
    game = game_manager.get_game(game_id)
    assert game is not None and len(game.players) == 1

    await second.start()
    await second.send({"type": "JOIN_GAME", "game_id": game_id, "player_name": "Bob"})
    assert (await second.until("ACTION_RESPONSE"))["data"]["success"] is True
    assert len(game.players) == 2

    card = game_manager.get_card_manager(game_id).create_deck()[0]
    game.players[0].add_card(card)
    own = game_manager.get_game_state_dict(game_id, "synthetic-alice")
    other = game_manager.get_game_state_dict(game_id, "synthetic-bob")
    alice_own = next(p for p in own["players"] if p["id"] == "synthetic-alice")
    alice_other = next(p for p in other["players"] if p["id"] == "synthetic-alice")
    assert alice_own["hand"][0]["id"] == card.id
    assert alice_other["hand"] == [] and alice_other["handCount"] == 1
    assert alice_other["role"] is None

    await first.close()
    assert not connection_manager.is_connected("synthetic-alice")
    assert game_manager.get_game(game_id) is game
    assert len(game.players) == 2
    reconnected = Socket("synthetic-alice")
    await reconnected.start()
    await reconnected.send({"type": "PING"})
    assert (await reconnected.until("PONG"))["type"] == "PONG"
    # Reconnection alone is not recovery of the room association.
    assert connection_manager.get_player_game("synthetic-alice") is None
    await reconnected.send({"type": "JOIN_GAME", "game_id": game_id, "player_name": "Alice"})
    assert (await reconnected.until("ACTION_RESPONSE"))["data"]["success"] is False
    await reconnected.close()
    await second.close()
    assert connection_manager.get_connection_count() == 0
    assert game_manager.get_game(game_id) is game

    # Fresh interpreter, not a restart of the original process or production service.
    check = "from app.main import game_manager; assert game_manager.get_game('synthetic-isolation-game') is None"
    subprocess.run([sys.executable, "-c", check], check=True, timeout=15)
    print(json.dumps({"asgi_websocket_join_ping_disconnect_reconnect": "passed",
                      "private_hand_visibility": "passed",
                      "same_process_game_retained": "passed",
                      "rejoin_existing_player": "rejected_by_current_app",
                      "fresh_process_state": "absent"}))


if __name__ == "__main__":
    asyncio.run(main())
