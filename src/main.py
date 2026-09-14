import argparse
import sys
import time

from src.generator import generate_puzzle, is_solvable, MAX_SIZE
from src.heuristics import HEURISTICS
from src.parser import parse_input, PuzzleError
from src.solver import SearchLimitReached, print_solution, solve


def main():
    # Punto de entrada del programa: parsea argumentos, carga/genera puzzle y resuelve
    parser = argparse.ArgumentParser(description='N-Puzzle solver using A*')
    group = parser.add_mutually_exclusive_group(required=True)  # -f y -g son excluyentes, uno es obligatorio
    group.add_argument('-f', '--file', type=str, help='Input file with puzzle')
    group.add_argument('-g', '--generate', type=int,
                       help='Generate random puzzle of given size (1-20)')

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
    parser.add_argument('-w', '--weight', type=float, default=1.0,
                        help='A* weight (f = g + w*h). 1.0 = optimal, >1 = faster')
    parser.add_argument('-i', '--iterations', type=int, default=0,
                        help='Random walks from the goal when using -g (0 = auto)')
    parser.add_argument('--max-nodes', type=int, default=0,
                        help='Abort after N opened states (0 = no limit)')

    args = parser.parse_args()  # parse_args: lee los argumentos de línea de comandos

    if args.generate is not None:
        if args.generate < 1:
            print(f"Error: Size must be at least 1, got {args.generate}", file=sys.stderr)
            sys.exit(1)  # sys.exit(1): termina el programa con código de error
        if args.generate > MAX_SIZE:
            print(f"Error: Size too large: {args.generate} (max is {MAX_SIZE})", file=sys.stderr)
            sys.exit(1)

    if args.weight <= 0:
        print(f"Error: Weight must be positive, got {args.weight}", file=sys.stderr)
        sys.exit(1)

    if args.iterations < 0:
        print(f"Error: Iterations must be >= 0, got {args.iterations}", file=sys.stderr)
        sys.exit(1)

    if args.max_nodes < 0:
        print(f"Error: max-nodes must be >= 0, got {args.max_nodes}", file=sys.stderr)
        sys.exit(1)

    quiet = args.stats_only

    # Carga el puzzle desde archivo o lo genera aleatoriamente
    if args.file:
        try:
            board = parse_input(args.file)
        except PuzzleError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        if not quiet:
            print(f"Puzzle loaded from '{args.file}' (size={board.size}):")
    else:
        board = generate_puzzle(args.generate, args.iterations)
        if not quiet:
            print(f"Generated random {board.size}-puzzle:")

    if not quiet:
        print()
        print(board.display())
        print()

    # Comprueba si el puzzle es solucionable
    if not is_solvable(board):
        print("This puzzle is UNSOLVABLE!")
        sys.exit(1)

    if args.solvable:
        print("This puzzle is solvable.")
        return

    if not quiet:
        print(f"Using heuristic: {args.heuristic}")
        print(f"Using algorithm: {args.algorithm}")
        if args.algorithm == 'a_star' and args.weight != 1.0:
            print(f"Using weight: {args.weight}")
        print("Solving...")

    heuristic_fn = HEURISTICS[args.heuristic]

    start = time.time()  # time.time(): marca el tiempo de inicio
    try:
        result = solve(board, heuristic_fn, algorithm=args.algorithm,
                       weight=args.weight, max_nodes=args.max_nodes)
    except SearchLimitReached as e:
        print(f"Error: aborted after {e.opened} opened states.", file=sys.stderr)
        print("Hint: retry with -w 1.5, -a greedy, or a higher --max-nodes.",
              file=sys.stderr)
        sys.exit(1)
    elapsed = time.time() - start  # tiempo transcurrido

    if result is None:
        print("No solution found (this should not happen for solvable puzzles!)",
              file=sys.stderr)
        sys.exit(1)

    path, stats = result
    if quiet:
        # Modo estadísticas: solo muestra números, sin tableros
        print(f"[{args.heuristic:<16s}] moves={stats['moves']:<4d} "
              f"opened={stats['time_complexity']:<8d} "
              f"memory={stats['size_complexity']:<8d} "
              f"time={elapsed:.3f}s")
    else:
        print_solution(path, stats)
        print(f"Elapsed time: {elapsed:.3f}s")


if __name__ == '__main__':
    main()
