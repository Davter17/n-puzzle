from typing import Optional

from src.board import Board


def parse_input(filename: str) -> Optional[Board]:
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except (FileNotFoundError, IOError):
        return None

    clean_lines = []
    for line in lines:
        comment_pos = line.find('#')
        if comment_pos != -1:
            line = line[:comment_pos]
        line = line.strip()
        if line:
            clean_lines.append(line)

    if not clean_lines:
        return None

    try:
        size = int(clean_lines[0])
    except (ValueError, IndexError):
        return None

    tiles = []
    for line in clean_lines[1:]:
        for token in line.split():
            if token.startswith('#'):
                break
            try:
                tiles.append(int(token))
            except ValueError:
                continue

    expected = size * size
    if len(tiles) != expected:
        return None

    return Board(size, tiles)
