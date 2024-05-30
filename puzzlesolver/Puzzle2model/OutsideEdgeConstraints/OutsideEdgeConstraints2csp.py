
from ortools.sat.python import cp_model
from puzzlesolver.Puzzle.ConstraintEnums import OutsideEdgeConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownRegionsConstraints2csp import get_or_set_unknown_regions_grid
from puzzlesolver.Puzzle2model.OtherConstraints.YinYangConstraints2csp import get_or_set_yin_yang_constraint
from puzzlesolver.Puzzle2model.OutsideEdgeConstraints.utils import genOutsideEdgeConstraintProperties
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import battlefield_csp, broken_x_sum_csp, masked_sum_csp, count_transitions_csp, find_first_mod_target, rising_streak_csp, sandwich_sum_csp, shifted_x_sum_csp, shortsighted_x_sum_csp, skyscraper_csp, x_sum_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, cells2vars
from ortools.sat.python.cp_model import IntVar

import warnings


def set_sandwich_sum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A number outside the grid gives the sum of the digits sandwiched between the 1 and 9 in that row/column.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.SANDWICH_SUM
    prefix = f"{key.value}"
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)

    for i, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        sum_result = sandwich_sum_csp(model, cells_vars, min_digit,
                                      max_digit, f"{prefix}_{i} - {cell.format_cell()}")
        model.Add(sum_result == sum_var)


def set_x_sums_constraints(model: PuzzleModel,
                           puzzle: Puzzle):
    """
    A clue outside the grid gives the sum of the first X digits from that direction,
    where X is the first of those digits.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.X_SUM
    prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)

    for i, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        sum_result = x_sum_csp(
            model, cells_vars, cells_vars[0], f"{prefix}_{i}")
        model.Add(sum_result == sum_var)


def set_shortsighted_x_sum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A clue outside the grid gives the sum of the nearest X or (X-1) numbers, where X is the number in the first
    cell from that direction.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.SHORTSIGHTED_X_SUM
    # prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)

    for _, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        shortsighted_x_sum_csp(model, cells_vars, sum_var, cells_vars[0])


def set_shifted_x_sum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Clues outside the grid indicate the sum of the first X digits from the Nth cell from that side, where X is the
    digit in the Nth cell and N is the digit in the first cell from that side.

    Example: in a row with 514839762 the clue from the left would be 19 (3+9+7) and from the right
    would be 37 (6+7+9+3+8+4).

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.SHIFTED_X_SUM
    prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for i, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        n_var = model.NewIntVar(min_digit, max_digit, f"{prefix}_{i} - n")
        model.Add(n_var == cells_vars[0] - 1)
        x_var = model.NewIntVar(min_digit, max_digit, f"{prefix}_{i} - x")
        model.AddElement(n_var, cells_vars, x_var)
        shifted_x_sum_csp(model, cells_vars, sum_var,
                          x_var, n_var, f"{prefix}_{i}")


def set_battlefield_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Consider the first X cells and the last Y cells of a row or column where X is the number in the first cell and Y
    is the number in the last cell. A clue outside the grid gives the sum of the digits where these groups overlap,
    or the sum of the digits in the gap between the groups if they don't overlap.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.BATTLEFIELD
    # prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)

    for _, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        battlefield_csp(model, cells_vars, sum_var)


def set_x_sum_skyscrapers_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A clue outside the grid gives the sum of the first X cells, where X would be the skyscraper clue outside the
    grid in that position.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.X_SUM_SKYSCRAPERS
    prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)

    for _, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        n = len(cells_vars)
        x = model.NewIntVar(1, n, f"{prefix} - skyscraper_count")
        skyscraper_csp(model, x, cells_vars)
        sum_result = x_sum_csp(model, cells_vars, x, f"{prefix}")
        model.Add(sum_result == sum_var)


def set_skyscrapers_constraints(model: PuzzleModel,
                                puzzle: Puzzle):
    """
    A clue outside the grid indicates the number of skyscrapers seen from that side.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.SKYSCRAPERS
    # prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for _, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        n = len(cells_vars)
        skyscraper_var = model.get_or_set_shared_var(
            value, 0, n, cell.format_cell())

        if isinstance(skyscraper_var, IntVar) and skyscraper_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), skyscraper_var)

        skyscraper_csp(model, skyscraper_var, cells_vars)


def set_broken_x_sum_constraints(model: PuzzleModel,
                                 puzzle: Puzzle):
    """
    A clue outside the grid indicates the sum of the first (X-1) or (X+1) digits from that side, where X is the
    digit in the first cell from that side.

    :param shared_vars:
    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.BROKEN_X_SUM
    # prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)

    for _, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        x0 = cells_vars[0]
        broken_x_sum_csp(model, cells_vars, sum_var, x0)


def set_x_index_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Clues outside the grid indicates the digit which has to be placed in the Xth cell in the corresponding direction,
    where X is the 1st digit in their row/column seen from the side of the clue.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.X_INDEX
    prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for i, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        digit_var = model.get_or_set_shared_var(
            value, min_digit, max_digit, cell.format_cell())

        if isinstance(digit_var, IntVar) and digit_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), digit_var)

        index = model.NewIntVar(0, max_digit - 1, f"{prefix}_{i} - index")
        model.AddElement(index, cells_vars, digit_var)
        model.Add(index == cells_vars[0] - 1)


def set_first_seen_odd_even_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A clue outside a row or column tells you the first odd (if the clue is odd) or even (if the clue is even) digit
    that appears in that row/column from the direction of the clue.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.FIRST_SEEN_ODD_EVEN
    prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for i, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        value_var = model.get_or_set_shared_var(
            value, min_digit, max_digit, cell.format_cell())

        mod_target = model.NewIntVar(0, 1, f"{prefix}_{i}: mod_target")
        model.AddModuloEquality(mod_target, value_var, 2)
        first_bools = find_first_mod_target(model, cells_vars, 2, mod_target)

        for j, var in enumerate(cells_vars):
            model.Add(var == value_var).OnlyEnforceIf(first_bools[j])


def set_rising_streak_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A number outside the grid indicates there is a streak of AT LEAST that many increasing, consecutive digits in the
    row or column in that direction (e.g. a number above the grid indicates a downward streak in that column).

    For instance, the row '214678935' has a maximal streak of 4 digits to the right (6789)
    and 2 digits to the left (21).

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.RISING_STREAK
    # prefix = f"{key.value}"
    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    # n_rows = puzzle.grid.nRows
    # n_cols = puzzle.grid.nCols
    # ub = max(n_rows, n_cols)

    for _, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        n = len(cells_vars)
        streak_var = model.get_or_set_shared_var(
            value, 1, n, cell.format_cell())

        if isinstance(streak_var, IntVar) and streak_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), streak_var)

        rising_streak_csp(model, cells_vars, streak_var)


def set_row_or_column_rank_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Considering all rows and columns as 9-digit numbers read from the direction of the clue and ranked from lowest (1)
    to highest (36), a clue represents where in the ranking that row/column lies.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.ROW_OR_COLUMN_RANK
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    n_rows = grid.nRows
    n_cols = grid.nCols
    n_numbers = 2 * n_rows + 2 * n_cols

    # create a dictionary with each number var and their rank var, key = outside cell index
    numbers_and_rank_dict: dict[tuple[int, int],
                                tuple[IntVar, IntVar]] = dict()

    for row in range(n_rows):
        row_cells = grid.getRow(row)
        n = len(row_cells)
        first_cell = row_cells[0]
        r0, c0 = first_cell.row, first_cell.col - 1
        number_var = model.NewIntVar(
            0, 10 ** (n + 1), f"{prefix} - ({r0}, {c0}) number")

        cells_vars = cells2vars(grid_vars, row_cells)
        multipliers = [10 ** (n - i - 1) for i in range(n)]
        model.Add(number_var == cp_model.LinearExpr.WeightedSum(
            cells_vars, multipliers))
        rank_var = model.NewIntVar(
            1, n_numbers, f"{prefix} - ({r0}, {c0}) rank")
        numbers_and_rank_dict[(r0, c0)] = (number_var, rank_var)

        row_cells.reverse()
        first_cell = row_cells[0]
        r0, c0 = first_cell.row, first_cell.col + 1
        number_var = model.NewIntVar(
            0, 10 ** (n + 1), f"{prefix} - ({r0}, {c0}) number")
        cells_vars = cells2vars(grid_vars, row_cells)
        multipliers = [10 ** (n - i - 1) for i in range(n)]
        model.Add(number_var == cp_model.LinearExpr.WeightedSum(
            cells_vars, multipliers))
        rank_var = model.NewIntVar(
            1, n_numbers, f"{prefix} - ({r0}, {c0}) rank")
        numbers_and_rank_dict[(r0, c0)] = (number_var, rank_var)

    for col in range(n_cols):
        col_cells = grid.getCol(col)
        n = len(col_cells)
        first_cell = col_cells[0]
        r0, c0 = first_cell.row - 1, first_cell.col
        number_var = model.NewIntVar(
            0, 10 ** (n + 1), f"{prefix} - ({r0}, {c0}) number")
        cells_vars = cells2vars(grid_vars, col_cells)
        multipliers = [10 ** (n - i - 1) for i in range(n)]
        model.Add(number_var == cp_model.LinearExpr.WeightedSum(
            cells_vars, multipliers))
        rank_var = model.NewIntVar(
            1, n_numbers, f"{prefix} - ({r0}, {c0}) rank")
        numbers_and_rank_dict[(r0, c0)] = (number_var, rank_var)

        col_cells.reverse()
        first_cell = col_cells[0]
        r0, c0 = first_cell.row + 1, first_cell.col
        number_var = model.NewIntVar(
            0, 10 ** (n + 1), f"{prefix} - ({r0}, {c0}) number")
        cells_vars = cells2vars(grid_vars, col_cells)
        multipliers = [10 ** (n - i - 1) for i in range(n)]
        model.Add(number_var == cp_model.LinearExpr.WeightedSum(
            cells_vars, multipliers))
        rank_var = model.NewIntVar(
            1, n_numbers, f"{prefix} - ({r0}, {c0}) rank")
        numbers_and_rank_dict[(r0, c0)] = (number_var, rank_var)

    # compute ranks
    for coords, val in numbers_and_rank_dict.items():
        number_var, rank_var = val
        bools: list[IntVar] = []
        for coords2, val2 in numbers_and_rank_dict.items():
            if coords == coords2:
                continue
            number_var2, _ = val2
            bool_var = model.NewBoolVar(
                f"{prefix} - {coords} > {coords2} bool")
            model.Add(number_var > number_var2).OnlyEnforceIf(bool_var)
            model.Add(number_var <= number_var2).OnlyEnforceIf(bool_var.Not())
            bools.append(bool_var)
        model.Add(rank_var == sum(bools) + 1)

    for _, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        number_and_rank = numbers_and_rank_dict.get((cell.row, cell.col))
        if number_and_rank is None:
            warnings.warn(
                f"Cell ({cell.row, cell.row,}) not in rank. Could be a problem.")
            continue

        number_var, rank_var = number_and_rank
        rank_value_var = model.get_or_set_shared_var(
            value, 1, n_numbers, cell.format_cell())

        if number_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), number_var)

        model.Add(rank_var == rank_value_var)


def set_x_sum_region_borders_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A clue outside the grid gives the sum of the first M digits from that direction, where M is the number of region
    borders in that row/column.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.X_SUM_REGION_BORDERS
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)
    regions_grid = get_or_set_unknown_regions_grid(
        model, puzzle)

    for i, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)
        region_vars = cells2vars(regions_grid, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        count_borders = count_transitions_csp(
            model, region_vars, f"{prefix}_{i}")
        sum_result = x_sum_csp(model, cells_vars, count_borders,
                               f"{prefix}_{i} - count_borders")
        model.Add(sum_result == sum_var)


def set_yin_yang_sum_of_shaded_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers outside the grid indicate the sum of the digits in shaded cells in the corresponding row/column.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideEdgeConstraintsE.OUTSIDE_EDGE_YIN_YANG_SUM_OF_SHADED
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    ub = sum(puzzle.valid_digits)
    yin_yang_grid = get_or_set_yin_yang_constraint(
        model, puzzle)

    for i, (cell, direction, value) in enumerate(genOutsideEdgeConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)
        yin_yang_vars = cells2vars(yin_yang_grid, cells)

        sum_var = model.get_or_set_shared_var(value, 0, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        masked_sum = masked_sum_csp(
            model, cells_vars, yin_yang_vars, f"{prefix}_{i}")
        model.Add(masked_sum == sum_var)


def set_outside_edge_constraints(model: PuzzleModel, puzzle: Puzzle):
    set_sandwich_sum_constraints(model, puzzle)
    set_x_sums_constraints(model, puzzle)
    set_shortsighted_x_sum_constraints(model, puzzle)
    set_shifted_x_sum_constraints(model, puzzle)
    set_battlefield_constraints(model, puzzle)
    set_x_sum_skyscrapers_constraints(model, puzzle)
    set_skyscrapers_constraints(model, puzzle)
    set_broken_x_sum_constraints(model, puzzle)
    set_x_index_constraints(model, puzzle)

    set_first_seen_odd_even_constraints(model, puzzle)
    set_rising_streak_constraints(model, puzzle)
    set_row_or_column_rank_constraints(model, puzzle)

    set_x_sum_region_borders_constraints(model, puzzle)
    set_yin_yang_sum_of_shaded_constraints(model, puzzle)
    # set_skycagers_skyscrapers_constraints(model, puzzle)
