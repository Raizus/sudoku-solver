

from puzzlesolver.Puzzle.ConstraintEnums import GlobalRegionConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import are_all_equal_csp, are_all_true_csp, masked_count_vars, count_vars, increasing_strict, index_of_first_bools_csp, is_inside_interval_2_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars, int_vars_grid_dict_from_puzzle_grid, orthogonally_connected_region_csp
from puzzlesolver.Puzzle2model.puzzle_model_types import build_adjacency_dict
from ortools.sat.python.cp_model import IntVar, IntervalVar


def set_regions_do_not_cover_2x2_sections_constraint(model: PuzzleModel, puzzle: Puzzle):
    key2 = GlobalRegionConstraintsE.UNKNOWN_REGIONS_DO_NOT_COVER_2X2_SECTIONS
    regions_do_not_cover_2x2_sections = puzzle.bool_constraints.get(
        key2, False)

    if not regions_do_not_cover_2x2_sections:
        return

    grid = puzzle.grid
    all_cells = grid.getAllCells()
    regions_grid = model.grid_vars_dict["regions_grid"]
    prefix = f"Unknown Regions - {key2.value}"
    for cell in all_cells:
        box = [cell for line in grid.getXByYBox(
            cell, 2, 2) for cell in line]
        if len(box) != 4:
            continue

        two_by_two = cells2vars(regions_grid, box)
        name = f"{prefix} - 2x2 sections have more than one region - {cell.format_cell()}"
        all_equal_bool = are_all_equal_csp(model, two_by_two, name)
        model.Add(all_equal_bool == 0)


def _set_unknown_regions_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)
    all_cells = grid.getAllCells()
    grid_vars_dict = model.grid_vars_dict
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    prefix = f"unknown_regions"

    n_rows = grid.nRows
    n_cols = grid.nCols

    if n_rows != n_cols:
        raise Exception("Grid must be square.")

    num_regions = n_rows
    region_size = num_regions
    all_cells_vars = cells2vars(cells_grid_vars, all_cells)

    region_values = [x for x in range(0, num_regions)]
    # each var represents the cell region
    regions_grid = int_vars_grid_dict_from_puzzle_grid(
        model, grid, -1, num_regions - 1, "region")
    grid_vars_dict["regions_grid"] = regions_grid

    # 9 cells of each region
    region_vars = cells2vars(regions_grid, all_cells)
    for region_val in region_values:
        region_size_count = count_vars(model, region_vars, region_val,
                                       f"{prefix} - region_size_count, region={region_val}")
        model.Add(region_size_count == region_size)

    # no lone regions of size 1
    for cell in all_cells:
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        adjacent_region_vars = cells2vars(regions_grid, adjacent_cells)
        region_cell_var = cell2var(regions_grid, cell)

        equal_adj_regions_count = \
            count_vars(model, adjacent_region_vars, region_cell_var,
                       f"{prefix} - equal_adj_regions_count_{cell.format_cell()}")
        model.Add(equal_adj_regions_count > 0)

    # orthogonally connected regions and region ordering
    unknown_numbered_regions = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.UNKNOWN_NUMBERED_REGIONS, False)
    adjacency_dict = build_adjacency_dict(puzzle.grid)
    regions_first_idx_vars: list[IntVar] = []
    for region in region_values:
        name = f"region_{region}_bools"
        region_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
            model, grid, name)
        grid_vars_dict[name] = region_bools_grid

        for cell in all_cells:
            region_var = cell2var(regions_grid, cell)
            region_bool_var = cell2var(region_bools_grid, cell)
            model.Add(region_var == region).OnlyEnforceIf(region_bool_var)
            model.Add(region_var != region).OnlyEnforceIf(
                region_bool_var.Not())

        seed = None
        # if i == 0 and not numbered_unknown_regions:
        #     seed = [(all_cells[0].row, all_cells[0].col)]
        #     region_var = cell2var(regions_grid, all_cells[0])
        #     model.Add(region_var == region)
        orthogonally_connected_region_csp(
            model, adjacency_dict, region_bools_grid, region_size, seed)

        # region ordering
        all_region_bools = cells2vars(region_bools_grid, all_cells)
        idx_var = index_of_first_bools_csp(model, all_region_bools)
        regions_first_idx_vars.append(idx_var)
        if unknown_numbered_regions:
            first_cell_value_var = model.NewIntVar(
                min_digit, max_digit, f"{prefix} - region_{region} first_cell_value")
            first_cell_region_var = model.NewIntVar(0, num_regions - 1,
                                                    f"{prefix} - region_{region} first_cell_region_var")
            model.AddElement(idx_var, all_cells_vars, first_cell_value_var)
            model.Add(first_cell_value_var == puzzle.valid_digits[region])
            model.AddElement(idx_var, region_vars, first_cell_region_var)
            model.Add(first_cell_region_var == region)

    if not unknown_numbered_regions:
        increasing_strict(model, regions_first_idx_vars)

    # all different values for each region
    all_cells_vars = cells2vars(cells_grid_vars, all_cells)
    for region_val in region_values:
        region_bools_grid = grid_vars_dict[f"region_{region_val}_bools"]
        all_region_bool_vars = cells2vars(region_bools_grid, all_cells)

        # one of each digit per region
        for value in puzzle.valid_digits:
            name = f"{prefix} - count_region_{region_val} digit_{value}"
            count_digit_in_region = masked_count_vars(
                model, all_cells_vars, all_region_bool_vars, value, name)
            model.Add(count_digit_in_region == 1)

    # 2x2 sections must have more than one region
    set_regions_do_not_cover_2x2_sections_constraint(model, puzzle)

    return regions_grid


def get_or_set_unknown_regions_grid(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "regions_grid" in grid_vars_dict:
        return grid_vars_dict["regions_grid"]

    regions_grid = _set_unknown_regions_constraint(model, puzzle)
    return regions_grid


def _set_nine_3x3_unknown_regions_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    grid_vars_dict = model.grid_vars_dict
    prefix = f"nine_3x3_unknown_regions"
    region_length = 3
    all_cells = grid.getAllCells()
    num_regions = 9
    region_size = 9
    n_rows = grid.nRows
    n_cols = grid.nCols
    cells_grid_vars = model.grid_vars_dict['cells_grid_vars']
    valid_digits = puzzle.valid_digits
    min_valid = min(puzzle.valid_digits)

    filled_cells_grid = grid_vars_dict.get("filled_cells_grid")

    is_region_bool_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix} - is_region_bool_grid")
    grid_vars_dict["is_region_bool_grid"] = is_region_bool_grid

    regions_grid = int_vars_grid_dict_from_puzzle_grid(
        model, grid, -1, num_regions - 1, "region")
    grid_vars_dict["regions_grid"] = regions_grid
    all_region_vars = cells2vars(regions_grid, all_cells)

    intervals_row: list[IntervalVar] = []
    intervals_col: list[IntervalVar] = []
    lin_region_first_idx_vars: list[IntVar] = []
    for region in range(num_regions):
        prefix2 = f"{prefix} - region={region}"
        start_row = model.NewIntVar(
            0, n_rows - region_length, f"{prefix2} - start_row")
        start_col = model.NewIntVar(
            0, n_cols - region_length, f"{prefix2} - start_col")
        region_first_idx_var = model.NewIntVar(
            0, n_rows * n_cols, f"{prefix2} - first_idx_var")
        lin_region_first_idx_vars.append(region_first_idx_var)
        model.Add(start_row * n_cols + start_col == region_first_idx_var)
        interval_row = model.NewFixedSizedIntervalVar(start_row, region_length,
                                                      f"{prefix2} - interval_row")
        intervals_row.append(interval_row)
        interval_col = model.NewFixedSizedIntervalVar(start_col, region_length,
                                                      f"{prefix} - interval_col")
        intervals_col.append(interval_col)

        for cell in all_cells:
            prefix3 = f"{prefix2} - {cell.format_cell()}"
            region_var = cell2var(regions_grid, cell)

            cell_is_inside_interval_row = is_inside_interval_2_csp(model, interval_row, cell.row,
                                                                   f"{prefix3} - cell_is_inside_interval_row")
            cell_is_inside_interval_col = is_inside_interval_2_csp(model, interval_col, cell.col,
                                                                   f"{prefix3} - cell_is_inside_interval_col")
            name = f"{prefix3} - cell_is_inside_region"
            cell_is_inside_region = are_all_true_csp(
                model, [cell_is_inside_interval_row, cell_is_inside_interval_col], name)

            model.Add(region_var == region).OnlyEnforceIf(
                cell_is_inside_region)
            model.Add(region_var != region).OnlyEnforceIf(
                cell_is_inside_region.Not())

        # enforce region sizes
        size_count = count_vars(model, all_region_vars, region,
                                f"{prefix2} - size_count")
        model.Add(size_count == region_size)

    # regions don't overlap and the linearized index of the first cell in each region is strictly increasing
    model.AddNoOverlap2D(intervals_col, intervals_row)
    increasing_strict(model, lin_region_first_idx_vars)

    for cell in all_cells:
        is_region_bool = cell2var(is_region_bool_grid, cell)
        region_var = cell2var(regions_grid, cell)
        model.Add(region_var == -1).OnlyEnforceIf(is_region_bool.Not())
        model.Add(region_var != -1).OnlyEnforceIf(is_region_bool)

    for cell in all_cells:
        is_region_bool = cell2var(is_region_bool_grid, cell)
        cell_var = cell2var(cells_grid_vars, cell)
        model.Add(cell_var != min_valid - 1).OnlyEnforceIf(is_region_bool)

    if filled_cells_grid:
        for cell in all_cells:
            filled_cell_var = cell2var(filled_cells_grid, cell)
            is_region_bool = cell2var(is_region_bool_grid, cell)
            model.Add(filled_cell_var == 1).OnlyEnforceIf(is_region_bool)
            model.Add(filled_cell_var == 0).OnlyEnforceIf(is_region_bool.Not())

    # no repeats in regions
    all_cell_vars = cells2vars(cells_grid_vars, all_cells)
    for region in range(num_regions):
        region_bool_grid = bool_vars_grid_dict_from_puzzle_grid(model, grid,
                                                                f"{prefix} - region_{region}_bools_grid")
        for cell in all_cells:
            region_var = cell2var(regions_grid, cell)
            region_bool_var = cell2var(region_bool_grid, cell)
            model.Add(region_var == region).OnlyEnforceIf(region_bool_var)
            model.Add(region_var != region).OnlyEnforceIf(
                region_bool_var.Not())

        all_region_bool_vars = cells2vars(region_bool_grid, all_cells)
        for digit in valid_digits:
            name = f"{prefix} - region={region}, digit={digit} count"
            count_var = masked_count_vars(model, all_cell_vars,
                                          all_region_bool_vars, digit, name)
            model.AddAllowedAssignments([count_var], [(0,), (1,)])

    # same_region_dict: dict[tuple[tuple[int, int], tuple[int, int]], IntVar] = dict()
    # for cell1, cell2 in combinations(all_cells, 2):
    #     cell1_var = cell2var(cells_grid_vars, cell1)
    #     cell2_var = cell2var(cells_grid_vars, cell2)
    #     cell1_region_var = cell2var(unknown_regions_grid, cell1)
    #     cell2_region_var = cell2var(unknown_regions_grid, cell2)
    #     cell1_filled_bool = cell2var(filled_cells_grid, cell1)
    #     cell2_filled_bool = cell2var(filled_cells_grid, cell2)
    #     same_region_bool = model.NewBoolVar(f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()}, "
    #                                         f"is_same_region_bool")
    #     any_unfilled_cell_bool = model.NewBoolVar(f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()}, "
    #                                               f"any_unfilled_cell_bool")
    #     same_region_and_filled_bool = model.NewBoolVar(f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()}, "
    #                                                    f"same_region_and_filled_bool")
    #     model.AddBoolOr(cell1_filled_bool.Not(), cell2_filled_bool.Not()).OnlyEnforceIf(any_unfilled_cell_bool)
    #     model.AddBoolAnd(cell1_filled_bool, cell2_filled_bool).OnlyEnforceIf(any_unfilled_cell_bool.Not())
    #     model.Add(cell1_region_var == cell2_region_var).OnlyEnforceIf(same_region_bool)
    #     model.Add(cell1_region_var != cell2_region_var).OnlyEnforceIf(same_region_bool.Not())
    #     model.AddBoolAnd(same_region_bool, any_unfilled_cell_bool.Not()).OnlyEnforceIf(same_region_and_filled_bool)
    #     model.AddBoolOr(same_region_bool.Not(), any_unfilled_cell_bool).OnlyEnforceIf(same_region_and_filled_bool.Not())
    #
    #     model.Add(cell1_var != cell2_var).OnlyEnforceIf(same_region_and_filled_bool)
    #     same_region_dict[((cell1.row, cell1.col), (cell2.row, cell2.col))] = same_region_and_filled_bool
    #     same_region_dict[((cell2.row, cell2.col), (cell1.row, cell1.col))] = same_region_and_filled_bool


def get_or_set_nine_3x3_unknown_regions_grid(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "regions_grid" in grid_vars_dict:
        return grid_vars_dict["regions_grid"]

    regions_grid = _set_nine_3x3_unknown_regions_constraint(model, puzzle)
    return regions_grid


def set_nine_3x3_unknown_regions_constraint(model: PuzzleModel, puzzle: Puzzle):
    key = GlobalRegionConstraintsE.UNKNOWN_NINE_3X3_REGIONS
    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    get_or_set_nine_3x3_unknown_regions_grid(model, puzzle)


def set_unknown_regions_constraint(model: PuzzleModel, puzzle: Puzzle):
    key1 = GlobalRegionConstraintsE.UNKNOWN_REGIONS
    key2 = GlobalRegionConstraintsE.UNKNOWN_NUMBERED_REGIONS
    constraint1 = puzzle.bool_constraints.get(key1, False)
    constraint2 = puzzle.bool_constraints.get(key2, False)
    if constraint1 or constraint2:
        get_or_set_unknown_regions_grid(model, puzzle)


def set_four_color_theorem_colored_regions_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    all_cells = grid.getAllCells()
    prefix = f"four_color_theorem_colored_regions"

    colored_regions_grid = int_vars_grid_dict_from_puzzle_grid(
        model, grid, 0, 3, "colored_regions")
    regions_grid = get_or_set_unknown_regions_grid(
        model, puzzle)

    for cell1 in all_cells:
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell1)
        cell1_region_var = cell2var(regions_grid, cell1)
        cell1_colored_region_var = cell2var(colored_regions_grid, cell1)
        for cell2 in adjacent_cells:
            cell2_region_var = cell2var(regions_grid, cell2)
            cell2_colored_region_var = cell2var(colored_regions_grid, cell2)
            same_region_bool = model.NewBoolVar(
                f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()} same_region")
            model.Add(cell1_region_var == cell2_region_var).OnlyEnforceIf(
                same_region_bool)
            model.Add(cell1_region_var != cell2_region_var).OnlyEnforceIf(
                same_region_bool.Not())

            model.Add(cell1_colored_region_var ==
                      cell2_colored_region_var).OnlyEnforceIf(same_region_bool)
            model.Add(cell1_colored_region_var != cell2_colored_region_var).OnlyEnforceIf(
                same_region_bool.Not())

    for cell in all_cells:
        cell_region_var = cell2var(regions_grid, cell)
        cell_colored_region_var = cell2var(colored_regions_grid, cell)
        cell_is_region_0 = model.NewBoolVar(
            f"{prefix} - {cell.format_cell()}, cell_is_region_0")
        model.Add(cell_region_var == 0).OnlyEnforceIf(cell_is_region_0)
        model.Add(cell_region_var != 0).OnlyEnforceIf(cell_is_region_0.Not())
        model.Add(cell_colored_region_var == 0).OnlyEnforceIf(cell_is_region_0)

    grid_vars_dict["four_color_theorem_colored_regions"] = colored_regions_grid
    return colored_regions_grid


def get_or_set_four_color_theorem_colored_regions_constraint(model: PuzzleModel,
                                                             puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "four_color_theorem_colored_regions" in grid_vars_dict:
        return grid_vars_dict["four_color_theorem_colored_regions"]

    colored_regions = set_four_color_theorem_colored_regions_constraint(
        model, puzzle)
    return colored_regions
