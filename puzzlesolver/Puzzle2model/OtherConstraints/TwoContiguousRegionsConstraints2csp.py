from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import count_vars
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars, orthogonally_connected_region_csp
from puzzlesolver.Puzzle2model.puzzle_model_types import build_adjacency_dict


def _set_two_contiguous_regions_constraints(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    n_rows, n_cols = grid.nRows, grid.nCols
    grid_vars_dict = model.grid_vars_dict
    all_cells = grid.getAllCells()
    prefix = f"two_contiguous_regions"

    two_contiguous_regions_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, prefix)
    grid_vars_dict["two_contiguous_regions_grid"] = two_contiguous_regions_grid

    # no lone 1s or 0s
    for cell in all_cells:
        cell_var = cell2var(two_contiguous_regions_grid, cell)
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        adjacent_vars = cells2vars(two_contiguous_regions_grid, adjacent_cells)

        count0 = count_vars(model, adjacent_vars, 0,
                            f"{prefix} - count0_{cell.format_cell()}_neighbours")
        count1 = count_vars(model, adjacent_vars, 1,
                            f"{prefix} - count1_{cell.format_cell()}_neighbours")
        model.Add(count0 > 0).OnlyEnforceIf(cell_var.Not())
        model.Add(count1 > 0).OnlyEnforceIf(cell_var)

    count0_total = model.NewIntVar(
        0, n_rows * n_cols, f"{prefix} - count0_total")
    count1_total = model.NewIntVar(
        0, n_rows * n_cols, f"{prefix} - count1_total")

    all_vars = cells2vars(two_contiguous_regions_grid, grid.getAllCells())
    model.Add(sum(all_vars) == count1_total)
    model.Add(len(all_vars) - count1_total == count0_total)

    # orthogonally connected regions
    two_contiguous_regions_negated_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, "two_contiguous_regions_negated")
    for key, var in two_contiguous_regions_grid.items():
        neg_var = two_contiguous_regions_negated_grid[key]
        model.Add(neg_var == var.Not())

    adjacency_dict = build_adjacency_dict(puzzle.grid)
    orthogonally_connected_region_csp(
        model, adjacency_dict, two_contiguous_regions_grid, n_rows * n_cols)
    orthogonally_connected_region_csp(
        model, adjacency_dict, two_contiguous_regions_negated_grid, n_rows * n_cols)

    return two_contiguous_regions_grid


def get_or_set_two_contiguous_regions_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "two_contiguous_regions_grid" in grid_vars_dict:
        return grid_vars_dict["two_contiguous_regions_grid"]

    two_contiguous_regions_grid = _set_two_contiguous_regions_constraints(
        model, puzzle)
    return two_contiguous_regions_grid
