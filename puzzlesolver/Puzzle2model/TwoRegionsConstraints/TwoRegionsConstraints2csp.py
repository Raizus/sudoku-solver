

from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.ConstraintEnums import TwoRegionsConstraintsE
from puzzlesolver.Puzzle.Constraints import CloneConstraint
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_csp_utils import coord2var
from puzzlesolver.Puzzle2model.puzzle_model_types import GridVars


def genCloneConstraintProperties(model: PuzzleModel, puzzle: Puzzle, tool_key: TwoRegionsConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for constraint in constraints_list:
        if not isinstance(constraint, CloneConstraint):
            continue
        cell_coords = constraint.cells
        cells: list[Cell] = []
        for cell_coord in cell_coords:
            cell = puzzle.grid.getCellFromCoords(cell_coord)
            if cell is not None:
                cells.append(cell)

        cell_coords2 = constraint.cells2
        cells2: list[Cell] = []
        for cell_coord in cell_coords2:
            cell = puzzle.grid.getCellFromCoords(cell_coord)
            if cell is not None:
                cells2.append(cell)

        cells_vars = [coord2var(grid_vars, cell_coord)
                      for cell_coord in cell_coords]
        cells2_vars = [coord2var(grid_vars, cell_coord)
                       for cell_coord in cell_coords2]
        yield cells, cells2, cells_vars, cells2_vars, constraint.value


def set_clones_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = TwoRegionsConstraintsE.CLONES
    # prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not constraints_list:
        return

    for _, (_, _, cells_vars, cells2_vars, _) in enumerate(genCloneConstraintProperties(model, puzzle, key)):
        for cell1_var, cell2_var in zip(cells_vars, cells2_vars):
            model.Add(cell1_var == cell2_var)


def set_two_regions_constraints(model: PuzzleModel, puzzle: Puzzle):
    set_clones_constraints(model, puzzle)
