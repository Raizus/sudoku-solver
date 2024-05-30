from typing import Any
import re


class GridCoords:
    _r: int | float
    _c: int | float

    def __init__(self, r: int | float, c: int | float) -> None:
        self._r = r
        self._c = c

    def __eq__(self, other: Any) -> bool:
        if type(other) is type(self):
            return self.r == other.r and self.c == other.c
        return False

    def __hash__(self) -> int:
        return hash((self.r, self.c))

    def __repr__(self) -> str:
        return str(self.toTuple())

    @property
    def r(self):
        return self._r

    @property
    def c(self):
        return self._c

    def __add__(self, other: 'GridCoords') -> 'GridCoords':
        return GridCoords(self.r + other.r, self.c + other.c)

    def __sub__(self, other: 'GridCoords') -> 'GridCoords':
        return GridCoords(self.r - other.r, self.c - other.c)

    def __mul__(self, other: int | float) -> 'GridCoords':
        return GridCoords(other * self.r, other * self.c)

    def __rmul__(self, other: int | float) -> 'GridCoords':
        return self.__mul__(other)

    # def norm(self) -> int | float:
    #     return self.r*self.r + self.c*self.c

    def toTuple(self) -> tuple[int | float, int | float]:
        return (self.r, self.c)

    def isOrthogonallyAdjacent(self, other: 'GridCoords') -> bool:
        dc = abs(self.c - other.c)
        dr = abs(self.r - other.r)

        return dr <= 1 and dc <= 1 and dr != dc

    def isDiagonallyAdjacent(self, other: 'GridCoords') -> bool:
        dc = abs(self.c - other.c)
        dr = abs(self.r - other.r)

        return dr == dc == 1

    def isNeighbour(self, other: 'GridCoords') -> bool:
        dc = abs(self.c - other.c)
        dr = abs(self.r - other.r)

        return dr <= 1 and dc <= 1 and dr+dc > 0

    def toCornerCoords(self, corner_idx: int) -> 'GridCoords':
        """
           0 -> •------• <- 1
                |      |
                |      |
           3 -> •------• <- 2

        Args:
            corner_idx (int): 

        Raises:
            Exception: 

        Returns:
            GridCoords: 
        """
        if not (self.r % 1 == 0 and self.c % 1 == 0):
            raise Exception(
                'To convert to corner coords r and c must be integers')

        if corner_idx % 4 == 0:
            r, c = int(self.r), int(self.c)
        elif corner_idx % 4 == 1:
            r, c = int(self.r), int(self.c+1)
        elif corner_idx % 4 == 2:
            r, c = int(self.r+1), int(self.c+1)
        else:
            r, c = int(self.r+1), int(self.c)
        corner = GridCoords(r, c)
        return corner

    @classmethod
    def fromString(cls, string: str) -> "GridCoords":
        def parse_int_or_float(string: str) -> int | float:
            try:
                res = int(string)
            except ValueError:
                res = float(string)
            return res

        int_or_float = r"([-+]?[0-9]+\.?[0-9]*)"
        result = re.search(f"R{int_or_float}C{int_or_float}", string)
        if not result or not len(result.groups()) == 2:
            raise ValueError(
                'Cell id must have formate RxCy, where x and y are integers or floats')
        groups = result.groups()
        row = parse_int_or_float(groups[0]) - 1
        col = parse_int_or_float(groups[1]) - 1
        coords = GridCoords(row, col)

        return coords


def coordToCellString(coord: GridCoords):
    res = f"R{coord.r+1}C{coord.c+1}"
    return res


def areBorderingCoords(coords: list[GridCoords]) -> bool:
    if len(coords) != 2:
        return False

    return coords[0].isOrthogonallyAdjacent(coords[1])


def areNeighbouringCoords(coords: list[GridCoords]) -> bool:
    if len(coords) != 2:
        return False

    return coords[0].isNeighbour(coords[1])


def areCornerCoords(coords: list[GridCoords]) -> bool:
    if len(set(coords)) != 4:
        return False

    coords = sortCoords(coords)
    is_corner = (coords[0] + GridCoords(0, 1) == coords[1]
                 ) and (coords[0] + GridCoords(1, 0) == coords[2]) and (coords[0] + GridCoords(1, 1) == coords[3])

    return is_corner


def areCoordsLine(coords: list[GridCoords], allow_intersection: bool) -> bool:
    if not allow_intersection and len(coords) != len(set(coords)):
        return False
    for i, coord in enumerate(coords[1:], 1):
        prev_coord = coords[i-1]
        if not coord.isNeighbour(prev_coord):
            return False
        if i >= 2:
            prev_coord2 = coords[i-2]
            if coord == prev_coord2:
                return False
    return True


def areCoordsCage(coords: list[GridCoords], allow_diagonals: bool = True) -> bool:
    coords2 = set(coords)
    n = len(coords2)
    if len(coords) == 0 and len(coords) != n:
        return False

    visited = set([coords[0]])
    coords2.remove(coords[0])

    while True:
        adj: list[GridCoords] = []
        for coord in coords2:
            if allow_diagonals and any(coord.isNeighbour(coord2) for coord2 in visited):
                adj.append(coord)
            elif not allow_diagonals and any(coord.isOrthogonallyAdjacent(coord2) for coord2 in visited):
                adj.append(coord)
        visited.update(adj)
        coords2.difference_update(adj)
        if len(adj) == 0:
            break

    return len(visited) == n


def sortCoords(coords: list[GridCoords]):
    coords.sort(key=lambda x: x.c)
    coords.sort(key=lambda x: x.r)

    return coords


if __name__ == "__main__":
    c1 = GridCoords(4, 3)
    c2 = GridCoords(4, 3)
    c3 = GridCoords(4, 4)

    print(c1 == c2)
    print(len(set([c1, c2])))
    print(areBorderingCoords([c1, c3]))
