import random
import unittest
from src.board import Board
from src.generator import is_solvable, generate_puzzle, _invariant
from src.heuristics import manhattan_distance, misplaced_tiles, linear_conflict, HEURISTICS, get_child_h_fn
from src.parser import parse_input, PuzzleError
from src.solver import solve


class TestBoard(unittest.TestCase):
    def test_goal_3(self):
        goal = Board.generate_goal(3)
        expected = (1, 2, 3, 8, 0, 4, 7, 6, 5)
        self.assertEqual(goal.tiles, expected)

    def test_goal_4(self):
        goal = Board.generate_goal(4)
        expected = (1, 2, 3, 4, 12, 13, 14, 5, 11, 0, 15, 6, 10, 9, 8, 7)
        self.assertEqual(goal.tiles, expected)

    def test_neighbors_3(self):
        board = Board(3, [1, 2, 3, 4, 0, 5, 6, 7, 8])
        neighbors = board.get_neighbors()
        self.assertEqual(len(neighbors), 4)

    def test_goal_blank_position_3(self):
        goal = Board.generate_goal(3)
        self.assertEqual(goal.row, 1)
        self.assertEqual(goal.col, 1)

    def test_equality(self):
        a = Board(3, [1, 2, 3, 8, 0, 4, 7, 6, 5])
        b = Board(3, [1, 2, 3, 8, 0, 4, 7, 6, 5])
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_set_membership(self):
        a = Board(3, [1, 2, 3, 8, 0, 4, 7, 6, 5])
        b = Board(3, [1, 2, 3, 8, 0, 4, 7, 6, 5])
        s = {a}
        self.assertIn(b, s)


class TestSolvability(unittest.TestCase):
    def test_goal_is_solvable(self):
        goal = Board.generate_goal(3)
        self.assertTrue(is_solvable(goal))

    def test_random_boards(self):
        for _ in range(20):
            board = generate_puzzle(3)
            self.assertTrue(is_solvable(board))

    def test_unsolvable_subject_example(self):
        board = Board(3, [3, 2, 6, 1, 4, 0, 8, 7, 5])
        self.assertTrue(is_solvable(board))

    def test_solvable_boards_are_really_solvable(self):
        for _ in range(10):
            board = generate_puzzle(3)
            goal = Board.generate_goal(3)
            result = solve(board, manhattan_distance)
            self.assertIsNotNone(result)
            path, stats = result
            self.assertEqual(path[-1], goal)
            self.assertEqual(len(path) - 1, stats['moves'])

    def test_invariant_consistency(self):
        goal = Board.generate_goal(4)
        inv_goal = _invariant(goal)
        for _ in range(10):
            board = generate_puzzle(4)
            self.assertEqual(_invariant(board), inv_goal)


class TestHeuristics(unittest.TestCase):
    def test_goal_manhattan_zero(self):
        goal = Board.generate_goal(3)
        self.assertEqual(manhattan_distance(goal), 0)

    def test_goal_misplaced_zero(self):
        goal = Board.generate_goal(3)
        self.assertEqual(misplaced_tiles(goal), 0)

    def test_goal_linear_conflict_zero(self):
        goal = Board.generate_goal(3)
        self.assertEqual(linear_conflict(goal), 0)

    def test_manhattan_one_move(self):
        goal = Board.generate_goal(3)
        board = Board(3, [1, 2, 3, 8, 4, 0, 7, 6, 5])
        self.assertEqual(manhattan_distance(board), 1)

    def test_all_heuristics_registered(self):
        self.assertIn('manhattan', HEURISTICS)
        self.assertIn('misplaced', HEURISTICS)
        self.assertIn('linear_conflict', HEURISTICS)

    def test_admissible(self):
        board = generate_puzzle(3)
        result_a_star = solve(board, manhattan_distance)
        self.assertIsNotNone(result_a_star)
        _, stats_a_star = result_a_star
        optimal_moves = stats_a_star['moves']

        for name, h in HEURISTICS.items():
            result = solve(board, h)
            self.assertIsNotNone(result,
                                 f"Heuristic {name} did not find solution")
            _, stats = result
            self.assertLessEqual(stats['moves'], optimal_moves + optimal_moves,
                                 f"Heuristic {name} path is suspiciously long")


class TestIncrementalHeuristics(unittest.TestCase):
    def _neighbor_positions(self, board):
        pos = board.blank_pos
        n = board.size
        positions = []
        if pos >= n:
            positions.append(pos - n)
        if pos < n * n - n:
            positions.append(pos + n)
        if pos % n:
            positions.append(pos - 1)
        if pos % n != n - 1:
            positions.append(pos + 1)
        return positions

    def test_incremental_matches_full_heuristic(self):
        for size in (3, 4):
            for name, h_fn in HEURISTICS.items():
                child_h_fn = get_child_h_fn(h_fn)
                rng = random.Random(1000 + size)
                board = Board.generate_goal(size)
                h = h_fn(board)
                for _ in range(300):
                    blank = board.blank_pos
                    pos = rng.choice(self._neighbor_positions(board))
                    tile = board.tiles[pos]
                    new_h = child_h_fn(size, board.tiles, tile, pos, blank, h)
                    tiles = list(board.tiles)
                    tiles[blank] = tile
                    tiles[pos] = 0
                    board = Board(size, tiles)
                    h = new_h
                    self.assertEqual(
                        h, h_fn(board),
                        f"Incremental {name} diverged on size {size}")


class TestParser(unittest.TestCase):
    def test_parse_basic(self):
        board = parse_input('puzzles/3x3.txt')
        self.assertIsNotNone(board)
        self.assertEqual(board.size, 3)

    def test_parse_nonexistent(self):
        with self.assertRaises(PuzzleError):
            parse_input('nonexistent_file.txt')


class TestSolver(unittest.TestCase):
    def test_solve_already_solved(self):
        goal = Board.generate_goal(3)
        result = solve(goal, manhattan_distance)
        self.assertIsNotNone(result)
        path, stats = result
        self.assertEqual(stats['moves'], 0)

    def test_unsolvable_returns_none(self):
        goal = Board.generate_goal(3)
        std_goal = Board(3, [1, 2, 3, 4, 5, 6, 7, 8, 0])
        if not is_solvable(std_goal):
            result = solve(std_goal, manhattan_distance)
            self.assertIsNone(result)

    def test_greedy_finds_solution(self):
        board = Board(3, [7, 8, 1, 3, 0, 6, 4, 2, 5])
        if is_solvable(board):
            result = solve(board, manhattan_distance, algorithm='greedy')
            self.assertIsNotNone(result)

    def test_uniform_cost_finds_solution(self):
        board = Board(3, [7, 8, 1, 3, 0, 6, 4, 2, 5])
        if is_solvable(board):
            result = solve(board, manhattan_distance, algorithm='uniform_cost')
            self.assertIsNotNone(result)

    def test_solve_4x4_linear_conflict_optimal(self):
        board = parse_input('puzzles/4x4.txt')
        result = solve(board, linear_conflict)
        self.assertIsNotNone(result)
        path, stats = result
        self.assertEqual(stats['moves'], 51)
        self.assertEqual(path[-1], Board.generate_goal(4))


if __name__ == '__main__':
    unittest.main()
