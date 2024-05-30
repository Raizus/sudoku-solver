from ortools.sat.python.cp_model import IntVar

from puzzlesolver.Puzzle.Grid import Grid

AdjacencyDict = dict[tuple[int, int], set[tuple[int, int]]]

# dict[coords representing nodes, dict[coords representing nodes, var indicating an edge (0 means no edge)]]
AdjacencyVarsDict = dict[tuple[int, int], dict[tuple[int, int], IntVar]]


GridVars = dict[tuple[int, int], IntVar]


def build_adjacency_dict(grid: Grid) -> AdjacencyDict:
    all_cells = grid.getAllCells()
    adjacency_dict: AdjacencyDict = dict()
    for cell in all_cells:
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        adjacency_coords = [(_cell.row, _cell.col) for _cell in adjacent_cells]
        adjacency_dict[(cell.row, cell.col)] = set(adjacency_coords)

    return adjacency_dict
