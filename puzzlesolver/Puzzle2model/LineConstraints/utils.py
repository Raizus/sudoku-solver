

from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.ConstraintEnums import LineConstraintsE
from puzzlesolver.Puzzle.Constraints import LineConstraint
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, coord2var
# from Puzzle2cp_model.puzzle_csp_utils import GridVars, coord2var


def genConstraint(puzzle: Puzzle, tool_key: LineConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    for constraint in constraints_list:
        if not isinstance(constraint, LineConstraint):
            continue
        yield constraint


def genLineConstraintProperties(model: PuzzleModel, puzzle: Puzzle, tool_key: LineConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for constraint in constraints_list:
        if not isinstance(constraint, LineConstraint):
            continue
        cell_coords = constraint.cells
        cells: list[Cell] = []
        for cell_coord in cell_coords:
            cell = puzzle.grid.getCellFromCoords(cell_coord, True)
            if cell is not None:
                cells.append(cell)

        # cell_var = coord2var(grid_vars, cell_coord)
        cells_vars = [coord2var(grid_vars, cell_coord)
                      for cell_coord in cell_coords]
        yield cells, cells_vars, constraint.value
