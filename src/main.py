import argparse
import sys
import time

from src.board import Board
from src.generator import generate_puzzle, is_solvable, MAX_SIZE
from src.heuristics import HEURISTICS
from src.parser import parse_input, PuzzleError
from src.solver import solve, print_solution


def main():
    parser = argparse.ArgumentParser(description='N-Puzzle solver using A*')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', type=str, help='Input file with puzzle')
    group.add_argument('-g', '--generate', type=int, help='Generate random puzzle of given size (3-20)')

    parser.add_argument('-H', '--heuristic', type=str, default='linear_conflict',
                        choices=list(HEURISTICS.keys()),
                        help='Heuristic function to use')
    parser.add_argument('-a', '--algorithm', type=str, default='a_star',
                        choices=['a_star', 'uniform_cost', 'greedy'],
                        help='Search algorithm to use')
    parser.add_argument('-s', '--solvable', action='store_true',
                        help='Only check if the puzzle is solvable')
    parser.add_argument('-q', '--stats-only', action='store_true',
                        help='Print only statistics (no boards or solution path)')

    args = parser.parse_args()

    if args.generate is not None:
        if args.generate < 1:
            print(f"Error: Size must be at least 1, got {args.generate}", file=sys.stderr)
            sys.exit(1)
        if args.generate > MAX_SIZE:
            print(f"Error: Size too large: {args.generate} (max is {MAX_SIZE})", file=sys.stderr)
            sys.exit(1)

    quiet = args.stats_only

    if args.file:
        try:
            board = parse_input(args.file)
        except PuzzleError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        if not quiet:
            print(f"Puzzle loaded from '{args.file}' (size={board.size}):")
    else:
        board = generate_puzzle(args.generate)
        if not quiet:
            print(f"Generated random {board.size}-puzzle:")

    if not quiet:
        print()
        print(board.display())
        print()

    if not is_solvable(board):
        print("This puzzle is UNSOLVABLE!")
        return

    if args.solvable:
        print("This puzzle is solvable.")
        return

    if not quiet:
        print(f"Using heuristic: {args.heuristic}")
        print(f"Using algorithm: {args.algorithm}")
        print("Solving...")

    heuristic_fn = HEURISTICS[args.heuristic]

    start = time.time()
    result = solve(board, heuristic_fn, algorithm=args.algorithm)
    elapsed = time.time() - start

    if result is None:
        print("No solution found (this should not happen for solvable puzzles!)",
              file=sys.stderr)
        sys.exit(1)

    path, stats = result
    if quiet:
        print(f"[{args.heuristic:<16s}] moves={stats['moves']:<4d} "
              f"opened={stats['time_complexity']:<8d} "
              f"memory={stats['size_complexity']:<8d} "
              f"time={elapsed:.3f}s")
    else:
        print_solution(path, stats)
        print(f"Elapsed time: {elapsed:.3f}s")


if __name__ == '__main__':
    main()
