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
    # 4 GAUSS ELIMINATION
    # ==========================================================
                
    gauss_move = gauss_solver(board)
    if gauss_move:
        return gauss_move

    # ==========================================================
    # 5 TANK SOLVER (BACKTRACKING)
    # ==========================================================

    tank_move = tank_solver(board, flags_left)
    if tank_move:
        return tank_move
    
    # ==========================================================
    # 6 PROBABILITY SOLVER
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
        if len(constraints) > 400:
            break
    # ===============================
    # Global disjoint region reasoning
    # ===============================

    # Tìm tập các constraint không chồng lấn
    disjoint_sets = []
    used_cells = set()
    total_bombs = 0

    for c in constraints:
        if not c["cells"].intersection(used_cells):
            disjoint_sets.append(c)
            used_cells.update(c["cells"])
            total_bombs += c["bombs"]

    # Nếu tổng bomb của các vùng = flags_left
    if total_bombs == flags_left and total_bombs > 0:

        # Các ô chưa mở còn lại ngoài used_cells đều an toàn
        for r in range(rows):
            for c in range(cols):
                if board[r][c] is None and (r, c) not in used_cells:
                    return ("reveal", r, c)
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

def gauss_solver(board):
    """Giải hệ phương trình bằng khử Gauss - Đã tối ưu biến số"""
    rows = len(board)
    cols = len(board[0])
    
    # 1. Thu thập các ô biên (chỉ lấy những ô ẩn nằm cạnh các con số)
    border_cells = []
    border_set = set()
    equations = []

    for r in range(rows):
        for c in range(cols):
            if isinstance(board[r][c], int) and board[r][c] > 0:
                h_neigh = []
                flagged = 0
                for dr, dc in DELTA:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if board[nr][nc] is None:
                            h_neigh.append((nr, nc))
                            if (nr, nc) not in border_set:
                                border_set.add((nr, nc))
                                border_cells.append((nr, nc))
                        elif board[nr][nc] == "F":
                            flagged += 1
                
                if h_neigh:
                    equations.append({
                        "cells": h_neigh,
                        "target": board[r][c] - flagged
                    })

    if not equations: 
        return None

    # 2. Xây dựng ma trận với kích thước siêu nhỏ (chỉ chứa các ô biên)
    num_vars = len(border_cells)
    cell_to_idx = {cell: i for i, cell in enumerate(border_cells)}
    matrix = []

    for eq in equations:
        row = [0] * (num_vars + 1)
        for cell in eq["cells"]: 
            row[cell_to_idx[cell]] = 1
        row[-1] = eq["target"]
        matrix.append(row)

    # 3. Thuật toán Khử Gauss (Gauss Elimination)
    num_eqs = len(matrix)
    pivot = 0
    for j in range(num_vars):
        if pivot >= num_eqs: break
        sel = pivot
        while sel < num_eqs and matrix[sel][j] == 0: 
            sel += 1
        
        if sel == num_eqs: 
            continue
            
        # Swap rows
        matrix[pivot], matrix[sel] = matrix[sel], matrix[pivot]
        
        for i in range(num_eqs):
            if i != pivot and matrix[i][j] != 0:
                factor = matrix[i][j] / matrix[pivot][j]
                for k in range(j, num_vars + 1): 
                    matrix[i][k] -= factor * matrix[pivot][k]
        pivot += 1

    # 4. Phân tích nghiệm chắc chắn
    for row in matrix:
        target = row[-1]
        # Lọc ra các biến có hệ số khác 0
        coeffs = [i for i in range(num_vars) if abs(row[i]) > 0.001]
        
        if len(coeffs) > 0:
            # Nếu hệ số dương và tổng hệ số bằng target -> Tất cả là mìn
            if abs(sum(row[i] for i in coeffs) - target) < 0.001 and all(row[i] > 0 for i in coeffs):
                return ("flag", border_cells[coeffs[0]][0], border_cells[coeffs[0]][1])
            
            # Nếu target = 0 và các hệ số cùng dấu -> Tất cả an toàn
            if abs(target) < 0.001 and all(row[i] > 0 for i in coeffs):
                return ("reveal", border_cells[coeffs[0]][0], border_cells[coeffs[0]][1])

    return None

def tank_solver(board, flags_left):
    rows, cols = len(board), len(board[0])
    border_cells_set = set()
    relevant_numbers = []
    
    for r in range(rows):
        for c in range(cols):
            if isinstance(board[r][c], int) and board[r][c] > 0:
                hidden_neighbors = []
                flagged_count = 0
                for dr, dc in DELTA:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if board[nr][nc] is None:
                            hidden_neighbors.append((nr, nc))
                            border_cells_set.add((nr, nc))
                        elif board[nr][nc] == "F":
                            flagged_count += 1
                if hidden_neighbors:
                    relevant_numbers.append({
                        "target": board[r][c] - flagged_count,
                        "cells": hidden_neighbors
                    })

    if not border_cells_set: return None
    border_cells = list(border_cells_set)
    
    # Tạo đồ thị để phân cụm (Clusters)
    adj = {cell: set() for cell in border_cells}
    for num in relevant_numbers:
        cells = num["cells"]
        for i in range(len(cells)):
            for j in range(i + 1, len(cells)):
                adj[cells[i]].add(cells[j]); adj[cells[j]].add(cells[i])

    visited = set()
    for cell in border_cells:
        if cell in visited: continue
        cluster = []
        stack = [cell]; visited.add(cell)
        while stack:
            curr = stack.pop(); cluster.append(curr)
            for n in adj[curr]:
                if n not in visited: visited.add(n); stack.append(n)
        
        if len(cluster) > 20: continue # Giới hạn độ phức tạp

        cluster_nums = [n for n in relevant_numbers if any(c in cluster for c in n["cells"])]
        cell_to_idx = {c: i for i, c in enumerate(cluster)}
        solutions = []

        def backtrack(c_idx, current_path, current_bombs):
            # Kiểm tra nhanh các ràng buộc của những con số liên quan
            for num in cluster_nums:
                # Chỉ kiểm tra những con số mà tất cả ô xung quanh nó đã được gán giá trị trong backtrack
                # Hoặc kiểm tra vi phạm sớm (quá số mìn)
                assigned_in_num = [cell_to_idx[c] for c in num["cells"] if cell_to_idx[c] < c_idx]
                bombs_assigned = sum(current_path[i] for i in assigned_in_num)
                
                if bombs_assigned > num["target"]: return # Quá số mìn cho phép
                
                remaining_tiles = len(num["cells"]) - len(assigned_in_num)
                if bombs_assigned + remaining_tiles < num["target"]: return # Không đủ mìn để lấp đầy

            # Kiểm tra số mìn toàn cục
            if current_bombs > flags_left: return

            if c_idx == len(cluster):
                solutions.append(list(current_path))
                return

            # Thử đặt mìn (1)
            current_path.append(1)
            backtrack(c_idx + 1, current_path, current_bombs + 1)
            current_path.pop()

            # Thử an toàn (0)
            current_path.append(0)
            backtrack(c_idx + 1, current_path, current_bombs)
            current_path.pop()

        backtrack(0, [], 0)
        if not solutions: continue

        # Phân tích kết quả: Tìm ô nào có giá trị giống nhau trong TẤT CẢ giải pháp
        num_sols = len(solutions)
        for i, cell in enumerate(cluster):
            total_bombs_at_i = sum(sol[i] for sol in solutions)
            if total_bombs_at_i == num_sols: # 100% là mìn
                return ("flag", cell[0], cell[1])
            if total_bombs_at_i == 0: # 100% an toàn
                return ("reveal", cell[0], cell[1])
                
    return None