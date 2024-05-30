
from puzzlesolver.Puzzle.ConstraintEnums import LineConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.LineConstraints.utils import genLineConstraintProperties
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import between_line_csp, modulo_count_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cells2vars
from puzzlesolver.Puzzle2model.BoolConstraints.puzzle_values_modifiers import get_or_set_doublers_grid
from puzzlesolver.utils.ParsingUtils import parse_int


def set_between_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits on a green line must be numerically in between the two circled cells at the line's ends.

    Args:
        model (PuzzleModel): _description_
        puzzle (Puzzle): _description_
    """
    key = LineConstraintsE.BETWEEN_LINE
    prefix = f"{key.value}"

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        cell1, cell2 = cells[0], cells[-1]
        between_line_csp(
            model, cells_vars, f"{prefix}_{i} - {cell1.format_cell()}-{cell2.format_cell()}")


def set_product_of_ends_equals_sum_of_line_constraints(model: PuzzleModel, puzzle: Puzzle):

    prefix = f"product_of_ends_equals_sum_of_line"
    max_digit = max(puzzle.valid_digits)

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.PRODUCT_OF_ENDS_EQUALS_SUM_OF_LINE)):
        end1 = cells_vars[0]
        end2 = cells_vars[-1]
        middle_vars = cells_vars[1:-1]

        product = model.NewIntVar(
            0, max_digit ** 2, f"{prefix}_{i}: product")
        model.AddMultiplicationEquality(product, [end1, end2])
        model.Add(product == sum(middle_vars))


def set_doublers_between_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.DOUBLERS_BETWEEN_LINE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    get_or_set_doublers_grid(model, puzzle)
    doubled_values_grid = model.grid_vars_dict["doubled_values_grid"]

    for i, (cells, _, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        doubled_line_values = cells2vars(doubled_values_grid, cells)
        between_line_csp(model, doubled_line_values, f"{prefix}_{i}")


def set_lockout_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits on the diamond endpoints of a purple line must have a difference of at least 4 and the remaining digits on
    the line cannot be between or equal to the digits on the endpoints.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.LOCKOUT_LINE
    prefix = f"{key.value}"

    max_digit = max(puzzle.valid_digits)
    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        end1 = cells_vars[0]
        end2 = cells_vars[-1]
        middle_vars = cells_vars[1:-1]

        value2 = parse_int(value)
        value2 = value2 if value2 is not None else 4

        target = model.NewIntVar(0, max_digit, f"{prefix}_{i}: abs_target")
        model.AddAbsEquality(target, end1 - end2)
        model.Add(target >= value2)

        for j, middle_var in enumerate(middle_vars):
            b = model.NewBoolVar(
                f'{prefix}_{i} - b_{j}')
            model.Add(middle_var < end1).OnlyEnforceIf(b)
            model.Add(middle_var < end2).OnlyEnforceIf(b)
            model.Add(middle_var > end2).OnlyEnforceIf(b.Not())
            model.Add(middle_var > end1).OnlyEnforceIf(b.Not())


def set_tightrope_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Each line has two circles. Both circle cells have the same value and that value does not repeat along the line
    connecting them. Each pair has a unique value, i.e, other tightropes cannot repeat the same value in a circle.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.TIGHTROPE_LINE

    for _, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        end1 = cells_vars[0]
        end2 = cells_vars[-1]
        middle_vars = cells_vars[1:-1]

        model.Add(end1 == end2)
        for var in middle_vars:
            model.Add(end1 != var)


def set_double_arrow_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The sum of the digits on the line must equal the sum of the digits in its end circles.
    Digits may repeat if allowed by other rules.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.DOUBLE_ARROW_LINE

    for _, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        end1 = cells_vars[0]
        end2 = cells_vars[-1]
        middle_vars = cells_vars[1:-1]

        model.Add(sum([end1, end2]) == sum(middle_vars))


def set_parity_count_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Each line has two circles. One of these circles gives the total number of odd digits on the line,
    and the other circle gives the total number of even digits on the line.
    Both of these totals include the digits in the circles. For each line, the solver must determine which
    circle counts the even digits and which counts the odd digits.
    Digits may repeat along a line if allowed by the other rules.

    Args:
        model (PuzzleModel): _description_
        puzzle (Puzzle): _description_
    """

    key = LineConstraintsE.PARITY_COUNT_LINE
    prefix = f"{key.value}"

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        # cells_vars = list(set(cells_vars))
        n = len(cells_vars)

        count_odd = model.NewIntVar(0, n, f"{prefix}_{i} - count_odd")
        count_even = modulo_count_csp(model, 0, 2, cells_vars, f"{prefix}_{i}")
        model.Add(count_odd == n - count_even)

        start_cell_var = cells_vars[0]
        end_cell_var = cells_vars[-1]

        b = model.NewBoolVar(f"{prefix}_{i} - bool_counts_even")
        count_equal = model.NewBoolVar(
            f"{prefix}_{i} - count_even == count_odd")
        model.Add(count_even == count_odd).OnlyEnforceIf(count_equal)
        model.Add(count_even != count_odd).OnlyEnforceIf(count_equal.Not())

        model.Add(start_cell_var == count_even).OnlyEnforceIf(b)
        model.Add(start_cell_var == count_odd).OnlyEnforceIf(b.Not())
        model.Add(end_cell_var == count_even).OnlyEnforceIf(b.Not())
        model.Add(end_cell_var == count_odd).OnlyEnforceIf(b)

        model.Add(b == 0).OnlyEnforceIf(count_equal)


def set_doublers_double_arrow_constraints(model: PuzzleModel, puzzle: Puzzle):
    """

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.DOUBLERS_DOUBLE_ARROW_LINE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    _, doublers_grid = get_or_set_doublers_grid(
        model, puzzle)

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        line_doublers_vars = cells2vars(doublers_grid, cells)
        # scalar product
        n = len(cells_vars)
        t = [model.NewIntVar(min_digit, 2 * max_digit,
                             f"{prefix}_{i} - t_{j}") for j in range(n)]
        for j in range(n):
            model.AddMultiplicationEquality(
                t[j], [cells_vars[j], line_doublers_vars[j]])

        end1 = t[0]
        end2 = t[-1]
        middle_vars = t[1:-1]

        model.Add(sum([end1, end2]) == sum(middle_vars))
