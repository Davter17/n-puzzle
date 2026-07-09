import heapq
from typing import Callable, Dict, List, Optional, Set, Tuple

from src.board import Board
from src.heuristics import HEURISTICS


class Node:
    __slots__ = ('board', 'parent', 'g', 'h', 'f', 'move')

    def __init__(self, board: Board, parent: Optional['Node'] = None,
                 g: int = 0, h: int = 0, move: str = ''):
        self.board = board
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h
        self.move = move

    def __lt__(self, other: 'Node') -> bool:
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f


def reconstruct_path(node: Node) -> List[Board]:
    path = []
    current: Optional[Node] = node
    while current:
        path.append(current.board)
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
    goal = Board.generate_goal(initial_board.size)

    start_h = heuristic_fn(initial_board)
    start_node = Node(initial_board, g=0, h=start_h)

    if start_node.board == goal:
        return [initial_board], {
            'time_complexity': 1,
            'size_complexity': 1,
            'moves': 0,
        }

    open_set: List[Tuple[int, int, Node]] = []
    entry_counter = 0
    heapq.heappush(open_set, (start_node.f, entry_counter, start_node))
    entry_counter += 1

    closed_set: Set[Board] = set()
    g_scores: Dict[Board, int] = {initial_board: 0}

    max_open_size = 1
    total_opened = 0

    while open_set:
        max_open_size = max(max_open_size, len(open_set))

        _, _, current = heapq.heappop(open_set)
        total_opened += 1

        if current.board in closed_set:
            continue

        if current.board == goal:
            path = reconstruct_path(current)
            stats = {
                'time_complexity': total_opened,
                'size_complexity': max_open_size,
                'moves': len(path) - 1,
            }
            return path, stats

        closed_set.add(current.board)

        for neighbor in current.board.get_neighbors():
            if neighbor in closed_set:
                continue

            if algorithm == 'greedy':
                new_g = current.g + 1
                new_h = heuristic_fn(neighbor)
                if neighbor not in g_scores or new_g < g_scores[neighbor]:
                    g_scores[neighbor] = new_g
                    node = Node(neighbor, current, g=new_g, h=new_h)
                    heapq.heappush(open_set, (new_h, entry_counter, node))
                    entry_counter += 1
            elif algorithm == 'uniform_cost':
                new_g = current.g + 1
                if neighbor not in g_scores or new_g < g_scores[neighbor]:
                    g_scores[neighbor] = new_g
                    node = Node(neighbor, current, g=new_g, h=0)
                    heapq.heappush(open_set, (new_g, entry_counter, node))
                    entry_counter += 1
            else:
                tentative_g = current.g + 1
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    h = heuristic_fn(neighbor)
                    node = Node(neighbor, current, g=tentative_g, h=h)
                    heapq.heappush(open_set, (node.f, entry_counter, node))
                    entry_counter += 1

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
