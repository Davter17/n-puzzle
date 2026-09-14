import os
import pickle
import sys
import time
from collections import deque
from typing import Dict, List, Tuple

from src.board import Board

_PDB_VERSION = 2
_UNVISITED = 255

_CACHE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 os.pardir, '.pdb_cache'))

_PDB_CACHE: Dict[int, Tuple[List[Tuple[int, ...]], List[bytearray], List[int]]] = {}


def _choose_k(size: int) -> int:
    if size <= 6:
        return 3
    if size <= 8:
        return 2
    return 1


def _cell_neighbors(size: int) -> List[Tuple[int, ...]]:
    n2 = size * size
    neighbors = []
    for pos in range(n2):
        row, col = divmod(pos, size)
        cells = []
        if row > 0:
            cells.append(pos - size)
        if row < size - 1:
            cells.append(pos + size)
        if col > 0:
            cells.append(pos - 1)
        if col < size - 1:
            cells.append(pos + 1)
        neighbors.append(tuple(cells))
    return neighbors


def _partition_tiles(size: int, k: int):
    goal = Board.generate_goal(size).tiles
    goal_pos = [0] * (size * size)
    for pos, tile in enumerate(goal):
        if tile != 0:
            goal_pos[tile] = pos
    tiles = [tile for tile in goal if tile != 0]
    groups = [tuple(tiles[i:i + k]) for i in range(0, len(tiles), k)]
    blank_goal = goal.index(0)
    return groups, goal_pos, blank_goal


def _build_group_table(size: int, group: Tuple[int, ...], goal_pos: List[int],
                       blank_goal: int, neighbors: List[Tuple[int, ...]]) -> bytearray:
    """Cost table for one tile group, found by 0-1 BFS from the goal.

    State = (positions of the group tiles, blank position), encoded in base
    n*n. Blank moves through non-group tiles cost 0, moves swapping the blank
    with a group tile cost 1. The stored value is the minimum number of
    group-tile moves needed to bring the group home.
    """
    n2 = size * size
    k = len(group)
    table = bytearray(b'\xff' * (n2 ** (k + 1)))

    goal_ps = tuple(goal_pos[t] for t in group)
    idx = blank_goal
    for p in goal_ps:
        idx = idx * n2 + p
    table[idx] = 0

    current: deque = deque([(goal_ps, blank_goal)])
    next_layer: deque = deque()
    layer = 0

    while current:
        ps, blank = current.popleft()
        for q in neighbors[blank]:
            idx = q
            for p in ps:
                idx = idx * n2 + p
            if q in ps:
                i = ps.index(q)
                nps = ps[:i] + (blank,) + ps[i + 1:]
                idx = q
                for p in nps:
                    idx = idx * n2 + p
                if table[idx] == _UNVISITED:
                    table[idx] = layer + 1
                    next_layer.append((nps, q))
            else:
                if table[idx] == _UNVISITED:
                    table[idx] = layer
                    current.append((ps, q))
        if not current:
            current = next_layer
            next_layer = deque()
            layer += 1

    return table


def _build_pdb(size: int):
    k = _choose_k(size)
    groups, goal_pos, blank_goal = _partition_tiles(size, k)
    if not groups:
        return groups, [], goal_pos
    neighbors = _cell_neighbors(size)
    tables = []
    for i, group in enumerate(groups):
        started = time.time()
        tables.append(
            _build_group_table(size, group, goal_pos, blank_goal, neighbors))
        print(f'  pattern database {i + 1}/{len(groups)} '
              f'({len(group)} tiles) built in {time.time() - started:.1f}s',
              file=sys.stderr)
    return groups, tables, goal_pos


def _get_pdb(size: int):
    if size in _PDB_CACHE:
        return _PDB_CACHE[size]
    os.makedirs(_CACHE_DIR, exist_ok=True)
    path = os.path.join(_CACHE_DIR, f'pdb_{size}_v{_PDB_VERSION}.pkl')
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            groups = [tuple(g) for g in data['groups']]
            tables = [bytearray(t) for t in data['tables']]
            goal_pos = list(data['goal_pos'])
            _PDB_CACHE[size] = (groups, tables, goal_pos)
            return _PDB_CACHE[size]
        except Exception:
            pass

    print(f'Building pattern databases for size {size} '
          f'(one-time cost, cached in .pdb_cache/)...', file=sys.stderr)
    started = time.time()
    groups, tables, goal_pos = _build_pdb(size)
    with open(path, 'wb') as f:
        pickle.dump({
            'groups': [list(g) for g in groups],
            'tables': [bytes(t) for t in tables],
            'goal_pos': list(goal_pos),
        }, f)
    print(f'Pattern databases ready in {time.time() - started:.1f}s',
          file=sys.stderr)
    _PDB_CACHE[size] = (groups, tables, goal_pos)
    return _PDB_CACHE[size]


def _group_manhattan(size: int, group: Tuple[int, ...],
                     goal_pos: List[int], pos: List[int]) -> int:
    total = 0
    for t in group:
        cur, goal = pos[t], goal_pos[t]
        total += abs(cur // size - goal // size) + abs(cur % size - goal % size)
    return total


def pdb_distance(board: Board) -> int:
    size = board.size
    n2 = size * size
    groups, tables, goal_pos = _get_pdb(size)
    pos = [0] * n2
    for i, tile in enumerate(board.tiles):
        pos[tile] = i
    blank = board.blank_pos
    total = 0
    for group, table in zip(groups, tables):
        idx = blank
        for t in group:
            idx = idx * n2 + pos[t]
        value = table[idx]
        if value == _UNVISITED:
            value = _group_manhattan(size, group, goal_pos, pos)
        total += value
    return total


def pdb_child_h(size: int, tiles: Tuple[int, ...], tile: int,
                old_pos: int, new_pos: int, parent_h: int) -> int:
    n2 = size * size
    groups, tables, goal_pos = _get_pdb(size)
    pos = [0] * n2
    for i, t in enumerate(tiles):
        pos[t] = i
    pos[tile] = new_pos
    blank = old_pos
    total = 0
    for group, table in zip(groups, tables):
        idx = blank
        for t in group:
            idx = idx * n2 + pos[t]
        value = table[idx]
        if value == _UNVISITED:
            value = _group_manhattan(size, group, goal_pos, pos)
        total += value
    return total
