from kribu import (
    INITIAL_STATE,
    minimax,
    boardState,
    find_move,
)


def test_minimax_initial_state():
    # Run minimax at depth 1
    res = minimax(INITIAL_STATE, 1)
    assert hasattr(res, "score")
    assert hasattr(res, "moveId")
    assert isinstance(res.score, int)
    assert isinstance(res.moveId, int)
    # The move ID should be a valid move (greater than 0 since INITIAL_STATE has only simple moves)
    assert res.moveId > 0


def test_minimax_winning_move():
    # Setup winning capture move
    state = boardState()
    state.me = 1 << 16
    state.opp = 1 << 17
    state.activeCaptureIdx = -1

    res = minimax(state, 1)
    win_move_id = find_move(16, 18)
    assert res.moveId == win_move_id
    assert res.score >= 1000000
