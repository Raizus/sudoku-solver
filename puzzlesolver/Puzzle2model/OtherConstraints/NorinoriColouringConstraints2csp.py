from puzzlesolver.Puzzle.ConstraintEnums import GlobalRegionConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import is_odd_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars


def _set_norinori_colouring_constraint(model: PuzzleModel, puzzle: Puzzle):
    """
    Nourinouri Coloring: each shaded cell is orthogonally adjacent to exactly one other shaded cell.
    """
    grid = puzzle.grid
    all_cells = grid.getAllCells()
    grid_vars_dict = model.grid_vars_dict

    # create norinori bool grid, var == 1 if norinori, else var == 0
    bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"norinori_colouring_grid")
    grid_vars_dict["norinori_colouring_grid"] = bools_grid

    # if cell is shaded then it has exactly 1 shaded cell that is orthogonally adjacent to it
    for cell in all_cells:
        cell_norinori_var = cell2var(bools_grid, cell)
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        adjacent_cells_norinori_vars = cells2vars(
            bools_grid, adjacent_cells)
        model.Add(sum(adjacent_cells_norinori_vars) ==
                  1).OnlyEnforceIf(cell_norinori_var)

    return bools_grid


def get_or_set_norinori_colouring_constraint(model: PuzzleModel,
                                             puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "norinori_colouring_grid" in grid_vars_dict:
        return grid_vars_dict["norinori_colouring_grid"]

    norinori_colouring_grid = _set_norinori_colouring_constraint(
        model, puzzle)
    return norinori_colouring_grid


def set_all_shaded_norinori_cells_are_odd_constraints(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.ALL_SHADED_NORINORI_CELLS_ARE_ODD, False)
    if not constraint:
        return

    norinori_colouring_grid = get_or_set_norinori_colouring_constraint(
        model, puzzle)

    grid_vars = model.grid_vars_dict['cells_grid_vars']
    all_cells = puzzle.grid.getAllCells()
    prefix = f"all_shaded_norinori_cells_are_odd"

    for cell in all_cells:
        norinori_var = cell2var(norinori_colouring_grid, cell)
        cell_var = cell2var(grid_vars, cell)

        is_odd_bool = is_odd_csp(
            model, cell_var, f"{prefix} - {cell.format_cell()}")
        model.AddImplication(norinori_var, is_odd_bool)
