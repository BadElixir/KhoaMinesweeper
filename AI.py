import random

# DELTA chứa 8 hướng xung quanh 1 ô (Moore neighborhood)
# Dùng để duyệt các ô lân cận trong Minesweeper
DELTA = [
    (-1,-1), (-1,0), (-1,1),
    (0,-1),         (0,1),
    (1,-1),  (1,0), (1,1)
]

def solve(board, flags_left):
    """
    board: ma trận 2 chiều (list[list])
        - None  : ô chưa mở
        - "F"   : ô đã đặt cờ
        - int   : ô đã mở, chứa số bomb xung quanh (0-8)

    flags_left: số lượng cờ còn lại có thể đặt

    return:
        ("flag", row, col)    -> đặt cờ tại (row, col)
        ("reveal", row, col)  -> mở ô tại (row, col)
        ("none", -1, -1)      -> không còn nước đi
    """
    rows = len(board)
    cols = len(board[0])

    # ==========================
    # 1️⃣ Thử tìm chỗ đặt flag
    # ==========================

    if flags_left > 0:  

        for r in range(rows):
            for c in range(cols):

                if isinstance(board[r][c], int) and board[r][c] > 0:

                    hidden = []
                    flagged = 0

                    for dr, dc in DELTA:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:

                            if board[nr][nc] is None:
                                hidden.append((nr, nc))

                            if board[nr][nc] == "F":
                                flagged += 1

                 
                    if hidden and flagged + len(hidden) == board[r][c]:

                        
                        return ("flag", hidden[0][0], hidden[0][1])

    # ==========================
    # 2️⃣ Nếu không đặt được flag → reveal an toàn
    # ==========================

    for r in range(rows):
        for c in range(cols):

            if isinstance(board[r][c], int):

                hidden = []
                flagged = 0

                for dr, dc in DELTA:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:

                        if board[nr][nc] is None:
                            hidden.append((nr, nc))

                        if board[nr][nc] == "F":
                            flagged += 1

                
                if hidden and flagged == board[r][c]:
                    return ("reveal", hidden[0][0], hidden[0][1])

    # ==========================
    # 3️⃣ Fallback → random
    # ==========================

    unopened = []

    for r in range(rows):
        for c in range(cols):
            if board[r][c] is None:
                unopened.append((r, c))

    if not unopened:
        return ("none", -1, -1)

    r, c = random.choice(unopened)
    return ("reveal", r, c)