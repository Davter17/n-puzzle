import time

from flask import Flask, render_template, request, jsonify

from engine.board import Board
from engine.solver import solve, SearchLimitReached
from engine.heuristics import HEURISTICS
from engine.generator import generate_puzzle, is_solvable

app = Flask(__name__)

MAX_NODES_BY_SIZE = {
    3: 0,
    4: 5_000_000,
    5: 2_000_000,
    6: 2_000_000,
}


def _precision_to_params(precision: int, size: int):
    if size <= 3:
        if precision <= 33:
            return 'a_star', 'linear_conflict', 1.0
        elif precision <= 66:
            return 'a_star', 'manhattan', 1.0
        else:
            return 'greedy', 'manhattan', 1.0
    elif size == 4:
        if precision <= 25:
            return 'a_star', 'linear_conflict', 1.0
        elif precision <= 50:
            return 'a_star', 'linear_conflict', 2.0
        elif precision <= 75:
            return 'a_star', 'manhattan', 3.0
        else:
            return 'greedy', 'manhattan', 1.0
    elif size == 5:
        if precision <= 20:
            return 'a_star', 'linear_conflict', 1.0
        elif precision <= 40:
            return 'a_star', 'linear_conflict', 2.0
        elif precision <= 60:
            return 'a_star', 'manhattan', 3.0
        elif precision <= 80:
            return 'a_star', 'manhattan', 6.0
        else:
            return 'greedy', 'manhattan', 1.0
    else:
        if precision <= 15:
            return 'a_star', 'linear_conflict', 3.0
        elif precision <= 30:
            return 'a_star', 'linear_conflict', 5.0
        elif precision <= 50:
            return 'a_star', 'manhattan', 8.0
        elif precision <= 70:
            return 'a_star', 'manhattan', 15.0
        elif precision <= 85:
            return 'a_star', 'manhattan', 25.0
        else:
            return 'greedy', 'manhattan', 1.0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/solve', methods=['POST'])
def api_solve():
    data = request.get_json()
    size = data.get('size', 3)
    tiles = data.get('tiles', [])
    precision = data.get('precision', 50)
    heuristic_name = data.get('heuristic', 'manhattan')

    if len(tiles) != size * size:
        return jsonify({'error': f'Expected {size * size} tiles, got {len(tiles)}'}), 400

    board = Board(size, tiles)

    if not is_solvable(board):
        return jsonify({'error': 'Puzzle is not solvable'}), 400

    if heuristic_name not in HEURISTICS:
        return jsonify({'error': f'Unknown heuristic: {heuristic_name}'}), 400

    algorithm, _, weight = _precision_to_params(precision, size)
    heuristic_fn = HEURISTICS[heuristic_name]
    max_nodes = MAX_NODES_BY_SIZE.get(size, 100_000)

    start = time.time()
    try:
        result = solve(board, heuristic_fn, algorithm=algorithm,
                       weight=weight, max_nodes=max_nodes)
    except SearchLimitReached as e:
        elapsed = time.time() - start
        return jsonify({
            'error': f'Search aborted after {e.opened} states ({elapsed:.1f}s). '
                     f'Try sliding towards more speed (right).',
        }), 408

    elapsed = time.time() - start

    if result is None:
        return jsonify({'error': 'No solution found'}), 500

    path, moves, stats = result

    path_tiles = [list(b.tiles) for b in path]

    return jsonify({
        'path': path_tiles,
        'moves': moves,
        'stats': stats,
        'time': round(elapsed, 3),
        'algorithm': algorithm,
        'heuristic': heuristic_name,
    })


@app.route('/api/randomize', methods=['POST'])
def api_randomize():
    data = request.get_json()
    size = data.get('size', 3)
    iterations = data.get('iterations', 0)

    try:
        board = generate_puzzle(size, iterations)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({
        'tiles': list(board.tiles),
        'size': size,
    })


@app.route('/api/solvable', methods=['POST'])
def api_solvable():
    data = request.get_json()
    size = data.get('size', 3)
    tiles = data.get('tiles', [])

    if len(tiles) != size * size:
        return jsonify({'error': f'Expected {size * size} tiles'}), 400

    board = Board(size, tiles)
    return jsonify({'solvable': is_solvable(board)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
