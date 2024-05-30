from math import floor
from typing import Union

grid_sizes = {3:  {'w': 3, 'h': 1},
              4:  {'w': 2, 'h': 2},
              5:  {'w': 5, 'h': 1},
              6:  {'w': 3, 'h': 2},
              7:  {'w': 7, 'h': 1},
              8:  {'w': 4, 'h': 2},
              9:  {'w': 3, 'h': 3},
              10: {'w': 5, 'h': 2},
              11: {'w': 11, 'h': 1},
              12: {'w': 4, 'h': 3},
              13: {'w': 13, 'h': 1},
              14: {'w': 7, 'h': 2},
              15: {'w': 5, 'h': 3},
              16: {'w': 4, 'h': 4},
              }


def get_region_size(size: int):
    region_size = grid_sizes.get(size, None)
    if region_size:
        return region_size['w'], region_size['h']
    return None


def get_region_index(row: int, col: int, size: int) -> Union[int, None]:
    region_dims = get_region_size(size)
    if region_dims is None:
        return region_dims

    region_w, region_h = region_dims
    return (floor(row / region_h) * region_h) + floor(col / region_w)


class Cell:
    value: Union[int, None] = None
    row: int
    col: int
    region: Union[int, None] = None
    given: bool
    outside: bool
    highlight: list[int] = []
    disabled: bool = False

    def __init__(self, row: int, col: int, size: int | None = None, value: int | None = None, outside: bool = False):
        self.row = row
        self.col = col
        self.value = value
        self.value_backup = None
        self.region = None if outside or size is None else get_region_index(
            row, col, size)
        self.outside = outside
        self.given = False

    def __repr__(self):
        string = f"<Cell>: {self.format_cell()}: {self.value if self.value is not None else ''}"
        return string

    def format_cell(self):
        """Turns a cell into 'RxCy' string format"""
        return f"R{self.row + 1}C{self.col + 1}"


def sortCells(cells: list[Cell]):
    new_list = sorted(cells, key=lambda cell: cell.col)
    new_list = sorted(new_list, key=lambda cell: cell.row)
    return new_list


def are_cells_orthogonally_connected(cell1: Cell, cell2: Cell) -> bool:
    dr = abs(cell1.row - cell2.row)
    dc = abs(cell1.col - cell2.col)

    return dr <= 1 and dc <= 1 and dr != dc


def split_line_into_regions(line: list[Cell]) -> list[list[Cell]]:
    regions: list[list[Cell]] = []
    if not len(line):
        return regions

    prev_region: int | None = None
    cells: list[Cell] = []
    for cell in line:
        region = cell.region
        if prev_region != region:
            if len(cells):
                regions.append(cells)
            cells = []

        cells.append(cell)

        prev_region = region
    if len(cells):
        regions.append(cells)

    return regions
