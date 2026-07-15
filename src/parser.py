from src.board import Board


class PuzzleError(Exception):
    pass


def parse_input(filename: str) -> Board:
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except PermissionError:
        raise PuzzleError(f"Permission denied: '{filename}'")
    except FileNotFoundError:
        raise PuzzleError(f"File not found: '{filename}'")
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

    if size < 2:
        raise PuzzleError(f"Puzzle size must be at least 2, got {size}")

    tiles = []
    for line_num, line in enumerate(clean_lines[1:], start=2):
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

    missing = expected_set - actual_set
    if missing:
        raise PuzzleError(f"Missing tile values: {sorted(missing)}")

    out_of_range = actual_set - expected_set
    if out_of_range:
        raise PuzzleError(
            f"Tile values out of range [0, {expected - 1}]: "
            f"{sorted(out_of_range)}"
        )

    return Board(size, tiles)
