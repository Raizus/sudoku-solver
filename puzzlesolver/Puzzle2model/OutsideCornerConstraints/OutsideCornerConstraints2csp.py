
from puzzlesolver.Puzzle.Cell import split_line_into_regions
from puzzlesolver.Puzzle.ConstraintEnums import OutsideCornerConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OutsideCornerConstraints.utils import genOutsideCornerConstraintProperties
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import compute_multiplication_domain, masked_sum_csp, count_vars, multiplication_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, cells2vars
from ortools.sat.python.cp_model import IntVar

from puzzlesolver.Puzzle2model.BoolConstraints.puzzle_values_modifiers import get_or_set_negators_grid
from puzzlesolver.utils.ParsingUtils import look_and_say_parse_string, parse_int


def set_little_killer_sum_constraints(model: PuzzleModel,
                                      puzzle: Puzzle):
    """
    A clue with an arrow outside the grid shows the sum of the numbers along the indicated diagonal.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    # prefix = f"little_killer_sum"
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for _, (cell, direction, value) in enumerate(genOutsideCornerConstraintProperties(model, puzzle, OutsideCornerConstraintsE.LITTLE_KILLER_SUM)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        n = len(cells_vars)
        ub = n*max_digit
        # value = value if value is not None and len(
        #     value) else cell.format_cell()
        sum_var = model.get_or_set_shared_var(
            value, min_digit, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        model.Add(sum(cells_vars) == sum_var)


def set_x_omit_little_killer_sum_constraints(model: PuzzleModel,
                                             puzzle: Puzzle):
    """
    Numbers outside the grid indicate the sum of the digits along the indicated diagonal while omitting the Xth digit
    from the sum, where X is the digit in the first cell along the indicated diagonal. Note: N cannot be larger than
    the length of the diagonal.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    prefix = f"x_omit_little_killer_sum"
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for i, (cell, direction, value) in enumerate(genOutsideCornerConstraintProperties(model, puzzle, OutsideCornerConstraintsE.X_OMIT_LITTLE_KILLER_SUM)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        n = len(cells_vars)
        ub = (n-1)*max_digit
        sum_var = model.get_or_set_shared_var(
            value, min_digit, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        x = cells_vars[0]
        bools = [model.NewBoolVar(
            f"{prefix}_{i} - bool_{cell.format_cell()}") for _, cell in enumerate(cells)]
        for j, bool_var in enumerate(bools):
            model.Add(x == j + 1).OnlyEnforceIf(bool_var.Not())
            model.Add(x != j + 1).OnlyEnforceIf(bool_var)

            masked_sum = masked_sum_csp(
                model, cells_vars, bools, f"{prefix}_{i}")
            model.Add(masked_sum == sum_var)


def set_little_killer_region_sum_product_constraints(model: PuzzleModel,
                                                     puzzle: Puzzle):
    """
    Clues outside the grid give the multiplication of the box sums that the diagonal passes through. Eg a 1000 clue on
    the SW-NE diagonal at R0C10 means that (R1C9 + R2C8 + R3C7) * (R4C6 + R5C5 + R6C4) * (R7C3 + R8C2 + R9C1) = 1000

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"little_killer_region_sum_product"
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for i, (cell, direction, value) in enumerate(genOutsideCornerConstraintProperties(model, puzzle, OutsideCornerConstraintsE.LITTLE_KILLER_REGION_SUM_PRODUCT)):
        cells = grid.getCellsInDirection(cell, direction)

        regions = split_line_into_regions(cells)

        sum_vars: list[IntVar] = []
        domains: list[tuple[int, int]] = []

        for j, cell_region in enumerate(regions):
            cell_region_vars = cells2vars(grid_vars, cell_region)
            n2 = len(cell_region_vars)
            lb, ub = min_digit, max_digit*n2
            sum_var = model.NewIntVar(
                lb, ub, f"{prefix}_{i} - segment_{j} - sum")
            model.Add(sum(cell_region_vars) == sum_var)
            sum_vars.append(sum_var)
            domains.append((lb, ub))

        lb, ub = compute_multiplication_domain(domains)

        product_var_target = model.get_or_set_shared_var(
            value, lb, ub, cell.format_cell())

        product_var = multiplication_csp(
            model, sum_vars, f"{prefix}_{i} - product")
        model.Add(product_var == product_var_target)


def set_little_killer_look_and_say_constraints(model: PuzzleModel,
                                               puzzle: Puzzle):
    """
    A clue outside the grid should be read as a 'look-and-say' number. Each number says which digits are in the
    respective diagonal. Eg if a diagonal clue is 1221, this means there is one 2 and two 1s in the indicated diagonal.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"little_killer_look_and_say"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for i, (cell, direction, value) in enumerate(genOutsideCornerConstraintProperties(model, puzzle, OutsideCornerConstraintsE.LITTLE_KILLER_LOOK_AND_SAY)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)

        if value is None:
            continue

        counts = look_and_say_parse_string(value)
        for value, count in counts.items():
            value = parse_int(value)
            if value is None:
                continue
            name = f"{prefix}_{i} - value={value}, count={count}"
            count_var = count_vars(model, cells_vars, int(value), name)
            model.Add(count_var == count)


def set_negators_little_killer_sum_constraints(model: PuzzleModel,
                                               puzzle: Puzzle):
    """
    Digits along indicated diagonals must add to the indicated total. Repeats are permitted along such diagonals.
    A digit in a negator cell must be subtracted rather than added to achieve the given diagonal total.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = OutsideCornerConstraintsE.NEGATORS_LITTLE_KILLER_SUM
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    negators_bool_grid, _ = get_or_set_negators_grid(model, puzzle)

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    min_val = min(-min_digit, min_digit, -max_digit, max_digit)
    max_val = max(-min_digit, min_digit, -max_digit, max_digit)

    for i, (cell, direction, value) in enumerate(genOutsideCornerConstraintProperties(model, puzzle, key)):
        cells = grid.getCellsInDirection(cell, direction)
        cells_vars = cells2vars(grid_vars, cells)
        n = len(cells_vars)

        lb, ub = n*min_val, n*max_val
        sum_var = model.get_or_set_shared_var(
            value, lb, ub, cell.format_cell())

        if isinstance(sum_var, IntVar) and sum_var.name == cell.format_cell():
            grid_vars.setdefault((cell.row, cell.col), sum_var)

        negators_bools = cells2vars(negators_bool_grid, cells)

        # scalar product
        n = len(cells_vars)
        t = [model.NewIntVar(
            min_val, max_val, f"{prefix}_{i}: t_{j}") for j in range(n)]
        for j in range(n):
            model.Add(t[j] == cells_vars[j]).OnlyEnforceIf(
                negators_bools[j].Not())
            model.Add(t[j] == -1 * cells_vars[j]
                      ).OnlyEnforceIf(negators_bools[j])

        model.Add(sum(t) == sum_var)


def set_outside_corner_constraints(model: PuzzleModel, puzzle: Puzzle):
    set_little_killer_sum_constraints(model, puzzle)
    set_x_omit_little_killer_sum_constraints(model, puzzle)
    set_little_killer_region_sum_product_constraints(model, puzzle)
    set_little_killer_look_and_say_constraints(model, puzzle)

    set_negators_little_killer_sum_constraints(model, puzzle)
