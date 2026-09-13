import os
from src.board import Board


class PuzzleError(Exception):
    pass


MAX_SIZE = 20


def parse_input(filename: str) -> Board:
    if not os.path.exists(filename):
        raise PuzzleError(f"File not found: '{filename}'")
    if os.path.isdir(filename):
        raise PuzzleError(f"'{filename}' is a directory, not a file")
    if not os.path.isfile(filename):
        raise PuzzleError(f"'{filename}' is not a regular file")
    if not os.access(filename, os.R_OK):
        raise PuzzleError(f"No read permission for '{filename}'")

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except PermissionError:
        raise PuzzleError(f"Permission denied: '{filename}'")
    except IOError as e:
        raise PuzzleError(f"Cannot read file '{filename}': {e}")

    clean_lines = []
    for line in lines:
        comment_pos = line.find('#')
        if comment_pos != -1:
            line = line[:comment_pos]
        line = line.strip()
        if line:
            clean_lines.append(line)

    if not clean_lines:
        raise PuzzleError(f"File '{filename}' is empty or contains only comments")

    try:
        size = int(clean_lines[0])
    except ValueError:
        raise PuzzleError(f"Invalid puzzle size: '{clean_lines[0]}' is not a number")

    if size < 1:
        raise PuzzleError(f"Puzzle size must be at least 1, got {size}")
    if size > MAX_SIZE:
        raise PuzzleError(f"Puzzle size too large: {size} (max is {MAX_SIZE})")

    data_lines = clean_lines[1:]
    if len(data_lines) < size:
        raise PuzzleError(
            f"Expected at least {size} lines of tiles for a {size}-puzzle, "
            f"but got {len(data_lines)}"
        )

    tiles = []
    for line_num, line in enumerate(data_lines, start=2):
        for token in line.split():
            if token.startswith('#'):
                break
            try:
                tiles.append(int(token))
            except ValueError:
                raise PuzzleError(
                    f"Invalid token '{token}' on line {line_num}"
                )

    expected = size * size
    if len(tiles) != expected:
        raise PuzzleError(
            f"Expected {expected} tiles for a {size}-puzzle, "
            f"but got {len(tiles)}"
        )

    expected_set = set(range(expected))
    actual_set = set(tiles)

    if len(actual_set) != len(tiles):
        duplicates = [n for n in actual_set
                      if tiles.count(n) > 1]
        raise PuzzleError(f"Duplicate tile values found: {duplicates}")

    out_of_range = actual_set - expected_set
    if out_of_range:
        raise PuzzleError(
            f"Tile values out of range [0, {expected - 1}]: "
            f"{sorted(out_of_range)}"
        )

    missing = expected_set - actual_set
    if missing:
        raise PuzzleError(f"Missing tile values: {sorted(missing)}")

    return Board(size, tiles)
