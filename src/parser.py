import os
from src.board import Board


class PuzzleError(Exception):
    pass


MAX_SIZE = 20


def parse_input(filename: str) -> Board:
    # Lee un archivo de texto y lo convierte en un tablero, con validación completa
    if not os.path.exists(filename):
        raise PuzzleError(f"File not found: '{filename}'")
    if os.path.isdir(filename):
        raise PuzzleError(f"'{filename}' is a directory, not a file")
    if not os.path.isfile(filename):
        raise PuzzleError(f"'{filename}' is not a regular file")
    if not os.access(filename, os.R_OK):  # os.access: comprueba permisos de lectura
        raise PuzzleError(f"No read permission for '{filename}'")

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except PermissionError:
        raise PuzzleError(f"Permission denied: '{filename}'")
    except IOError as e:
        raise PuzzleError(f"Cannot read file '{filename}': {e}")

    # Elimina comentarios (todo lo que va después de #) y líneas vacías
    clean_lines = []
    for line in lines:
        comment_pos = line.find('#')  # find: devuelve posición del primer '#' (-1 si no existe)
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

    # Extrae todos los números de las líneas de fichas
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

    # Valida que no haya duplicados, valores fuera de rango o valores faltantes
    expected_set = set(range(expected))
    actual_set = set(tiles)

    if len(actual_set) != len(tiles):
        duplicates = [n for n in actual_set
                      if tiles.count(n) > 1]
        raise PuzzleError(f"Duplicate tile values found: {duplicates}")

    out_of_range = actual_set - expected_set  # diferencia de sets: valores en actual_set pero no en expected_set
    if out_of_range:
        raise PuzzleError(
            f"Tile values out of range [0, {expected - 1}]: "
            f"{sorted(out_of_range)}"
        )

    missing = expected_set - actual_set  # valores que deberían estar pero no están
    if missing:
        raise PuzzleError(f"Missing tile values: {sorted(missing)}")

    return Board(size, tiles)
