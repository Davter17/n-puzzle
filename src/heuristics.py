from typing import Callable, Dict, List, Optional, Tuple

from src.board import Board

# (size, tiles_before, moved_tile, old_pos, new_pos, parent_h) -> child_h
ChildH = Callable[[int, Tuple[int, ...], int, int, int, int], int]

_tables_cache: Dict[int, Tuple[List[int], List[int], List[Optional[Tuple[int, ...]]]]] = {}


def _get_tables(size: int) -> Tuple[List[int], List[int], List[Optional[Tuple[int, ...]]]]:
    if size not in _tables_cache:
        n2 = size * size
        goal = Board.generate_goal(size).tiles
        goal_row: List[int] = [0] * n2
        goal_col: List[int] = [0] * n2
        dist: List[Optional[Tuple[int, ...]]] = [None] * n2
        for pos, tile in enumerate(goal):
            if tile == 0:
                continue
            row, col = divmod(pos, size)
            goal_row[tile] = row
            goal_col[tile] = col
            dist[tile] = tuple(
                abs(row - q // size) + abs(col - q % size)
                for q in range(n2)
            )
        _tables_cache[size] = (goal_row, goal_col, dist)
    return _tables_cache[size]


def manhattan_distance(board: Board) -> int:
    _, _, dist = _get_tables(board.size)
    return sum(dist[tile][pos] for pos, tile in enumerate(board.tiles) if tile)


def misplaced_tiles(board: Board) -> int:
    size = board.size
    goal_row, goal_col, _ = _get_tables(size)
    count = 0
    for pos, tile in enumerate(board.tiles):
        if tile and pos != goal_row[tile] * size + goal_col[tile]:
            count += 1
    return count


def linear_conflict(board: Board) -> int:
    size = board.size
    goal_row, goal_col, dist = _get_tables(size)
    tiles = board.tiles
    total = sum(dist[tile][pos] for pos, tile in enumerate(tiles) if tile)

    conflict = 0
    for row in range(size):
        line = []
        for col in range(size):
            tile = tiles[row * size + col]
            if tile and goal_row[tile] == row:
                line.append((col, goal_col[tile]))
        for i in range(len(line)):
            for j in range(i + 1, len(line)):
                if line[i][1] > line[j][1]:
                    conflict += 1

    for col in range(size):
        line = []
        for row in range(size):
            tile = tiles[row * size + col]
            if tile and goal_col[tile] == col:
                line.append((row, goal_row[tile]))
        for i in range(len(line)):
            for j in range(i + 1, len(line)):
                if line[i][1] > line[j][1]:
                    conflict += 1

    return total + 2 * conflict


def manhattan_child_h(size: int, tiles: Tuple[int, ...], tile: int,
                      old_pos: int, new_pos: int, parent_h: int) -> int:
    _, _, dist = _get_tables(size)
    return parent_h + dist[tile][new_pos] - dist[tile][old_pos]


def misplaced_child_h(size: int, tiles: Tuple[int, ...], tile: int,
                      old_pos: int, new_pos: int, parent_h: int) -> int:
    goal_row, goal_col, _ = _get_tables(size)
    goal = goal_row[tile] * size + goal_col[tile]
    return parent_h + (old_pos == goal) - (new_pos == goal)


def linear_conflict_child_h(size: int, tiles: Tuple[int, ...], tile: int,
                            old_pos: int, new_pos: int, parent_h: int) -> int:
    goal_row, goal_col, dist = _get_tables(size)
    old_r, old_c = divmod(old_pos, size)
    new_r, new_c = divmod(new_pos, size)
    h = parent_h + dist[tile][new_pos] - dist[tile][old_pos]
    conflicts = 0

    if old_r == new_r:
        # Horizontal move: row conflicts keep their order (blank is not a
        # tile), only the conflicts in the old and new column can change.
        if goal_col[tile] == old_c:
            for r in range(size):
                if r == old_r:
                    continue
                other = tiles[r * size + old_c]
                if other and goal_col[other] == old_c \
                        and (old_r < r) != (goal_row[tile] < goal_row[other]):
                    conflicts -= 1
        if goal_col[tile] == new_c:
            for r in range(size):
                if r == new_r:
                    continue
                other = tiles[r * size + new_c]
                if other and goal_col[other] == new_c \
                        and (new_r < r) != (goal_row[tile] < goal_row[other]):
                    conflicts += 1
    else:
        # Vertical move: column order is preserved, only the conflicts in
        # the old and new row can change.
        if goal_row[tile] == old_r:
            for c in range(size):
                if c == old_c:
                    continue
                other = tiles[old_r * size + c]
                if other and goal_row[other] == old_r \
                        and (old_c < c) != (goal_col[tile] < goal_col[other]):
                    conflicts -= 1
        if goal_row[tile] == new_r:
            for c in range(size):
                if c == new_c:
                    continue
                other = tiles[new_r * size + c]
                if other and goal_row[other] == new_r \
                        and (new_c < c) != (goal_col[tile] < goal_col[other]):
                    conflicts += 1

    return h + 2 * conflicts


HEURISTICS = {
    'manhattan': manhattan_distance,
    'misplaced': misplaced_tiles,
    'linear_conflict': linear_conflict,
}

CHILD_HEURISTICS = {
    manhattan_distance: manhattan_child_h,
    misplaced_tiles: misplaced_child_h,
    linear_conflict: linear_conflict_child_h,
}


def _make_full_recompute_child_h(
        heuristic_fn: Callable[[Board], int]) -> ChildH:
    def child_h(size: int, tiles: Tuple[int, ...], tile: int,
                old_pos: int, new_pos: int, parent_h: int) -> int:
        new_tiles = list(tiles)
        new_tiles[old_pos] = 0
        new_tiles[new_pos] = tile
        return heuristic_fn(Board(size, new_tiles))
    return child_h


def get_child_h_fn(heuristic_fn: Callable[[Board], int]) -> ChildH:
    child_h = CHILD_HEURISTICS.get(heuristic_fn)
    if child_h is None:
        return _make_full_recompute_child_h(heuristic_fn)
    return child_h
