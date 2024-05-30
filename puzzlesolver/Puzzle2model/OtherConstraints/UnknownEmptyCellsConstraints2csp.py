from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var


def _set_unknown_empty_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    prefix = f"filler_cells"
    grid_vars_dict = model.grid_vars_dict
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    filled_cells_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix} - bools_grid")
    grid_vars_dict["filled_cells_grid"] = filled_cells_grid
    all_cells = grid.getAllCells()
    min_valid = min(puzzle.valid_digits)

    for cell in all_cells:
        cell_var = cell2var(cells_grid_vars, cell)
        filled_cell_var = cell2var(filled_cells_grid, cell)
        model.Add(cell_var == min_valid -
                  1).OnlyEnforceIf(filled_cell_var.Not())
        model.Add(cell_var != min_valid - 1).OnlyEnforceIf(filled_cell_var)

    return filled_cells_grid


def get_or_set_unknown_empty_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "filled_cells_grid" in grid_vars_dict:
        return grid_vars_dict["filled_cells_grid"]

    filled_cells_grid = _set_unknown_empty_cells_constraint(
        model, puzzle)
    return filled_cells_grid
