

from puzzlesolver.Puzzle.ConstraintEnums import SingleCellArrowConstraintsE, SingleCellConstraintsE, SingleCellMultiArrowConstraintsE
from puzzlesolver.Puzzle.Constraints import SingleCellArrowConstraint, SingleCellConstraint, SingleCellMultiArrowConstraint
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, coord2var


def genConstraint(puzzle: Puzzle, tool_key: SingleCellConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    for constraint in constraints_list:
        if not isinstance(constraint, SingleCellConstraint):
            continue
        cell_coord = constraint.cell
        cell = puzzle.grid.getCellFromCoords(cell_coord)
        if cell is None:
            continue

        yield constraint


def genSingleCellConstraintProperties(model: PuzzleModel, puzzle: Puzzle, tool_key: SingleCellConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for constraint in constraints_list:
        if not isinstance(constraint, SingleCellConstraint):
            continue
        cell_coord = constraint.cell
        cell = puzzle.grid.getCellFromCoords(cell_coord)
        if cell is None:
            continue

        value = constraint.value

        cell_var = coord2var(grid_vars, cell_coord)
        yield cell, cell_var, value


def genSingleCellArrowConstraintProperties(model: PuzzleModel, puzzle: Puzzle, tool_key: SingleCellArrowConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for constraint in constraints_list:
        if not isinstance(constraint, SingleCellArrowConstraint):
            continue
        cell_coord = constraint.cell
        cell = puzzle.grid.getCellFromCoords(cell_coord)
        if cell is None:
            continue

        value = constraint.value
        arrow = constraint.arrow

        cell_var = coord2var(grid_vars, cell_coord)
        yield cell, cell_var, arrow, value


def genSingleCellMultiArrowConstraintProperties(model: PuzzleModel, puzzle: Puzzle, tool_key: SingleCellMultiArrowConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for constraint in constraints_list:
        if not isinstance(constraint, SingleCellMultiArrowConstraint):
            continue
        cell_coord = constraint.cell
        cell = puzzle.grid.getCellFromCoords(cell_coord)
        if cell is None:
            continue

        value = constraint.value
        arrows = constraint.arrows

        cell_var = coord2var(grid_vars, cell_coord)
        yield cell, cell_var, arrows, value
