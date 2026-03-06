import AI


# ----------------------------
# solve(...) deterministic rules
# ----------------------------
def test_solve_flag_when_hidden_must_be_bomb():
    board = [
        [1, None],
        [0, 0],
    ]
    assert AI.solve(board, flags_left=1) == ("flag", 0, 1)


def test_solve_reveal_when_all_bombs_already_flagged():
    board = [
        [1, "F"],
        [None, 0],
    ]
    assert AI.solve(board, flags_left=1) == ("reveal", 1, 0)


def test_solve_no_flag_when_no_flags_left():
    board = [
        [1, None],
        [0, 0],
    ]
    assert AI.solve(board, flags_left=0) == ("reveal", 0, 1)


def test_solve_when_flagged_more_than_possible_bombs_uses_fallback(monkeypatch):
    board = [
        [1, "F"],
        ["F", None],
    ]
    called = {"random_choice": False}

    monkeypatch.setattr(AI, "constraint_solver", lambda *_: ("none", -1, -1))
    monkeypatch.setattr(AI, "probability_solver", lambda *_: ("none", -1, -1))

    def fake_choice(unopened):
        called["random_choice"] = True
        return unopened[0]

    monkeypatch.setattr(AI.random, "choice", fake_choice)

    assert AI.solve(board, flags_left=1) == ("reveal", 1, 1)
    assert called["random_choice"] is True


def test_solve_none_when_board_fully_opened():
    board = [
        [0, 1],
        [1, 1],
    ]
    assert AI.solve(board, flags_left=0) == ("none", -1, -1)


def test_solve_random_fallback(monkeypatch):
    board = [
        [None, None],
        [None, None],
    ]
    monkeypatch.setattr(AI.random, "choice", lambda unopened: unopened[2])
    assert AI.solve(board, flags_left=0) == ("reveal", 1, 0)


# ----------------------------
# solve(...) solver ordering
# ----------------------------
def test_solve_prefers_constraint_solver_over_probability(monkeypatch):
    board = [[None]]

    monkeypatch.setattr(AI, "constraint_solver", lambda *_: ("reveal", 0, 0))
    monkeypatch.setattr(AI, "probability_solver", lambda *_: ("flag", 0, 0))
    monkeypatch.setattr(
        AI.random,
        "choice",
        lambda *_: (_ for _ in ()).throw(AssertionError("random must not be called")),
    )
    assert AI.solve(board, flags_left=1) == ("reveal", 0, 0)


def test_solve_uses_probability_when_constraint_has_no_move(monkeypatch):
    board = [[None]]

    monkeypatch.setattr(AI, "constraint_solver", lambda *_: ("none", -1, -1))
    monkeypatch.setattr(AI, "probability_solver", lambda *_: ("reveal", 0, 0))
    monkeypatch.setattr(
        AI.random,
        "choice",
        lambda *_: (_ for _ in ()).throw(AssertionError("random must not be called")),
    )
    assert AI.solve(board, flags_left=1) == ("reveal", 0, 0)


# ----------------------------
# constraint_solver(...)
# ----------------------------
def test_constraint_solver_subset_case_reveal_safe():
    board = [
        [1, 1, None],
        [None, None, None],
        [0, 0, 0],
    ]
    action, r, c = AI.constraint_solver(board, flags_left=2)
    assert action == "reveal"
    assert (r, c) in {(0, 2), (1, 2)}


def test_constraint_solver_subset_case_flag_bomb():
    board = [
        [1, 3, None],
        [None, None, None],
        [0, 0, 0],
    ]
    action, r, c = AI.constraint_solver(board, flags_left=2)
    assert action == "flag"
    assert (r, c) in {(0, 2), (1, 2)}


def test_constraint_solver_ignores_over_flagged_constraints():
    board = [
        [1, "F"],
        ["F", None],
    ]
    assert AI.constraint_solver(board, flags_left=1) == ("none", -1, -1)


def test_constraint_solver_global_disjoint_region_reveal_outside_constraints():
    board = [
        [1, None, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, None, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, None, 1],
    ]
    assert AI.constraint_solver(board, flags_left=2) == ("reveal", 2, 2)


def test_constraint_solver_none_when_no_actionable_constraints():
    board = [
        [0, 0],
        [0, None],
    ]
    assert AI.constraint_solver(board, flags_left=0) == ("none", -1, -1)


# ----------------------------
# probability_solver(...)
# ----------------------------
def test_probability_solver_chooses_lowest_risk_cell():
    board = [
        [1, None, None],
        [1, 2, None],
        [0, 0, 0],
    ]
    assert AI.probability_solver(board, flags_left=3) == ("reveal", 0, 2)


def test_probability_solver_with_exact_flags_treats_hidden_as_safe():
    board = [
        [1, "F"],
        [None, 0],
    ]
    assert AI.probability_solver(board, flags_left=1) == ("reveal", 1, 0)


def test_probability_solver_none_without_influenced_cells():
    board = [
        [None, None],
        [None, None],
    ]
    assert AI.probability_solver(board, flags_left=2) == ("none", -1, -1)
