from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var, exactly_n_per_row_col_region


def _set_battlestar_constraint(model: PuzzleModel, puzzle: Puzzle):
    """
    Battlestar: Each row, column, and region contains exactly 2 stars. Stars can't be within a kings move (in chess) from each other.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 

    Returns:
        _type_: 
    """
    grid = puzzle.grid
    grid_vars_dict = model.grid_vars_dict
    all_cells = grid.getAllCells()
    prefix = f"battlestar"

    n = 2

    # create multipliers bool grid, var == 1 if multiplier, else var == 0
    battlestar_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix} - bools_grid")
    grid_vars_dict["stars_bools_grid"] = battlestar_bools_grid
    exactly_n_per_row_col_region(model, grid, battlestar_bools_grid, n=n)

    # antiking
    for cell in all_cells:
        star_bool_var = cell2var(battlestar_bools_grid, cell)
        king_moves = grid.getNeighbourCells(cell)
        filtered = [_cell for _cell in king_moves if _cell.row >= cell.row]
        for cell2 in filtered:
            cell2_star_bool_var = cell2var(battlestar_bools_grid, cell2)
            model.Add(cell2_star_bool_var == 0).OnlyEnforceIf(star_bool_var)
            model.Add(star_bool_var == 0).OnlyEnforceIf(cell2_star_bool_var)

    return battlestar_bools_grid


def get_or_set_battlestar_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "stars_bools_grid" in grid_vars_dict:
        return grid_vars_dict["stars_bools_grid"]

    stars_bools_grid = _set_battlestar_constraint(model, puzzle)
    return stars_bools_grid
