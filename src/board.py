import copy
from typing import List, Tuple, Optional


class Board:
    def __init__(self, size: int, tiles: Optional[List[int]] = None):
        self.size = size
        if tiles:
            self.tiles = tuple(tiles)
        else:
            self.tiles = tuple(range(size * size))
        self._hash = hash((self.size, self.tiles))
        try:
            self._blank_pos = self.tiles.index(0)
        except ValueError:
            raise ValueError("Board must contain a 0 (blank tile)")

    @property
    def blank_pos(self) -> int:
        return self._blank_pos

    @property
    def row(self) -> int:
        return self._blank_pos // self.size

    @property
    def col(self) -> int:
        return self._blank_pos % self.size

    def __getitem__(self, idx: int) -> int:
        return self.tiles[idx]

    def __eq__(self, other) -> bool:
        if not isinstance(other, Board):
            return False
        return self.size == other.size and self.tiles == other.tiles

    def __hash__(self) -> int:
        return self._hash

    def __len__(self) -> int:
        return len(self.tiles)

    def get_neighbors(self) -> List['Board']:
        neighbors = []
        pos = self._blank_pos
        n = self.size

        if pos >= n:
            neighbors.append(self._swap(pos, pos - n))
        if pos < n * n - n:
            neighbors.append(self._swap(pos, pos + n))
        if pos % n != 0:
            neighbors.append(self._swap(pos, pos - 1))
        if pos % n != n - 1:
            neighbors.append(self._swap(pos, pos + 1))

        return neighbors

    def _swap(self, i: int, j: int) -> 'Board':
        tiles = list(self.tiles)
        tiles[i], tiles[j] = tiles[j], tiles[i]
        return Board(self.size, tiles)

    @staticmethod
    def generate_goal(size: int) -> 'Board':
        n = size
        tiles = [0] * (n * n)
        val = 1
        top, bottom = 0, n - 1
        left, right = 0, n - 1

        while top <= bottom and left <= right:
            for col in range(left, right + 1):
                tiles[top * n + col] = val
                val += 1
            top += 1
            for row in range(top, bottom + 1):
                tiles[row * n + right] = val
                val += 1
            right -= 1
            if top <= bottom:
                for col in range(right, left - 1, -1):
                    tiles[bottom * n + col] = val
                    val += 1
                bottom -= 1
            if left <= right:
                for row in range(bottom, top - 1, -1):
                    tiles[row * n + left] = val
                    val += 1
                left += 1

        tiles[tiles.index(n * n)] = 0
        return Board(size, tiles)

    def display(self) -> str:
        lines = []
        for i in range(self.size):
            row_tiles = self.tiles[i * self.size:(i + 1) * self.size]
            lines.append(' '.join(f'{t:2d}' for t in row_tiles))
        return '\n'.join(lines)

    def __repr__(self) -> str:
        return f"Board(size={self.size})"
