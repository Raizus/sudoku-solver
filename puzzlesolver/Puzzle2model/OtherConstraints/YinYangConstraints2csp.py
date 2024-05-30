from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import count_vars
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars, orthogonally_connected_region_csp
from puzzlesolver.Puzzle2model.puzzle_model_types import build_adjacency_dict


def _set_yin_yang_constraints(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    n_rows = grid.nRows
    n_cols = grid.nCols
    all_cells = grid.getAllCells()
    prefix = f"yin_yang"

    yin_yang_grid = bool_vars_grid_dict_from_puzzle_grid(model, grid, prefix)

    # 2x2 box cannot be all shaded and unshaded, no crossing shaded vs unshaded
    for cell in all_cells:
        box = [cell2 for line in grid.getXByYBox(cell, 2, 2) for cell2 in line]
        if len(box) != 4:
            continue

        two_by_two = cells2vars(yin_yang_grid, box)

        # 2x2 box cannot be all shaded or all unshaded
        # 0 < count < 4
        count0 = count_vars(model, two_by_two, 0,
                            f"{prefix} - count0_2by2_{cell.format_cell()}")
        model.Add(count0 > 0)
        model.Add(count0 < 4)

        # no crossing 1's and 0's because it implies the grid is not connected
        # [1, 0]    or  [0, 1]
        # [0, 1]        [1, 0]
        # ^ NOT ALLOWED
        a = model.NewBoolVar(
            f"{prefix} - crossing_a {box[0].format_cell()} == {box[3].format_cell()}")
        b = model.NewBoolVar(
            f"{prefix} - crossing_b {box[1].format_cell()} == {box[2].format_cell()}")
        model.Add(two_by_two[0] == two_by_two[3]).OnlyEnforceIf(a)
        model.Add(two_by_two[0] != two_by_two[3]).OnlyEnforceIf(a.Not())
        model.Add(two_by_two[1] == two_by_two[2]).OnlyEnforceIf(b)
        model.Add(two_by_two[1] != two_by_two[2]).OnlyEnforceIf(b.Not())
        model.AddBoolOr([a.Not(), b.Not()])

    # PERIMETER TRANSITIONS
    # perimeter_cells = grid.get_perimeter()
    # perimeter_vars = cells2vars(yin_yang_grid, perimeter_cells)
    # ts = [model.NewBoolVar(f"{prefix}: perimeter_transition_bool_{_cell.format_cell()}")
    #       for i, _cell in enumerate(perimeter_cells)]
    # for i, var in enumerate(perimeter_vars):
    #     var2 = perimeter_vars[(i + 1) % len(perimeter_vars)]
    #     model.Add(var != var2).OnlyEnforceIf(ts[i])
    #     model.Add(var == var2).OnlyEnforceIf(ts[i].Not())
    # model.Add(sum(ts) <= 2)

    # every row must have at least one "1" and one "0", except for edges
    for row in range(1, n_rows - 1):
        row_cells = grid.getRow(row)
        row_vars = cells2vars(yin_yang_grid, row_cells)

        count0 = count_vars(model, row_vars, 0, f"{prefix} - count0_row_{row}")
        model.Add(count0 > 0)
        model.Add(count0 < n_cols)

    # every col must have at least one "1" and one "0", except for edges
    for col in range(1, n_cols - 1):
        col_cells = grid.getCol(col)
        col_vars = cells2vars(yin_yang_grid, col_cells)

        count0 = count_vars(model, col_vars, 0, f"{prefix} - count0_col_{col}")
        model.Add(count0 > 0)
        model.Add(count0 < n_rows)

    # no lone 1s or 0s
    for cell in grid.getAllCells():
        cell_var = cell2var(yin_yang_grid, cell)
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        adjacent_vars = cells2vars(yin_yang_grid, adjacent_cells)

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

    all_vars = cells2vars(yin_yang_grid, grid.getAllCells())
    model.Add(sum(all_vars) == count1_total)
    model.Add(len(all_vars) - count1_total == count0_total)

    # orthogonally connected regions
    yin_yang_negated_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, "yin_yang_negated")
    for key, var in yin_yang_grid.items():
        neg_var = yin_yang_negated_grid[key]
        model.Add(neg_var == var.Not())

    adjacency_dict = build_adjacency_dict(puzzle.grid)
    orthogonally_connected_region_csp(
        model, adjacency_dict, yin_yang_grid, n_rows * n_cols)
    orthogonally_connected_region_csp(
        model, adjacency_dict, yin_yang_negated_grid, n_rows * n_cols)

    model.grid_vars_dict["yin_yang_grid"] = yin_yang_grid
    model.grid_vars_dict["yin_yang_negated_grid"] = yin_yang_negated_grid

    return yin_yang_grid


def get_or_set_yin_yang_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "yin_yang_grid" in grid_vars_dict:
        return grid_vars_dict["yin_yang_grid"]

    yin_yang_grid = _set_yin_yang_constraints(model, puzzle)
    return yin_yang_grid
