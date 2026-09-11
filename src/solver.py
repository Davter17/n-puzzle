import heapq
from typing import Callable, Dict, List, Optional, Tuple

from src.board import Board
from src.heuristics import get_child_h_fn

_INF = 1 << 60


class Node:
    __slots__ = ('tiles', 'blank', 'parent', 'g', 'h', 'move')

    def __init__(self, tiles: Tuple[int, ...], blank: int,
                 parent: Optional['Node'] = None, g: int = 0,
                 h: int = 0, move: str = ''):
        self.tiles = tiles
        self.blank = blank
        self.parent = parent
        self.g = g
        self.h = h
        self.move = move


def _neighbor_positions(blank: int, size: int, total: int) -> List[int]:
    positions = []
    if blank >= size:
        positions.append(blank - size)
    if blank < total - size:
        positions.append(blank + size)
    if blank % size:
        positions.append(blank - 1)
    if blank % size != size - 1:
        positions.append(blank + 1)
    return positions


def reconstruct_path(node: Node, size: int) -> List[Board]:
    path = []
    current: Optional[Node] = node
    while current:
        path.append(Board(size, list(current.tiles)))
        current = current.parent
    path.reverse()
    return path


def reconstruct_moves(node: Node) -> List[str]:
    moves = []
    current: Optional[Node] = node
    while current and current.parent:
        moves.append(current.move)
        current = current.parent
    moves.reverse()
    return moves


def solve(initial_board: Board, heuristic_fn: Callable[[Board], int],
          algorithm: str = 'a_star') -> Optional[Tuple[List[Board], Dict]]:
    size = initial_board.size
    total = size * size
    goal_tiles = Board.generate_goal(size).tiles
    start_tiles = initial_board.tiles

    if start_tiles == goal_tiles:
        return [initial_board], {
            'time_complexity': 1,
            'size_complexity': 1,
            'moves': 0,
        }

    start_h = heuristic_fn(initial_board)
    child_h_fn = get_child_h_fn(heuristic_fn)

    start_node = Node(start_tiles, initial_board.blank_pos, None, 0, start_h)

    open_heap: List[Tuple[int, int, int, Node]] = []
    counter = 0
    heapq.heappush(open_heap, (start_h, start_h, counter, start_node))
    counter += 1

    # Best known g per state. Nodes are re-opened when a shorter path to an
    # already expanded state is found (needed because linear conflict is
    # admissible but not consistent).
    g_best: Dict[Tuple[int, ...], int] = {start_tiles: 0}

    max_open_size = 1
    total_opened = 0

    while open_heap:
        max_open_size = max(max_open_size, len(open_heap))

        _, _, _, current = heapq.heappop(open_heap)
        total_opened += 1

        tiles = current.tiles
        g = current.g
        if g > g_best[tiles]:
            continue  # stale entry: a shorter path to this state exists

        if tiles == goal_tiles:
            path = reconstruct_path(current, size)
            stats = {
                'time_complexity': total_opened,
                'size_complexity': max_open_size,
                'moves': len(path) - 1,
            }
            return path, stats

        blank = current.blank
        h = current.h
        new_g = g + 1

        for pos in _neighbor_positions(blank, size, total):
            tile = tiles[pos]
            if pos > blank:
                neighbor_tiles = (
                    tiles[:blank] + (tile,) + tiles[blank + 1:pos]
                    + (0,) + tiles[pos + 1:]
                )
            else:
                neighbor_tiles = (
                    tiles[:pos] + (0,) + tiles[pos + 1:blank]
                    + (tile,) + tiles[blank + 1:]
                )

            if new_g < g_best.get(neighbor_tiles, _INF):
                g_best[neighbor_tiles] = new_g

                if algorithm == 'uniform_cost':
                    child_h = 0
                else:
                    child_h = child_h_fn(size, tiles, tile, pos, blank, h)

                if algorithm == 'greedy':
                    priority = child_h
                elif algorithm == 'uniform_cost':
                    priority = new_g
                else:
                    priority = new_g + child_h

                if pos == blank - size:
                    move = 'up'
                elif pos == blank + size:
                    move = 'down'
                elif pos == blank - 1:
                    move = 'left'
                else:
                    move = 'right'

                child = Node(neighbor_tiles, pos, current, new_g, child_h, move)
                heapq.heappush(open_heap, (priority, child_h, counter, child))
                counter += 1

    return None


def print_solution(path: List[Board], stats: Dict):
    print(f"Solution found in {stats['moves']} moves:")
    for board in path:
        print()
        print(board.display())

    print()
    print(f"Time complexity (total opened states): {stats['time_complexity']}")
    print(f"Size complexity (max states in memory): {stats['size_complexity']}")
    print(f"Number of moves: {stats['moves']}")
