from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from enum import Enum
import random
import uvicorn
from AI import solve
app = FastAPI()
import webbrowser
import threading

DELTA_PAIRS = [
    (dy, dx)
    for dy in (-1, 0, 1)
    for dx in (-1, 0, 1)
    if not (dy == 0 and dx == 0)
]



class CustomNotif(str, Enum):
    NO_BOMB = "NO_BOMB"
    FOUND_BOMB = "FOUND_BOMB"
    INVALID_COORDINATES = "INVALID_COORDINATES"
    OUT_OF_FLAG = "OUT_OF_FLAG"
    TILE_FLAGGED = "TILE_FLAGGED"
    TILE_UNFLAGGED = "TILE_UNFLAGGED"
    GAME_WON = "GAME_WON"



class Move(BaseModel):
    row: int
    col: int

class NewGameRequest(BaseModel):
    board_size: int
    bomb_count: int



class BoardTile:
    def __init__(self):
        self.adjacent_bombs = 0
        self.revealed = False
        self.has_bomb = False
        self.flagged = False


class Game:
    def __init__(self, board_size=8, bomb_count=10):
        self.board_size = board_size
        self.bomb_count = bomb_count

        self.board = [
            [BoardTile() for _ in range(board_size)]
            for _ in range(board_size)
        ]

        self.first_move = True
        self.revealed_tiles = 0
        self.safe_tiles = board_size * board_size - bomb_count
        self.available_flags = bomb_count
        self.bombs_locations = []
        self.game_over = False



    def coords_valid(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size

 

    def place_bombs(self, safe_row, safe_col):
        valid_cells = []

        for r in range(self.board_size):
            for c in range(self.board_size):
                if abs(r - safe_row) <= 1 and abs(c - safe_col) <= 1:
                    continue
                valid_cells.append((r, c))

        random.shuffle(valid_cells)
        bombs = valid_cells[:self.bomb_count]

        for r, c in bombs:
            self.board[r][c].has_bomb = True

        self.bombs_locations = bombs

    def place_numbers(self):
        for y_bomb, x_bomb in self.bombs_locations:
            for dy, dx in DELTA_PAIRS:
                ny, nx = y_bomb + dy, x_bomb + dx
                if self.coords_valid(ny, nx):
                    self.board[ny][nx].adjacent_bombs += 1


    def reveal_safe_area(self, row, col):
        stack = [(row, col)]

        while stack:
            y, x = stack.pop()
            tile = self.board[y][x]

            if tile.revealed or tile.flagged:
                continue

            tile.revealed = True
            self.revealed_tiles += 1

            if tile.adjacent_bombs > 0:
                continue

            for dy, dx in DELTA_PAIRS:
                ny, nx = y + dy, x + dx
                if self.coords_valid(ny, nx):
                    neighbor = self.board[ny][nx]
                    if not neighbor.revealed and not neighbor.has_bomb:
                        stack.append((ny, nx))

    def reveal(self, row, col):
        if self.game_over:
            return CustomNotif.FOUND_BOMB

        if not self.coords_valid(row, col):
            return CustomNotif.INVALID_COORDINATES

        tile = self.board[row][col]

        if tile.flagged:
            return CustomNotif.INVALID_COORDINATES

        if self.first_move:
            self.place_bombs(row, col)
            self.place_numbers()
            self.first_move = False

        if tile.has_bomb:
            self.game_over = True
            return CustomNotif.FOUND_BOMB

        self.reveal_safe_area(row, col)

        if self.revealed_tiles == self.safe_tiles:
            self.game_over = True
            return CustomNotif.GAME_WON

        return CustomNotif.NO_BOMB


    def flag(self, row, col):
        if not self.coords_valid(row, col):
            return CustomNotif.INVALID_COORDINATES

        tile = self.board[row][col]

        if tile.revealed:
            return CustomNotif.INVALID_COORDINATES

        if tile.flagged:
            tile.flagged = False
            self.available_flags += 1
            return CustomNotif.TILE_UNFLAGGED

        if self.available_flags <= 0:
            return CustomNotif.OUT_OF_FLAG

        tile.flagged = True
        self.available_flags -= 1
        return CustomNotif.TILE_FLAGGED


    def get_board_state(self):
        result = []

        for row in self.board:
            row_data = []
            for tile in row:
                if tile.revealed:
                    row_data.append(tile.adjacent_bombs)
                elif tile.flagged:
                    row_data.append("F")
                else:
                    row_data.append(None)
            result.append(row_data)

        return result




game = Game()



@app.post("/new-game")
def new_game(request: NewGameRequest):
    global game

    if request.board_size < 2:
        return {"error": "Board size must be >= 2"}

    if request.bomb_count <= 0:
        return {"error": "Bomb count must be > 0"}

    if request.bomb_count >= request.board_size ** 2:
        return {"error": "Too many bombs"}

    game = Game(request.board_size, request.bomb_count)

    return {
        "message": "Game created",
        "board_size": request.board_size,
        "bomb_count": request.bomb_count
    }


@app.post("/reveal")
def reveal(move: Move):
    result = game.reveal(move.row, move.col)
    return {
        "result": result,
        "board": game.get_board_state(),
        "flags_left": game.available_flags
    }


@app.post("/flag")
def flag(move: Move):
    result = game.flag(move.row, move.col)
    return {
        "result": result,
        "board": game.get_board_state(),
        "flags_left": game.available_flags
    }


@app.get("/state")
def state():
    return {
        "board": game.get_board_state(),
        "flags_left": game.available_flags
    }

@app.get("/ai_move")
def ai_move():

    if game.game_over:
        return {"action": "none", "row": -1, "col": -1}

    board = game.get_board_state()

    action, row, col = solve(board, game.available_flags)

    return {
        "action": action,
        "row": row,
        "col": col
    }

@app.get("/")
def serve_index():
    return FileResponse("index.html")


def open_browser():
    webbrowser.open("http://127.0.0.1:3210/")
    
if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=3210,
        reload=True
    )
