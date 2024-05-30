
from itertools import combinations
from puzzlesolver.Puzzle.Cell import split_line_into_regions
from puzzlesolver.Puzzle.ConstraintEnums import GlobalRegionConstraintsE, LineConstraintsE, LocalConstraintsModifiersE, SimpleGlobalConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.LineConstraints.utils import genLineConstraintProperties
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownEmptyCellsConstraints2csp import get_or_set_unknown_empty_cells_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownRegionsConstraints2csp import get_or_set_unknown_regions_grid
from puzzlesolver.Puzzle2model.OtherConstraints.YinYangConstraints2csp import get_or_set_yin_yang_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import are_all_equal_csp, are_consecutive_csp, compare_multisets_csp, compute_multiplication_domain, count_transitions_csp, count_unique_values, count_vars, cycle_order_csp, distance_csp, factors_csp, increasing_strict, is_entropic_line_csp, is_modular_line_csp, is_ratio_1_r_csp, is_renban_csp, is_unimodular_csp, is_whispers_csp, member_of, multiplication_csp, nonconsecutive_csp, palindrome_csp, region_sum_with_unknown_regions_csp, regular_distance_csp, reif2, renban_csp, segment_by_transitions_csp, whispers_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import PRIME_LIST, cell2var, cells2vars
from puzzlesolver.Puzzle2model.puzzle_model_types import GridVars
from puzzlesolver.Puzzle2model.BoolConstraints.puzzle_values_modifiers import get_or_set_cold_cells_constraint, get_or_set_doublers_grid, get_or_set_hot_cells_constraint
from puzzlesolver.utils.ListUtils import generate_list_kmers, get_left_side, get_right_side
from ortools.sat.python.cp_model import IntVar

from puzzlesolver.utils.ParsingUtils import parse_int


def set_lines_do_not_pass_through_empty_cells(model: PuzzleModel, puzzle: Puzzle,
                                              line_key: LineConstraintsE):

    # prefix = f"{line_key.value} - does_not_pass_through_empty_cells"
    key2 = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key2, False)
    if not unknown_empty_cells:
        return

    filled_cells_grid = get_or_set_unknown_empty_cells_constraint(
        model, puzzle)

    sum_line_cells = set(cell for
                         (cells, _, _) in genLineConstraintProperties(model, puzzle, line_key) for cell in cells)

    for cell in sum_line_cells:
        filled_cell_var = cell2var(filled_cells_grid, cell)
        model.Add(filled_cell_var == 1)


def set_superfuzzy_arrow_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Draw a circle in one of the cells of each line. The digit in the circle gives the sum of the digits towards
    (each of) the remaining end(s) of the line.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"superfuzzy_arrow"

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.SUPERFUZZY_ARROW)):
        bools = [model.NewBoolVar(f"{prefix}_{i} - b_{j}")
                 for j, _ in enumerate(cells)]

        for j, var in enumerate(cells_vars):
            left_side = get_left_side(cells_vars, j)
            right_side = get_right_side(cells_vars, j)
            if left_side:
                model.Add(var == sum(left_side)).OnlyEnforceIf(bools[j])
            if right_side:
                model.Add(var == sum(right_side)).OnlyEnforceIf(bools[j])
        model.AddExactlyOne(bools)


def set_renban_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Number along a purple line form a set of non-repeating consecutive digits (which can be in any order).

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"renban_line"

    start_end: dict[int, tuple[IntVar, IntVar]] = dict()
    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.RENBAN_LINE)):
        cell_vars2 = list(set(cells_vars))
        start, end = renban_csp(model, cell_vars2, f"{prefix}_{i}")
        start_end[i] = (start, end)

    all_renbans_are_distinct = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.DISTINCT_RENBANS)
    if all_renbans_are_distinct:
        distinct_lengths = list(set([len(set(cells))
                                for (cells, _, _) in genLineConstraintProperties(model, puzzle, LineConstraintsE.RENBAN_LINE)]))
        for length in distinct_lengths:
            renbans_idx_with_length = [i for i, (cells, _, _) in enumerate(genLineConstraintProperties(
                model, puzzle, LineConstraintsE.RENBAN_LINE)) if len(cells) == length]

            combinations_gen = combinations(renbans_idx_with_length, 2)
            for group in combinations_gen:
                (i, j) = group
                start1, end1 = start_end[i]
                start2, end2 = start_end[j]

                b = model.NewBoolVar(
                    f"{prefix} - all_renbans_are_distinct - bool: renban_{i} != renban_{j}")
                model.Add(start2 < start1).OnlyEnforceIf(b)
                model.Add(end2 < end1).OnlyEnforceIf(b)

                model.Add(start2 > start1).OnlyEnforceIf(b.Not())
                model.Add(end2 > end1).OnlyEnforceIf(b.Not())


def set_double_renban_line_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Number along a purple line form 2 sets of non-repeating consecutive digits (which can be in any order). Both sets must have the same length

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"double_renban_line"
    lb = min(puzzle.valid_digits)
    ub = max(puzzle.valid_digits)

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.DOUBLE_RENBAN_LINE)):
        cell_vars2 = list(set(cells_vars))
        set_length = len(cell_vars2) // 2

        set_1_vars = [model.NewIntVar(
            lb, ub, f"{prefix}_{i} - set_1, var_{j}") for j in range(set_length)]
        set_2_vars = [model.NewIntVar(
            lb, ub, f"{prefix}_{i} - set_1, var_{j}") for j in range(set_length)]

        model.Add(set_1_vars[0] <= set_2_vars[0])
        for k, _set in enumerate([set_1_vars, set_2_vars]):
            regular_distance_csp(model, _set, 1)
            for j, var in enumerate(_set):
                member_of(model, cell_vars2, var,
                          f"{prefix}_{i} - set_{k}, var_{j} - member_of_line")
        is_equal = compare_multisets_csp(
            model, set_1_vars + set_2_vars, cell_vars2, f"{prefix}_{i}")
        model.Add(is_equal == 1)


def set_n_consecutive_renban_line_constraints(model: PuzzleModel,
                                              puzzle: Puzzle):
    """
    Every string of N consecutive cells along the large purple line / loop must contain a set of n (default = 5) consecutive digits in
    any order without repeats.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"n_consecutive_renban_line"

    for i, (cells, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.N_CONSECUTIVE_RENBAN_LINE)):
        is_closed = cells[0] == cells[-1]
        n = parse_int(value)
        n = n if n is not None else 5

        for group in generate_list_kmers(cells_vars, n, is_closed):
            assert len(group) == n
            renban_csp(model, group, f"{prefix}_{i}")


def set_renrenbanban_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    A purple line contains a set of consecutive digits. Any digit appearing on a line MUST appear on that line at
    least twice.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"renrenbanban"

    valid_digits = puzzle.valid_digits
    lb = min(valid_digits)
    ub = max(valid_digits)

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.RENRENBANBAN_LINE)):
        cell_vars2 = list(set(cells_vars))

        unique_count = count_unique_values(model, cell_vars2, f"{prefix}_{i}")
        start = model.NewIntVar(lb, ub, f'{prefix}_{i} - start')
        end = model.NewIntVar(lb, ub, f'{prefix}_{i} - end')
        model.Add(end == start + unique_count - 1)

        for j, var in enumerate(cell_vars2):
            count_j = count_vars(model, cell_vars2, var,
                                 f"{prefix}_{i} - count_var_{j}")
            model.Add(count_j >= 2)
            model.Add(start <= var)
            model.Add(var <= end)


def set_entropic_line_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Along orange lines, each segment of three cells must contain one low digit (1,2,3), one medium digit (4,5,6) and
    one high digit (7,8,9). Digits may repeat along these lines if allowed by other rules.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"entropic_line"

    entropic_groups = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ENTROPIC_LINE)):
        is_entropic = is_entropic_line_csp(
            model, cells_vars, entropic_groups, f"{prefix}_{i}")  # type: ignore
        model.Add(is_entropic == 1)


def set_entropic_or_modular_line_constraints(model: PuzzleModel,
                                             puzzle: Puzzle):
    """
    **Entropic Or Modular Line:** A blue line is either an Entropic Line or a Modular Line:

    - **Entropic Lines:** Along an entropic line any run of three cells contains exactly one low {1,2,3},
    one medium {4,5,6}, and one high {7,8,9} digit.


    - **Modular Lines:** Along a modular line, the digits in any run of three cells must all have different remainders
    under division by 3. (ie So one digit must be from the set {1,4,7}, one from {2,5,8} and one from {3,6,9}).

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"entropic_or_modular_line"

    entropic_groups = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    mod = 3

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ENTROPIC_OR_MODULAR_LINE)):

        is_entropic = is_entropic_line_csp(
            model, cells_vars, entropic_groups, f"{prefix}_{i}")  # type: ignore
        is_modular = is_modular_line_csp(
            model, cells_vars, mod, f"{prefix}_{i}")
        model.Add(sum([is_entropic, is_modular]) >= 1)


def set_high_low_oscillator_line_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Along a red oscillator line digits alternate being high (more than 5) and low (less than 5).

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"high_low_oscillator_line"

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.HIGH_LOW_OSCILLATOR_LINE)):

        bools: list[IntVar] = []
        for j in range(0, 2):
            group_vars = cells_vars[j::2]

            bool_var = model.NewBoolVar(f"{prefix}_{i} - bool group_{j} < 5")
            bools.append(bool_var)

            for _, var in enumerate(group_vars):
                model.Add(var < 5).OnlyEnforceIf(bool_var)
                model.Add(var > 5).OnlyEnforceIf(bool_var.Not())

        if len(bools) == 2:
            model.Add(bools[0] != bools[1])


def set_odd_even_oscillator_line_constraints(model: PuzzleModel,
                                             puzzle: Puzzle):
    """
    Digits along a blue line alternate between odd and even numbers.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"odd_even_oscillator_line"

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ODD_EVEN_OSCILLATOR_LINE)):

        targets: list[IntVar] = []
        for j in range(0, 2):
            group_vars = cells_vars[j::2]

            target = model.NewIntVar(
                0, 1, f"{prefix}_{i} - target_{j}")
            targets.append(target)
            for _, var in enumerate(group_vars):
                model.AddModuloEquality(target, var, 2)

        model.AddAllDifferent(targets)


def set_whispers_line_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Adjacent numbers along a green line must have a difference of at least 5.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"whispers_line"

    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.WHISPERS_LINE)):
        value = parse_int(value)
        value = value if value is not None else 5

        whispers_csp(model, cells_vars, value, f"{prefix}_{i}")


def set_unique_values_line_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Along a grey line there are no repeated digits.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    # prefix = f"unique_values_line"

    for _, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.UNIQUE_VALUES_LINE)):
        cells_vars = list(set(cells_vars))
        model.AddAllDifferent(cells_vars)


def set_maximum_adjacent_difference_line_constraints(model: PuzzleModel,
                                                     puzzle: Puzzle):
    """
    Adjacent cells on an orange line must contain digits that have difference of at most X (default is 2).

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"maximum_adjacent_difference_line"

    for i, (cells, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.MAXIMUM_ADJACENT_DIFFERENCE_LINE)):
        value = parse_int(value)
        value = value if value is not None else 5
        is_closed = cells[0] == cells[-1]

        for j, (var1, var2) in enumerate(generate_list_kmers(cells_vars, 2, is_closed)):
            dist_var = distance_csp(
                model, var1, var2, f"{prefix}_{i} - distance_{j}")
            model.Add(dist_var <= value)


def set_adjacent_multiples_line_constraints(model: PuzzleModel,
                                            puzzle: Puzzle):
    """
    For any two adjacent digits along a gold line, one must be divisible by the other.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"adjacent_multiples_line"

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ADJACENT_MULTIPLES_LINE)):

        is_closed = cells[0] == cells[-1]
        for j, (var1, var2) in enumerate(generate_list_kmers(cells_vars, 2, is_closed)):
            factors_csp(model, var1, var2, f"{prefix}_{i} - factors_{j}")


def set_at_least_x_line_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Adjacent digits along a line must sum to at least X (10 by default) or more.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    # prefix = f"at_least_x_line"

    for _, (cells, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.AT_LEAST_X_LINE)):
        value = parse_int(value)
        value = value if value is not None else 10

        is_closed = cells[0] == cells[-1]

        for _, (var1, var2) in enumerate(generate_list_kmers(cells_vars, 2, is_closed)):
            model.Add(sum([var1, var2]) >= value)


def set_thermometer_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Numbers along a thermometer must increase from the bulb end.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    # prefix = f"thermometer"

    for _, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.THERMOMETER)):
        increasing_strict(model, cells_vars)


def set_palindrome_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Gray lines are palindromes, reading the same when reversed. e.g. 12321 or 4554.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"palindrome"

    for _, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.PALINDROME)):

        palindrome_csp(model, cells_vars)

    palindromes_only_have_2_digits = False
    # palindromes_only_have_2_digits = puzzle.bool_constraints.get(BoolConstraints.PALINDROMES_ONLY_HAVE_TWO_DIGITS,
    #                                                              False)
    if palindromes_only_have_2_digits:
        for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.PALINDROME)):
            unique_count = count_unique_values(
                model, cells_vars, f"{prefix}_{i} - palindromes_only_have_2_digits")
            model.Add(unique_count == 2)


def set_region_sum_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers on a blue line have an equal sum N within each box the line passes through. If a line passes through the
    same box more than once, each individual segment of such a line within that box sums to N separately.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.REGION_SUM_LINE
    prefix = f"{key.value}"
    max_digit = max(puzzle.valid_digits)
    min_digit = min(puzzle.valid_digits)

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    unknown_regions = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.UNKNOWN_REGIONS, False)

    for i, (cells, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        l = len(set(cells_vars))
        sum_var = model.get_or_set_shared_var(
            value, min_digit, l * max_digit, f"{prefix} {i}: sum")

        if not unknown_regions:
            regions = split_line_into_regions(cells)
            for cells_region in regions:
                region_vars = cells2vars(grid_vars, cells_region)
                model.Add(sum(region_vars) == sum_var)

        else:
            region_grid = get_or_set_unknown_regions_grid(model, puzzle)
            region_line_vars = cells2vars(region_grid, cells)

            # region sum line passes through more than 1 region (at least 1 region transition)
            count = count_transitions_csp(
                model, region_line_vars, f"{prefix} {i} - unknown_regions")
            model.Add(count >= 1)

            sum_var2 = region_sum_with_unknown_regions_csp(model, cells_vars, region_line_vars,
                                                           f"{prefix} {i} - unknown_regions")
            model.Add(sum_var == sum_var2)


def set_doublers_region_sum_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = LineConstraintsE.DOUBLERS_REGION_SUM_LINE
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    prefix = f"{key.value}"
    _, _ = get_or_set_doublers_grid(model, puzzle)
    doubled_values_grid = model.grid_vars_dict["doubled_values_grid"]

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    lb = min(min_digit, 2*min_digit)

    for i, (cells, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        l = len(set(cells_vars))
        sum_var = model.get_or_set_shared_var(
            value, lb, 2 * l * max_digit, f"{prefix}_{i}: sum")

        regions = split_line_into_regions(cells)
        for cells_region in regions:
            # region_vars = cells2vars(grid_vars, cells_region)
            region_values_vars = cells2vars(doubled_values_grid, cells_region)
            model.Add(sum(region_values_vars) == sum_var)


def set_red_carpet_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers along a red line must repeat in the same order when the carpet is 'rolled out' starting from the bulbed end.
    """

    # prefix = f"red_carpet"
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    for _, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.RED_CARPET)):
        cell1 = cells[0]
        cell2 = cells[1]
        dr, dc = cell2.row - cell1.row, cell2.col - cell1.col
        for j, (_, cell_var) in enumerate(zip(cells, cells_vars)):
            mapped_cell = puzzle.grid.getCell(
                cell1.row + dr * j, cell1.col + dc * j)
            if mapped_cell is None:
                continue
            mapped_cell_var = cell2var(grid_vars, mapped_cell)
            model.Add(cell_var == mapped_cell_var)


def set_repeated_digits_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    All digits appearing on an orange line are repeated on this line. The number of time each digit appears on a line
    is the same for all digits on the line (for example, if 2 appears three times on a line, every other digit on the
    line must also appear three times on it).
    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"repeated_digits_line"

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.REPEATED_DIGITS_LINE)):
        cells_vars = list(set(cells_vars))
        global_count = model.NewIntVar(
            2, len(cells_vars), f"{prefix}_{i}: count")

        for var in cells_vars:
            count = count_vars(model, cells_vars, var, f"{prefix}_{i} - {var}")
            model.Add(count == global_count)


def set_n_repeated_digits_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Each digit on the red line must appear N times on the line (default N = 2).

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"n_repeated_digits_line"

    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.N_REPEATED_DIGITS_LINE)):
        cells_vars = list(set(cells_vars))

        value = parse_int(value)
        value = value if value is not None else 2

        for var in cells_vars:
            count = count_vars(model, cells_vars, var, f"{prefix}_{i} - {var}")
            model.Add(count == value)


def set_sum_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits on a blue line sum to X.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.SUM_LINE
    prefix = f"{key.value}"

    max_digit = max(puzzle.valid_digits)
    min_digit = min(puzzle.valid_digits)

    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        cells_vars = list(set(cells_vars))
        l = len(cells_vars)
        lb = l * min_digit
        ub = l * max_digit

        sum_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix} {i}: sum")

        model.Add(sum(cells_vars) == sum_var)

    key2 = LocalConstraintsModifiersE.SUM_LINES_DO_NOT_PASS_THROUGH_EMPTY_CELLS
    constraint = puzzle.bool_constraints.get(key2, False)
    if constraint:
        set_lines_do_not_pass_through_empty_cells(model, puzzle, key)


def set_two_digit_sum_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Two-digit numbers along a line must sum to X.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    prefix = f"two_digit_sum_line"
    max_digit = max(puzzle.valid_digits)
    min_digit = min(puzzle.valid_digits)

    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.TWO_DIGIT_SUM_LINE)):
        max_val = (len(cells_vars) // 2) * (max_digit * 10 + max_digit)

        sum_var = model.get_or_set_shared_var(
            value, min_digit, max_val, f"{prefix}_{i}: sum")

        numbers_vars: list[IntVar] = []
        for j, k in enumerate(range(1, len(cells_vars), 2)):
            cell1_var = cells_vars[k-1]
            cell2_var = cells_vars[k]
            number_var = model.NewIntVar(
                10, 99, f"{prefix}_{i}: number_{j}")
            model.Add(10 * cell1_var + cell2_var == number_var)
            numbers_vars.append(number_var)
        model.Add(sum(numbers_vars) == sum_var)


def set_product_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The product of digits on a line is X.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.PRODUCT_LINE
    prefix = f"{key.value}"

    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        cells_vars = list(set(cells_vars))

        domains: list[tuple[int, int]] = []
        for var in cells_vars:
            (lb, ub) = var.Proto().domain
            domains.append((lb, ub))

        (plb, pub) = compute_multiplication_domain(domains)

        product_var = model.get_or_set_shared_var(
            value, plb, pub, f"{prefix} {i}: sum")

        product_result_var = multiplication_csp(model, cells_vars, f"{prefix}")
        model.Add(product_result_var == product_var)


def set_knabner_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Orange lines contain no repeated digits and no two digits on the same line can be consecutive.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    # prefix = f"knabner_line"

    for _, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.KNABNER_LINE)):
        cells_vars = list(set(cells_vars))

        model.AddAllDifferent(cells_vars)

        # no two digits in the line can be consecutive
        combinations_gen = combinations(cells_vars, 2)
        for group in combinations_gen:
            cell1_var, cell2_var = group
            nonconsecutive_csp(model, cell1_var, cell2_var)


def set_arithmetic_sequence_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits along a grey line must increase by the same amount, in the same direction.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"arithmetic_sequence_line"
    max_digit = max(puzzle.valid_digits)
    min_digit = min(puzzle.valid_digits)
    ub = max_digit - min_digit

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ARITHMETIC_SEQUENCE_LINE)):
        model.AddAllDifferent(cells_vars)

        target = model.NewIntVar(-ub, ub, f"{prefix}_{i} - diff")
        for j, cell1_var in enumerate(cells_vars[:-1]):
            cell2_var = cells_vars[j + 1]
            model.Add(cell2_var - cell1_var == target)


def set_modular_or_unimodular_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Lines are either modular or unimodular. On modular lines, every set of three sequential digits contains one digit
    from {1,4,7}, one from {2,5,8} and one from {3,6,9}. On unimodular lines, all digits are from the same class
    (ie all from {1,4,7} or all from {2,5,8} or all from {3,6,9}).

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"modular_or_unimodular_line"

    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.MODULAR_OR_UNIMODULAR_LINE)):
        value = value if value is not None and len(value) else "3"
        mod = parse_int(value)
        if mod is None:
            continue

        is_unimodular, _ = is_unimodular_csp(
            model, cells_vars, mod, f"{prefix}_{i}")
        is_modular = is_modular_line_csp(
            model, cells_vars, mod, f"{prefix}_{i}")
        model.AddBoolOr(is_modular, is_unimodular)


def set_modular_line_constraints(model: PuzzleModel,
                                 puzzle: Puzzle):
    """
    On modular lines, every set of three sequential digits contains one digit from {1,4,7}, one from {2,5,8}
    and one from {3,6,9}.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    prefix = f"modular_line"

    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.MODULAR_LINE)):
        value = value if value is not None and len(value) else "3"
        mod = parse_int(value)
        if mod is None:
            continue

        is_modular = is_modular_line_csp(
            model, cells_vars, mod, f"{prefix}_{i}")
        model.Add(is_modular == 1)


def set_unimodular_line_constraints(model: PuzzleModel,
                                    puzzle: Puzzle):
    """
    On modular lines, every set of three sequential digits contains one digit from {1,4,7}, one from {2,5,8}
    and one from {3,6,9}.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    prefix = f"modular_line"

    for i, (_, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.UNIMODULAR_LINE)):
        value = value if value is not None and len(value) else "3"
        mod = parse_int(value)
        if mod is None:
            continue

        is_modular, _ = is_unimodular_csp(
            model, cells_vars, mod, f"{prefix}_{i}")
        model.Add(is_modular == 1)


def set_xv_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Neighboring digits along a yellow line must sum either to 5 or 10.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"xv_line"

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.XV_LINE)):

        for j, var1 in enumerate(cells_vars[0:-1]):
            sum_var = model.NewIntVar(5, 10, f"{prefix}_{i} - sum_{j}")
            model.AddAllowedAssignments([sum_var], [(5,), (10,)])
            var2 = cells_vars[j + 1]
            model.Add(var1 + var2 == sum_var)


def set_renban_or_german_whispers_line_constraints(model: PuzzleModel,
                                                   puzzle: Puzzle):
    """
    An orange line is either 1) a sequence of non-repeating consecutive digits, in any order; or 2) a line on which
    neighbouring digits differ by at least 5.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"renban_or_german_whispers_line"

    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.RENBAN_OR_WHISPERS_LINE)):
        cells_vars2 = list(set(cells_vars))
        is_renban = is_renban_csp(
            model, cells_vars2, f"{prefix}_{i}")
        is_german_whispers = is_whispers_csp(model, cells_vars, 5)
        model.AddExactlyOne(is_renban, is_german_whispers)


def set_n_consecutive_fuzzy_sum_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    For every N (default N = 3) consecutive digits on a line, one of the digits has to be the sum of the others. For example, for N=3, 2-5-7, 6-9-3, and 8-4-4 are valid adjacent digits along a line.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"n_consecutive_fuzzy_sum_line"

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.N_CONSECUTIVE_FUZZY_SUM_LINE)):
        is_closed = cells[0] == cells[-1]
        n = 3

        for k, group_vars in enumerate(generate_list_kmers(cells_vars, n, is_closed)):
            bs = [model.NewBoolVar(
                f"{prefix}_{i} - group_{k} - bool_{i2}") for i2, _ in enumerate(group_vars)]
            model.AddExactlyOne(bs)
            for k, cell_var in enumerate(group_vars):
                other_vars = [var2 for j, var2 in enumerate(
                    group_vars) if j != k]
                model.Add(cell_var == sum(other_vars)).OnlyEnforceIf(bs[k])


def set_adjacent_cells_are_consecutive_or_ratio_line_constraints(model: PuzzleModel,

                                                                 puzzle: Puzzle):
    """
    Along lines, adjacent digits must be consecutive and/or in a ratio of 2:1.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"adjacent_cells_are_consecutive_or_ratio_line"

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ADJACENT_CELLS_ARE_CONSECUTIVE_OR_RATIO_LINE)):

        is_closed = cells[0] == cells[-1]

        for j, (var1, var2) in enumerate(generate_list_kmers(cells_vars, 2, is_closed)):
            is_ratio = is_ratio_1_r_csp(
                model, var1, var2, 2, f"{prefix}_{i} - is_ratio_{j}")
            are_consecutive = are_consecutive_csp(
                model, var1, var2, f"{prefix}_{i} - is_consecutive_{j}")

            model.AddBoolOr([is_ratio, are_consecutive])


def set_adjacent_sum_is_prime_line_constraints(model: PuzzleModel,
                                               puzzle: Puzzle):
    """
    Pairs of adjacent numbers on a line must sum to a prime number.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    max_digit = max(puzzle.valid_digits)
    prefix = f"adjacent_sum_is_prime_line"

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ADJACENT_CELL_SUM_IS_PRIME_LINE)):

        is_closed = cells[0] == cells[-1]

        for j, (var1, var2) in enumerate(generate_list_kmers(cells_vars, 2, is_closed)):
            sum_var_name = f"{prefix}_{i} - sum_{j}"
            sum_var = model.NewIntVar(0, max_digit * 2, sum_var_name)
            model.Add(var1 + var2 == sum_var)
            member_of(model, PRIME_LIST, sum_var, sum_var_name)


def set_adjacent_diff_at_least_x_or_sum_at_most_x_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Adjacent cells on a green line have a difference of at least X or a sum of at most X (default X = 5).

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    max_digit = max(puzzle.valid_digits)
    prefix = f"adjacent_diff_at_least_x_or_sum_at_most_x"

    for i, (cells, cells_vars, value) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ADJACENT_DIFF_IS_AT_LEAST_X_OR_ADJACENT_SUM_IS_AT_MOST_X_LINE)):

        is_closed = cells[0] == cells[-1]

        value = parse_int(value)
        if value is None:
            continue

        for j, (var1, var2) in enumerate(generate_list_kmers(cells_vars, 2, is_closed)):
            sum_var_name = f"{prefix}_{i} - sum_{j}"
            sum_var = model.NewIntVar(0, max_digit * 2, sum_var_name)
            model.Add(var1 + var2 == sum_var)

            diff_var_name = f"{prefix}_{i} - diff_{j}"
            diff_var = model.NewIntVar(0, max_digit, diff_var_name)
            model.AddAbsEquality(diff_var, var1 - var2)

            bool_var1 = reif2(model, sum_var <= value,
                              sum_var > value, f"{prefix}_{i} - group_{j}")
            bool_var2 = reif2(model, diff_var >= value,
                              diff_var < value, f"{prefix}_{i} - group_{j}")
            model.AddBoolOr(bool_var1, bool_var2)


def set_doublers_thermometer_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Values along a thermometer must increase from the bulb end. If a thermometer cell is a doubler it counts as twice
    its value for purposes of the thermometer.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """

    constraints_list = puzzle.tool_constraints.get(
        LineConstraintsE.DOUBLERS_THERMOMETER)
    if not len(constraints_list):
        return

    # prefix = f"doublers_thermometer"
    get_or_set_doublers_grid(model, puzzle)
    doubled_values_grid = model.grid_vars_dict["doubled_values_grid"]

    for _, (cells, _, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.DOUBLERS_THERMOMETER)):
        cells_values_vars = cells2vars(doubled_values_grid, cells)
        increasing_strict(model, cells_values_vars)


def set_hot_cold_thermometer_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Values along a thermometer must increase from the bulb end. If a thermometer cell is a doubler it counts as twice
    its value for purposes of the thermometer.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.HOT_COLD_THERMOMETER
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    prefix = f"{key.value}"
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    cold_cells_grid = get_or_set_cold_cells_constraint(model, puzzle)
    hot_cells_grid = get_or_set_hot_cells_constraint(model, puzzle)

    lb = min(puzzle.valid_digits)
    ub = max(puzzle.valid_digits)

    for i, (cells, _, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        ts: list[IntVar] = []
        for _, cell in enumerate(cells):
            cell_var = cell2var(grid_vars, cell)
            hot_var = cell2var(hot_cells_grid, cell)
            cold_var = cell2var(cold_cells_grid, cell)
            _t = model.NewIntVar(
                lb-1, ub+1, f"{prefix} {i} - {cell.format_cell()} value")
            ts.append(_t)
            model.Add(_t == cell_var + hot_var + cold_var)

        increasing_strict(model, ts)


def set_two_digit_thermometer_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Two-digit numbers along a thermometer must increase from the bulb end.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    prefix = f"two_digit_thermometer"

    numbers_vars_dict: dict[tuple[str, str], IntVar] = dict()
    for i, (_, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.TWO_DIGIT_THERMOMETER)):

        number_vars: list[IntVar] = []
        for j, k in enumerate(range(1, len(cells_vars), 2)):
            cell1_var, cell2_var = cells_vars[k - 1], cells_vars[k]
            number_var = model.NewIntVar(10, 99, f"{prefix}_{i}: number_{j}")
            model.Add(10 * cell1_var + cell2_var == number_var)
            numbers_vars_dict.setdefault(
                (cell1_var.name, cell2_var.name), number_var)
            number_vars.append(number_var)

        increasing_strict(model, number_vars)

    unique_numbers = \
        puzzle.bool_constraints.get(
            LocalConstraintsModifiersE.TWO_DIGIT_NUMBERS_DO_NOT_REPEAT_ON_TWO_DIGIT_THERMOS, False)

    if unique_numbers and len(numbers_vars_dict):
        number_vars = list(numbers_vars_dict.values())
        model.AddAllDifferent(number_vars)


def set_row_cycle_order_thermometers_constraints(model: PuzzleModel, puzzle: Puzzle):

    # prefix = f"row_cycle_order_thermometers"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    # max_digit = max(puzzle.valid_digits)

    for _, (cells, _, _) in enumerate(genLineConstraintProperties(model, puzzle, LineConstraintsE.ROW_CYCLE_THERMOMETER)):

        order_vars: list[IntVar] = []
        for j, cell in enumerate(cells):
            row = grid.getRow(cell.row)
            row_vars = cells2vars(grid_vars, row)
            order = cycle_order_csp(model, row_vars, cell.col)
            order_vars.append(order)
            model.Add(order == order_vars[j])

        increasing_strict(model, order_vars)


def set_yin_yang_region_sum_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Blue lines must have an equal sum N within each colour they pass through. If a blue line passes through a colour multiple times, each individual pass sums to N. All lines must cross colours at least once.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.YIN_YANG_REGION_SUM_LINE
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    prefix = f"yin_yang_region_sum_line"
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        yin_yang_line_vars = cells2vars(yin_yang_grid, cells)

        # All lines must cross colours at least once. (At least one shaded and one unshaded cell)
        member_of(model, yin_yang_line_vars, 0,
                  f"{prefix} - line_i - 0_is_member")
        member_of(model, yin_yang_line_vars, 1,
                  f"{prefix} - line_i - 1_is_member")

        region_sum_with_unknown_regions_csp(
            model, cells_vars, yin_yang_line_vars, f"{prefix}_{i}")


def set_californian_mountain_snake_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Yin yang rules apply. Along the red line, each run of cells with the same shading contains a non-repeating set of
    consecutive digits in any order. Along the red line, digits in each pair of adjacent cells with different shading
    must differ by at least 5.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.YIN_YANG_CALIFORNIAN_MOUNTAIN_SNAKE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid_vars = model.grid_vars_dict['cells_grid_vars']
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for i, (cells, cells_vars, _) in enumerate(genLineConstraintProperties(model, puzzle, key)):
        yin_yang_line_vars = cells2vars(yin_yang_grid, cells)

        # Along the red line, digits in each pair of adjacent cells with different shading must differ by at least 5.
        for cell1, cell2 in zip(cells, cells[1:]):
            yin_yang_var1 = cell2var(yin_yang_grid, cell1)
            yin_yang_var2 = cell2var(yin_yang_grid, cell2)
            cell1_var = cell2var(grid_vars, cell1)
            cell2_var = cell2var(grid_vars, cell2)

            name = f"{prefix}_{i} - dist = |{cell1.format_cell()}-{cell2.format_cell()}|"
            dist = distance_csp(model, cell1_var, cell2_var, name)

            shading_different_bool = model.NewBoolVar(
                f"{prefix}_{i} - shading_different {cell1.format_cell()},{cell2.format_cell()}")
            model.Add(yin_yang_var1 != yin_yang_var2).OnlyEnforceIf(
                shading_different_bool)
            model.Add(yin_yang_var1 == yin_yang_var2).OnlyEnforceIf(
                shading_different_bool.Not())

            model.Add(dist >= 5).OnlyEnforceIf(shading_different_bool)

        # Along the red line, each run of cells with the same shading contains a non-repeating set of
        # consecutive digits in any order.
        segments = segment_by_transitions_csp(
            model, yin_yang_line_vars, f"{prefix}_{i}")
        # compute segment sizes
        segment_sizes_dict: dict[str, IntVar] = dict()
        for cell, segment_var in zip(cells, segments):
            segment_size_var = count_vars(model, segments, segment_var,
                                          f"{prefix}_{i} - segment_size_{cell.format_cell()}")
            segment_sizes_dict[cell.format_cell()] = segment_size_var

        for _, ((cell1, var1, seg_var1), (cell2, var2, seg_var2)) in \
                enumerate(combinations(zip(cells, cells_vars, segments), 2)):
            name = f"{prefix} - same_segment_bool, {cell1.format_cell}, {cell2.format_cell}"
            same_segment_bool = are_all_equal_csp(
                model, [seg_var1, seg_var2], name)

            # same segment => cells must have different values
            model.Add(var1 != var2).OnlyEnforceIf(same_segment_bool)

            # must be consecutive -> max distance between variables of the same segment is the segment_size - 1
            name = f"{prefix}_{i} - dist = |{cell1.format_cell()}-{cell2.format_cell()}|"
            dist = distance_csp(model, var1, var2, name)
            segment_size_var = segment_sizes_dict[cell1.format_cell()]
            model.Add(dist < segment_size_var).OnlyEnforceIf(same_segment_bool)


def set_indexing_column_is_x_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits along an orange line indicate the COLUMN in which the digit X (default X = 5) appears in that
    ROW (from left to right).

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.INDEXING_COLUMN_IS_X_LINE
    prefix = f"{key.value}"
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for i, (cells, _, value) in enumerate(genLineConstraintProperties(model, puzzle, key)):

        value = value if value is not None and len(value) else "5"
        value_var = model.get_or_set_shared_var(
            value, min_digit, max_digit, f"{prefix}_{i}: value")

        for cell in cells:
            cell_var = cell2var(grid_vars, cell)
            row_cells = grid.getRow(cell.row)
            row_vars = cells2vars(grid_vars, row_cells)
            idx_var = model.NewIntVar(
                0, len(row_cells) - 1, f"{prefix}_{i} - {cell.format_cell()}")
            model.Add(idx_var == cell_var - 1)
            model.AddElement(idx_var, row_vars, value_var)


def set_indexing_row_is_x_line_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits along a blue line indicate the ROW in which the digit X (default X = 5) appears in that COLUMN
    (from top to bottom).

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = LineConstraintsE.INDEXING_ROW_IS_X_LINE
    prefix = f"{key.value}"
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for i, (cells, _, value) in enumerate(genLineConstraintProperties(model, puzzle, key)):

        value = value if value is not None and len(value) else "5"
        value_var = model.get_or_set_shared_var(
            value, min_digit, max_digit, f"{prefix}_{i}: value")

        for cell in cells:
            cell_var = cell2var(grid_vars, cell)
            col_cells = grid.getCol(cell.col)
            col_vars = cells2vars(grid_vars, col_cells)
            idx_var = model.NewIntVar(
                0, len(col_cells) - 1, f"{prefix}_{i} - {cell.format_cell()}")
            model.Add(idx_var == cell_var - 1)
            model.AddElement(idx_var, col_vars, value_var)
