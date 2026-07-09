from src.board import Board
from typing import Dict, Tuple


_goal_positions_cache: Dict[int, Dict[int, Tuple[int, int]]] = {}


def _get_goal_positions(size: int) -> Dict[int, Tuple[int, int]]:
    if size not in _goal_positions_cache:
        goal = Board.generate_goal(size)
        positions = {}
        for i in range(len(goal)):
            tile = goal[i]
            if tile != 0:
                positions[tile] = (i // size, i % size)
        _goal_positions_cache[size] = positions
    return _goal_positions_cache[size]


def manhattan_distance(board: Board) -> int:
    size = board.size
    goal_positions = _get_goal_positions(size)
    distance = 0
    for i, tile in enumerate(board.tiles):
        if tile == 0:
            continue
        goal_row, goal_col = goal_positions[tile]
        current_row, current_col = i // size, i % size
        distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance


def misplaced_tiles(board: Board) -> int:
    size = board.size
    goal = Board.generate_goal(size)
    count = 0
    for i, tile in enumerate(board.tiles):
        if tile != 0 and tile != goal[i]:
            count += 1
    return count


def linear_conflict(board: Board) -> int:
    size = board.size
    goal_positions = _get_goal_positions(size)
    conflict = 0

    for row in range(size):
        tiles_in_row = []
        for col in range(size):
            idx = row * size + col
            tile = board[idx]
            if tile == 0:
                continue
            goal_row, goal_col = goal_positions[tile]
            if goal_row == row:
                tiles_in_row.append((col, goal_col, tile))
        for i in range(len(tiles_in_row)):
            for j in range(i + 1, len(tiles_in_row)):
                if tiles_in_row[i][1] > tiles_in_row[j][1]:
                    conflict += 1

    for col in range(size):
        tiles_in_col = []
        for row in range(size):
            idx = row * size + col
            tile = board[idx]
            if tile == 0:
                continue
            goal_row, goal_col = goal_positions[tile]
            if goal_col == col:
                tiles_in_col.append((row, goal_row, tile))
        for i in range(len(tiles_in_col)):
            for j in range(i + 1, len(tiles_in_col)):
                if tiles_in_col[i][1] > tiles_in_col[j][1]:
                    conflict += 1

    return manhattan_distance(board) + 2 * conflict


HEURISTICS = {
    'manhattan': manhattan_distance,
    'misplaced': misplaced_tiles,
    'linear_conflict': linear_conflict,
}
