import random

from src.board import Board


MAX_SIZE = 20


def _count_inversions(tiles):
    inv = 0
    arr = [t for t in tiles if t != 0]
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    return inv


def _invariant(board: Board) -> int:
    inv = _count_inversions(board.tiles)
    if board.size % 2 == 1:
        return inv % 2
    else:
        return (inv + board.row) % 2


_goal_invariant_cache = {}


def _get_goal_invariant(size: int) -> int:
    if size not in _goal_invariant_cache:
        goal = Board.generate_goal(size)
        _goal_invariant_cache[size] = _invariant(goal)
    return _goal_invariant_cache[size]


def is_solvable(board: Board) -> bool:
    return _invariant(board) == _get_goal_invariant(board.size)


def generate_puzzle(size: int, iterations: int = 0) -> Board:
    if size < 1:
        raise ValueError(f"Size must be at least 1, got {size}")
    if size > MAX_SIZE:
        raise ValueError(f"Size too large: {size} (max is {MAX_SIZE})")
    goal = Board.generate_goal(size)
    if size == 1:
        return goal
    if iterations <= 0:
        iterations = size * size * 10
    board = goal
    previous = None
    while board == goal:
        for _ in range(iterations):
            options = [n for n in board.get_neighbors() if n != previous]
            previous = board
            board = random.choice(options)
    return board
