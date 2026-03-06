import random

from fastapi.testclient import TestClient

import main
from main import CustomNotif, Game


def make_game_with_bombs(board_size, bomb_coords):
    game = Game(board_size=board_size, bomb_count=len(bomb_coords))
    for r, c in bomb_coords:
        game.board[r][c].has_bomb = True
    game.bombs_locations = list(bomb_coords)
    game.place_numbers()
    game.first_move = False
    return game


def test_coords_valid():
    game = Game(board_size=3, bomb_count=1)
    assert game.coords_valid(0, 0) is True
    assert game.coords_valid(2, 2) is True
    assert game.coords_valid(-1, 0) is False
    assert game.coords_valid(3, 0) is False


def test_first_reveal_is_safe_and_places_exact_bombs():
    random.seed(1)
    game = Game(board_size=8, bomb_count=10)

    result = game.reveal(3, 3)

    assert result in (CustomNotif.NO_BOMB, CustomNotif.GAME_WON)
    assert game.first_move is False
    assert game.board[3][3].has_bomb is False
    assert len(game.bombs_locations) == 10
    for r, c in game.bombs_locations:
        assert abs(r - 3) > 1 or abs(c - 3) > 1


def test_reveal_invalid_coordinates():
    game = Game(board_size=4, bomb_count=2)
    assert game.reveal(-1, 0) == CustomNotif.INVALID_COORDINATES
    assert game.reveal(0, 4) == CustomNotif.INVALID_COORDINATES


def test_flag_unflag_and_out_of_flag():
    game = Game(board_size=3, bomb_count=1)

    assert game.flag(0, 0) == CustomNotif.TILE_FLAGGED
    assert game.available_flags == 0
    assert game.flag(1, 1) == CustomNotif.OUT_OF_FLAG
    assert game.flag(0, 0) == CustomNotif.TILE_UNFLAGGED
    assert game.available_flags == 1


def test_game_won_when_all_safe_tiles_revealed():
    game = make_game_with_bombs(board_size=2, bomb_coords=[(0, 0)])

    assert game.reveal(0, 1) == CustomNotif.NO_BOMB
    assert game.reveal(1, 0) == CustomNotif.NO_BOMB
    assert game.reveal(1, 1) == CustomNotif.GAME_WON
    assert game.game_over is True


def test_api_new_game_validation_and_state():
    client = TestClient(main.app)

    bad = client.post("/new-game", json={"board_size": 1, "bomb_count": 1})
    assert bad.status_code == 200
    assert "error" in bad.json()

    ok = client.post("/new-game", json={"board_size": 6, "bomb_count": 6})
    assert ok.status_code == 200
    payload = ok.json()
    assert payload["board_size"] == 6
    assert payload["bomb_count"] == 6

    state = client.get("/state")
    assert state.status_code == 200
    body = state.json()
    assert len(body["board"]) == 6
    assert body["flags_left"] == 6
