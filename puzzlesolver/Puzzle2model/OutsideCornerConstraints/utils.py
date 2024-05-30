

from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.ConstraintEnums import OutsideCornerConstraintsE
from puzzlesolver.Puzzle.Constraints import OutsideCornerConstraint
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
# from Puzzle2cp_model.puzzle_csp_utils import GridVars, coord2var


def genConstraint(puzzle: Puzzle, tool_key: OutsideCornerConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    for constraint in constraints_list:
        if not isinstance(constraint, OutsideCornerConstraint):
            continue
        yield constraint


def genOutsideCornerConstraintProperties(model: PuzzleModel, puzzle: Puzzle, tool_key: OutsideCornerConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for constraint in constraints_list:
        if not isinstance(constraint, OutsideCornerConstraint):
            continue
        cell_coord = constraint.cell
        cell = puzzle.grid.getCellFromCoords(cell_coord, True)
        if cell is None:
            cell = Cell(int(cell_coord.r), int(cell_coord.c), outside=True)

        direction = constraint.direction
        # cell_var = coord2var(grid_vars, cell_coord)
        value = constraint.value

        yield cell, direction, value
