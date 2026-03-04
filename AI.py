import random

# 8 hướng xung quanh
DELTA = [
    (-1,-1), (-1,0), (-1,1),
    (0,-1),         (0,1),
    (1,-1),  (1,0), (1,1)
]

def solve(board, flags_left):
    """
    board:
        None  : ô chưa mở
        "F"   : đã đặt cờ
        int   : số bomb xung quanh

    flags_left: số cờ còn lại

    return:
        ("flag", r, c)
        ("reveal", r, c)
        ("none", -1, -1)
    """

    rows = len(board)
    cols = len(board[0])

    # ==========================================================
    # 1: Nếu chắc chắn là bomb → đặt flag
    # ==========================================================

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

                    # nếu tất cả hidden đều là bomb
                    if hidden and flagged + len(hidden) == board[r][c]:
                        return ("flag", hidden[0][0], hidden[0][1])

    # ==========================================================
    # 2: Nếu chắc chắn an toàn → mở
    # ==========================================================

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

    # ==========================================================
    # 3 CONSTRAINT SOLVER
    # ==========================================================

    move = constraint_solver(board, flags_left)
    if move[0] != "none":
        return move

    # ==========================================================
    # 4 PROBABILITY SOLVER
    # ==========================================================

    move = probability_solver(board, flags_left)
    if move[0] != "none":
        return move

    # ==========================================================
    # 5 Fallback: random nếu không có thông tin
    # ==========================================================

    unopened = []
    for r in range(rows):
        for c in range(cols):
            if board[r][c] is None:
                unopened.append((r, c))

    if not unopened:
        return ("none", -1, -1)

    r, c = random.choice(unopened)
    return ("reveal", r, c)




def constraint_solver(board, flags_left):
    rows = len(board)
    cols = len(board[0])

    constraints = []

    # ===============================
    # Thu thập constraint ban đầu
    # ===============================
    for r in range(rows):
        for c in range(cols):

            if isinstance(board[r][c], int) and board[r][c] > 0:

                hidden = set()
                flagged = 0

                for dr, dc in DELTA:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if board[nr][nc] is None:
                            hidden.add((nr, nc))
                        if board[nr][nc] == "F":
                            flagged += 1

                bomb_left = board[r][c] - flagged

                if hidden and bomb_left >= 0:
                    constraints.append({
                        "cells": hidden,
                        "bombs": bomb_left
                    })

    # ===============================
    # Propagation loop
    # ===============================

    changed = True

    while changed:
        changed = False
        new_constraints = []

        for i in range(len(constraints)):
            for j in range(len(constraints)):

                if i == j:
                    continue

                c1 = constraints[i]
                c2 = constraints[j]

                cells1 = c1["cells"]
                cells2 = c2["cells"]

                # subset case
                if cells1.issubset(cells2) and cells1 != cells2:

                    diff_cells = cells2 - cells1
                    diff_bombs = c2["bombs"] - c1["bombs"]

                    # =========================
                    # Case 1: an toàn
                    # =========================
                    if diff_bombs == 0 and diff_cells:
                        r, c = next(iter(diff_cells))
                        return ("reveal", r, c)

                    # =========================
                    # Case 2: toàn bomb
                    # =========================
                    if diff_bombs == len(diff_cells) and diff_cells:
                        r, c = next(iter(diff_cells))
                        return ("flag", r, c)

                    # =========================
                    # Case 3: constraint mới
                    # =========================
                    if 0 < diff_bombs < len(diff_cells):

                        new_constraint = {
                            "cells": diff_cells,
                            "bombs": diff_bombs
                        }

                        if new_constraint not in constraints:
                            new_constraints.append(new_constraint)
                            changed = True

        constraints.extend(new_constraints)

    return ("none", -1, -1)

def probability_solver(board, flags_left):
    rows = len(board)
    cols = len(board[0])

    probabilities = {}  # (r,c) -> P_bomb

    for r in range(rows):
        for c in range(cols):

            if board[r][c] is None:

                p_safe_total = 1
                influenced = False

                # duyệt các ô số xung quanh nó
                for dr, dc in DELTA:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:

                        if isinstance(board[nr][nc], int) and board[nr][nc] > 0:

                            hidden = []
                            flagged = 0

                            for dr2, dc2 in DELTA:
                                rr, cc = nr + dr2, nc + dc2
                                if 0 <= rr < rows and 0 <= cc < cols:
                                    if board[rr][cc] is None:
                                        hidden.append((rr, cc))
                                    if board[rr][cc] == "F":
                                        flagged += 1

                            if (r, c) in hidden and len(hidden) > 0:

                                influenced = True

                                bomb_left = board[nr][nc] - flagged
                                p = bomb_left / len(hidden)

                                # xác suất không dính bomb
                                p_safe_total *= (1 - p)

                if influenced:
                    probabilities[(r, c)] = 1 - p_safe_total

    if probabilities:
        best_cell = min(probabilities, key=probabilities.get)
        return ("reveal", best_cell[0], best_cell[1])

    return ("none", -1, -1)