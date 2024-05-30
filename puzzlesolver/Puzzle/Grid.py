from collections import Counter
from math import floor
from typing import Any, Literal, Union

from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.Coords import GridCoords
from puzzlesolver.Puzzle.Directions import DIRECTIONS, DirectionToRCDict


class Grid:
    _grid: list[list[Cell]]
    nRows: int
    nCols: int

    def __init__(self, nrows: int, ncols: int):
        self.nRows = nrows
        self.nCols = ncols
        self._grid = []

        for i in range(nrows):
            row: list[Cell] = []
            for j in range(ncols):
                cell = Cell(i, j, nrows)
                row.append(cell)
            self._grid.append(row)

    def getCell(self, row: int, col: int, get_outside: bool = False) -> Union[Cell, None]:
        if not (0 <= row < self.nRows):
            return None
        if not (0 <= col < self.nCols):
            return None

        cell = self._grid[row][col]
        if cell.outside and not get_outside:
            return None
        return cell

    def getCellFromCoords(self, coord: GridCoords, get_outside: bool = False) -> Union[Cell, None]:
        if not isinstance(coord.r, int) or not isinstance(coord.c, int):
            return None
        return self.getCell(coord.r, coord.c, get_outside)

    def getRow(self, row: int, getOutside: bool = False) -> list[Cell]:
        cells: list[Cell] = []
        if 0 <= row < self.nRows:
            cells = list(self._grid[row])

        if not getOutside:
            cells = [cell for cell in cells if not cell.outside]

        return cells

    def getCol(self, col: int, getOutside: bool = False) -> list[Cell]:
        cells: list[Cell] = []
        if 0 <= col < self.nCols:
            cells = [row[col] for row in self._grid]

        if not getOutside:
            cells = [cell for cell in cells if not cell.outside]

        return cells

    def getVerticallyAdjacentCells(self, cell: Cell, get_outside: bool = False) -> list[Cell]:
        cells: list[Cell] = []
        up = self.getCell(cell.row-1, cell.col, get_outside)
        down = self.getCell(cell.row+1, cell.col, get_outside)

        if up is not None:
            cells.append(up)
        if down is not None:
            cells.append(down)

        return cells

    def getHorizontallyAdjacentCells(self, cell: Cell, get_outside: bool = False) -> list[Cell]:
        cells: list[Cell] = []
        left = self.getCell(cell.row, cell.col-1, get_outside)
        right = self.getCell(cell.row, cell.col+1, get_outside)

        if left is not None:
            cells.append(left)
        if right is not None:
            cells.append(right)

        return cells

    def getOrthogonallyAdjacentCells(self, cell: Cell, get_outside: bool = False) -> list[Cell]:
        cells: list[Cell] = []
        up = self.getCell(cell.row-1, cell.col, get_outside)
        down = self.getCell(cell.row+1, cell.col, get_outside)
        left = self.getCell(cell.row, cell.col-1, get_outside)
        right = self.getCell(cell.row, cell.col+1, get_outside)

        if up is not None:
            cells.append(up)
        if down is not None:
            cells.append(down)
        if left is not None:
            cells.append(left)
        if right is not None:
            cells.append(right)

        return cells

    def getDiagonallyAdjacentCells(self, cell: Cell, get_outside: bool = False) -> list[Cell]:
        cells: list[Cell] = []
        nw = self.getCell(cell.row-1, cell.col-1, get_outside)
        ne = self.getCell(cell.row-1, cell.col+1, get_outside)
        sw = self.getCell(cell.row+1, cell.col-1, get_outside)
        se = self.getCell(cell.row+1, cell.col+1, get_outside)

        if nw is not None:
            cells.append(nw)
        if ne is not None:
            cells.append(ne)
        if sw is not None:
            cells.append(sw)
        if se is not None:
            cells.append(se)

        return cells

    def getNeighbourCells(self, cell: Cell, get_outside: bool = False) -> list[Cell]:
        orth_adj = self.getOrthogonallyAdjacentCells(cell, get_outside)
        diag_adj = self.getDiagonallyAdjacentCells(cell, get_outside)

        cells = orth_adj + diag_adj
        return cells

    def getAllCells(self, getOutside: bool = False) -> list[Cell]:
        cells: list[Cell] = []
        for row in self._grid:
            cells.extend(row)

        if not getOutside:
            cells = [cell for cell in cells if not cell.outside]

        return cells

    def getRegionCells(self, region: int | None) -> list[Cell]:
        if region is None:
            return []
        regionCells: list[Cell] = [
            cell for row in self._grid for cell in row if cell.region == region]
        return regionCells

    def getUsedRegions(self) -> list[int]:
        usedRegions: set[int] = set(
            cell.region for row in self._grid for cell in row if cell.region != None)

        usedRegionsList = list(usedRegions)
        usedRegionsList.sort()
        return usedRegionsList

    def getRegionCounts(self) -> Counter[int]:
        region_vals = [cell.region for cell in self.getAllCells()
                       if cell.region is not None]
        c = Counter(region_vals)
        return c

    def getDisjointGroupIdx(self, cell: Cell) -> int:
        if cell.region is None:
            return -1
        return self.getRegionCells(cell.region).index(cell)

    def getCellsInDisjointGroup(self, groupIdx: int) -> list[Cell]:
        usedRegions = self.getUsedRegions()

        disjointGroup: list[Cell] = []

        for regionIdx in usedRegions:
            regionCells = self.getRegionCells(regionIdx)
            if 0 <= groupIdx < len(regionCells):
                disjointGroup.append(regionCells[groupIdx])

        return disjointGroup

    def getCellsInDirection(self, cell: Cell, direction: DIRECTIONS):
        dr, dc = DirectionToRCDict[direction]

        cells: list[Cell] = []
        i = 0
        while True:
            i += 1
            r, c = cell.row + i*dr, cell.col + i*dc

            if dr == 1 and r >= self.nRows:
                break
            if dr == -1 and r < 0:
                break
            if dc == 1 and c >= self.nCols:
                break
            if dc == -1 and c < 0:
                break

            cell2 = self.getCell(r, c)
            if cell2 is not None:
                cells.append(cell2)

        return cells

    def getAdjacentCellInDirection(self, cell: Cell, direction: DIRECTIONS) -> Cell | None:
        dr, dc = DirectionToRCDict[direction]
        cell2 = self.getCell(cell.row+dr, cell.col+dc)
        return cell2

    def getMainDiagonal(self, first_cell: Cell, direction: DIRECTIONS) -> list[Cell]:
        cells: list[Cell] = []
        cells = self.getCellsInDirection(first_cell, direction)
        cells = [first_cell] + cells
        if len(cells) != self.nRows or len(cells) != self.nCols:
            return []
        return cells

    def getPositiveDiagonal(self) -> list[Cell]:
        first_cell = self.getCell(self.nRows-1, 0)
        direction = DIRECTIONS.NE
        if not first_cell:
            return []

        return self.getMainDiagonal(first_cell, direction)

    def getNegativeDiagonal(self) -> list[Cell]:
        first_cell = self.getCell(0, 0)
        direction = DIRECTIONS.SE
        if not first_cell:
            return []

        return self.getMainDiagonal(first_cell, direction)

    def getKnigthMoveCells(self, cell: Cell) -> list[Cell]:
        cells: list[Cell] = []
        r, c = cell.row, cell.col
        deltas = [(-2, -1), (-2, 1),
                  (-1, -2), (-1, 2),
                  (1, -2),  (1, 2),
                  (2, -1), (2, 1),]
        for dr, dc in deltas:
            cell2 = self.getCell(r+dr, c+dc)
            if cell2 is not None:
                cells.append(cell2)
        return cells

    def genAllAdjacentPairs(self, mode: Literal["combinations", "permutations"] = "combinations"):
        for cell1 in self.getAllCells():
            adj_cells = self.getOrthogonallyAdjacentCells(cell1)
            if mode == "combinations":
                adj_cells = [cell2 for cell2 in adj_cells if cell2.row >=
                             cell1.row and cell2.col >= cell1.col]
            for cell2 in adj_cells:
                yield (cell1, cell2)

    def getXByYBox(self, cell: Cell, width: int, height: int) -> list[list[Cell]]:
        box: list[list[Cell]] = []
        r, c = cell.row, cell.col
        for i in range(height):
            line: list[Cell] = []
            for j in range(width):
                cell2 = self.getCell(r+i, c+j)
                if cell2:
                    line.append(cell2)
            box.append(line)
        return box

    def genAllPDiagonals(self):
        direction = DIRECTIONS.NE
        for cell in self.getCol(0):
            diag = [cell] + self.getCellsInDirection(cell, direction)
            yield diag

        for cell in self.getRow(self.nRows-1):
            if cell.col == 0:
                continue
            diag = [cell] + self.getCellsInDirection(cell, direction)
            yield diag

    def genAllNDiagonals(self):
        direction = DIRECTIONS.SE
        for cell in reversed(self.getCol(0)):
            diag = [cell] + self.getCellsInDirection(cell, direction)
            yield diag

        for cell in self.getRow(0):
            if cell.col == 0:
                continue
            diag = [cell] + self.getCellsInDirection(cell, direction)
            yield diag

    def getCell180RotSymmetry(self, cell: Cell, r: int | float, c: int | float) -> Union[Cell, None]:
        """Rotates a cell 180 degrees, around a center of rotation given by r, c

        Args:
            cell (Cell): 
            r (int | float): 
            c (int | float): 

        Returns:
            Union[Cell, None]: 
        """
        center_r = cell.row + 0.5
        center_c = cell.col + 0.5

        dr = r - center_r
        dc = c - center_c
        nr = floor(r + dr)
        nc = floor(c + dc)
        new_cell = self.getCell(nr, nc)
        return new_cell

    def getCellsInPDiagonalWithCell(self, cell: Cell) -> list[Cell]:
        cells1 = self.getCellsInDirection(cell, DIRECTIONS.NE)
        cells2 = self.getCellsInDirection(cell, DIRECTIONS.SW)
        cells2.reverse()
        cells = cells2 + [cell] + cells1

        return cells

    def getCellsInNDiagonalWithCell(self, cell: Cell) -> list[Cell]:
        cells1 = self.getCellsInDirection(cell, DIRECTIONS.SE)
        cells2 = self.getCellsInDirection(cell, DIRECTIONS.NW)
        cells2.reverse()
        cells = cells2 + [cell] + cells1

        return cells

    def getAdjacentToRC(self, r: int | float, c: int | float) -> list[Cell]:
        cells: list[Cell] = []
        r_residue = r % 1
        c_residue = c % 1

        # center
        if r_residue == 0.5 and c_residue == 0.5:
            nr = int(r - 0.5)
            nc = int(c - 0.5)
            cell = self.getCell(nr, nc)
            if cell:
                cells.append(cell)
        # border (same row)
        elif r_residue == 0.5 and c_residue == 0:
            nr = int(r - 0.5)
            nc = int(c - 0.5)
            for i in range(2):
                cell = self.getCell(nr, nc+i)
                if cell:
                    cells.append(cell)

        # border (same col)
        elif r_residue == 0 and c_residue == 0.5:
            nr = int(r - 0.5)
            nc = int(c - 0.5)
            for i in range(2):
                cell = self.getCell(nr+i, nc)
                if cell:
                    cells.append(cell)
        # corner
        elif r_residue == 0 and c_residue == 0:
            nr = int(r - 0.5)
            nc = int(c - 0.5)
            for i in range(2):
                for j in range(2):
                    cell = self.getCell(nr+i, nc+j)
                    if cell:
                        cells.append(cell)

        return cells

    @classmethod
    def fromJSON(cls, nrows: int, ncols: int, grid_json_data: list[list[dict[Any, Any]]]) -> 'Grid':
        grid = Grid(nrows, ncols)
        for i, data_row in enumerate(grid_json_data):
            for j, data_cell in enumerate(data_row):
                cell = grid._grid[i][j]
                for key, value in data_cell.items():
                    cell.__setattr__(key, value)

        return grid


if __name__ == "__main__":
    grid = Grid(9, 9)
