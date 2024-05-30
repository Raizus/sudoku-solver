from ortools.sat.python.cp_model import IntVar
from puzzlesolver.Puzzle.ConstraintEnums import EdgeConstraintsE, LocalConstraintsModifiersE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.EdgeConstraints.utils import genEdgeConstraintProperties
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import distance_csp, factors_csp, is_member_of, is_ratio_1_r_csp, member_of
from puzzlesolver.Puzzle2model.puzzle_csp_utils import SQUARE_NUMBERS_LIST2, GridVars, cell2var
from puzzlesolver.utils.ParsingUtils import parse_int


def set_ratio_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Cells separated by a black dot have a 1:2 ratio or a 1:X ratio if the circle has value X.

    :param shared_vars:
    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    prefix = f"ratio"
    max_digit = max(puzzle.valid_digits)
    for i, (_, cells_vars, value) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.RATIO)):
        [cell1_var, cell2_var] = cells_vars

        value_id = value if len(value) else 2

        ratio_var = model.get_or_set_shared_var(
            value_id, 1, max_digit, f"{prefix}_{i}")

        is_ratio = is_ratio_1_r_csp(
            model, cell1_var, cell2_var, ratio_var, f"{prefix}_{i}")
        model.Add(is_ratio == 1)

    all_ratios_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_RATIOS_GIVEN, False)
    # assuming all ratios are 1:2
    if all_ratios_given:
        cell_pairs = [cells for cells, _, _ in genEdgeConstraintProperties(
            model, puzzle, EdgeConstraintsE.RATIO)]

        for cell1, cell2 in puzzle.grid.genAllAdjacentPairs():
            ratios_with_both_cells = [
                cell_pair for cell_pair in cell_pairs if cell1 in cell_pair and cell2 in cell_pair]
            if len(ratios_with_both_cells):
                continue

            # add exception for 1-2 differences
            cell1_var = cell2var(grid_vars, cell1)
            cell2_var = cell2var(grid_vars, cell2)

            model.Add(2 * cell1_var != cell2_var)
            model.Add(2 * cell2_var != cell1_var)


def set_difference_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers separated by a white circle are consecutive.
    Cells separated by a white circle with a number X must have a difference of X.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    prefix = f"difference"
    used_values: set[int | IntVar] = set()

    for i, (_, cells_vars, value) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.DIFFERENCE)):
        cell1_var, cell2_var = cells_vars

        lb = min(min(cell1_var.Proto().domain), min(cell2_var.Proto().domain))
        ub = max(max(cell1_var.Proto().domain), max(cell2_var.Proto().domain))

        value_id = value if len(value) else 1
        diff_var = model.get_or_set_shared_var(value_id, 0, ub - lb,
                                               f"difference_{i}")
        used_values.add(diff_var)

        dist_var = distance_csp(model, cell1_var, cell2_var, f"{prefix}_{i}")
        model.Add(dist_var == diff_var)

    all_differences_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_DIFFERENCES_GIVEN, False)
    if all_differences_given:
        if len(used_values) == 0:
            used_values.add(1)

        difference_pairs = [cells for cells, _, _ in genEdgeConstraintProperties(
            model, puzzle, EdgeConstraintsE.DIFFERENCE)]

        for cell1, cell2 in puzzle.grid.genAllAdjacentPairs():
            differences_with_both_cells = [
                cell_pair for cell_pair in difference_pairs if cell1 in cell_pair and cell2 in cell_pair]
            if len(differences_with_both_cells):
                continue

            cell1_var = cell2var(grid_vars, cell1)
            cell2_var = cell2var(grid_vars, cell2)
            for value in used_values:
                model.Add(cell1_var - cell2_var != value)
                model.Add(cell2_var - cell1_var != value)


def set_edge_sum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Cells separated by a transparent blue dot marked with an X have a fixed sum of X.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    prefix = f"edge_sum"

    for i, (_, cells_vars, value) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.EDGE_SUM)):
        cell1_var, cell2_var = cells_vars

        lb = min(min(cell1_var.Proto().domain), min(cell2_var.Proto().domain))
        ub = max(max(cell1_var.Proto().domain), max(cell2_var.Proto().domain))

        value_id = value
        sum_var = model.get_or_set_shared_var(value_id, 2 * lb, 2 * ub,
                                              f"{prefix}_{i}: sum")

        model.Add(cell1_var + cell2_var == sum_var)


def set_edge_product_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Cells separated by a transparent red dot marked with an X have a fixed product of X.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    prefix = f"edge_product"

    for i, (_, cells_vars, value) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.EDGE_PRODUCT)):
        cell1_var, cell2_var = cells_vars

        lb = min(min(cell1_var.Proto().domain), min(cell2_var.Proto().domain))
        ub = max(max(cell1_var.Proto().domain), max(cell2_var.Proto().domain))

        product_var = model.get_or_set_shared_var(value, lb ** 2, ub ** 2,
                                                  f"{prefix}_{i}: product")

        model.AddMultiplicationEquality(product_var, [cell1_var, cell2_var])


def set_edge_modulo_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Cells separated by a circle marked with an X shows the remainder when the bigger number is divided by
    the smaller number.

    :param shared_vars:
    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    # shared_vars = model.shared_vars_dict
    prefix = f"edge_modulo"
    max_digit = max(puzzle.valid_digits)

    for i, (_, cells_vars, value) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.EDGE_MODULO)):
        cell1_var, cell2_var = cells_vars

        value2 = parse_int(value)
        # modulo_var = get_or_set_shared_var(model, value_id, shared_vars, 0, max_digit,
        #                                    f"{prefix}_{i}: modulo")

        if value2 is not None:

            modulo_val_0 = model.NewIntVar(
                0, max_digit, f"{prefix}_{i} - value_0")
            modulo_val_1 = model.NewIntVar(
                0, max_digit, f"{prefix}_{i} - value_1")
            ordering_var = model.NewBoolVar(f"{prefix}_{i} - ordering_bool")
            # ordering_var == 0 -> cell1_var > cell2_var -> modulo_val_0 = cell1_var % cell2_var
            # ordering_var == 1 -> cell2_var > cell1_var -> modulo_val_0 = cell2_var % cell1_var
            model.Add(cell1_var < cell2_var).OnlyEnforceIf(ordering_var)
            model.Add(cell1_var >= cell2_var).OnlyEnforceIf(ordering_var.Not())
            model.AddModuloEquality(modulo_val_0, cell1_var, cell2_var)
            model.AddModuloEquality(modulo_val_1, cell2_var, cell1_var)
            model.Add(modulo_val_0 == value2).OnlyEnforceIf(ordering_var.Not())
            model.Add(modulo_val_1 == value2).OnlyEnforceIf(ordering_var)


def set_factor_dot_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    For any two cells separated by a transparent yellow dot, one must be divisible by the other.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    prefix = f"edge_factor"
    for i, (_, cells_vars, _) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.EDGE_FACTOR)):
        cell1_var, cell2_var = cells_vars

        factors_csp(model, cell1_var, cell2_var, f"{prefix}_{i}")


def set_xv_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Two cells joined by X must sum to 10. Two cells joined by a V must sum to 5.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    # shared_vars = model.shared_vars_dict

    for _, (_, cells_vars, value_str) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.XV)):
        cell1_var, cell2_var = cells_vars

        if value_str == 'X' or value_str == 'x':
            value = 10
        elif value_str == 'V' or value_str == 'v':
            value = 5
        else:
            raise ValueError("XV constraint value must be X or V")

        model.Add(cell1_var + cell2_var == value)

    all_xv_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_XV_GIVEN, False)
    all_x_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_X_GIVEN, False)
    all_v_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_V_GIVEN, False)
    if all_x_given or all_v_given or all_xv_given:
        values: set[str] = set()
        if all_x_given or all_xv_given:
            values.update(['x', 'X'])
        if all_v_given or all_xv_given:
            values.update(['v', 'V'])

        cell_pairs = [cells for cells, _, value in genEdgeConstraintProperties(
            model, puzzle, EdgeConstraintsE.XV) if value in values]

        for cell1, cell2 in puzzle.grid.genAllAdjacentPairs():
            xv_with_both_cells = [
                cell_pair for cell_pair in cell_pairs if cell1 in cell_pair and cell2 in cell_pair]
            if len(xv_with_both_cells):
                continue

            cell1_var = cell2var(grid_vars, cell1)
            cell2_var = cell2var(grid_vars, cell2)
            if all_x_given or all_xv_given:
                model.Add(cell1_var + cell2_var != 10)
            if all_v_given or all_xv_given:
                model.Add(cell1_var + cell2_var != 5)


def set_x_or_v_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Two cells joined by an XV must sum to 5 or 10.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"x_or_v"

    for i, (_, cells_vars, value) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.X_OR_V)):
        cell1_var, cell2_var = cells_vars

        value = model.NewIntVar(5, 10, f'{prefix}_{i} - value')
        model.Add(cell1_var + cell2_var == value)
        member_of(model, [5, 10], value, f"{prefix}_{i} - value")


def set_edge_inequality_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    The inequality sign points to the lower of the two digits.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    for _, (_, cells_vars, value) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.EDGE_INEQUALITY)):
        cell1_var, cell2_var = cells_vars

        if value == '<':
            model.Add(cell1_var < cell2_var)
        elif value == '>':
            model.Add(cell1_var > cell2_var)
        else:
            raise ValueError(
                "Edge inequality constraint value must be '<' or '>'")


def set_edge_multiples_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Adjacent cells separated by a number should be read as a two-digit number (reading left-to-right or downwards);
    the two-digit number must be a multiple of the clue
    (e.g. around a 7 clue, the two digits could be 14, 21, 28, 35, …)

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    # shared_vars = model.shared_vars_dict
    prefix = f"two_digit_multiples"
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    min_value = min_digit * 10 + min_digit
    max_value = max_digit * 10 + max_digit

    for i, (_, cells_vars, value) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.TWO_DIGIT_MULTIPLES)):
        cell1_var, cell2_var = cells_vars

        value2 = parse_int(value)

        if value2 is not None:
            res = model.NewIntVar(min_value, max_value, f"{prefix}_{i} - res")
            model.Add(10 * cell1_var + cell2_var == res)
            model.AddModuloEquality(0, res, value2)


def set_xy_differences_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    If two cells are separated by a diamond, the digits must exhibit a difference equal to the leftmost or topmost
    digit sharing a row or column with them. For example, the difference between R9C3,4 = R9C1, and the difference
    between R2,3C1 = R1C1. Not all possible diamonds are necessarily given.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    prefix = f"xy_differences"
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)
    grid = puzzle.grid

    ub = max_digit-min_digit

    for i, (cells, cells_vars, _) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.XY_DIFFERENCES)):
        cell1_var, cell2_var = cells_vars
        cell1, cell2 = cells

        if cell1.col != cell2.col and cell1.row != cell2.row:
            continue

        target_cell = grid.getCell(
            0, cell1.col) if cell1.col == cell2.col else grid.getCell(cell1.row, 0)
        if target_cell is None:
            continue
        target_var = cell2var(grid_vars, target_cell)

        diff = model.NewIntVar(
            0, ub, f"{prefix}_{i} - |{cell1.format_cell()}_{cell2.format_cell()}|")
        model.AddAbsEquality(diff, cell1_var - cell2_var)
        model.Add(diff == target_var)

    all_xy_differences_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_XY_DIFFERENCES_GIVEN, False)
    if all_xy_differences_given:
        cell_pairs = [cells for cells, _, _ in genEdgeConstraintProperties(
            model, puzzle, EdgeConstraintsE.XY_DIFFERENCES)]

        for cell1, cell2 in puzzle.grid.genAllAdjacentPairs():
            xy_diff_with_both_cells = [
                cell_pair for cell_pair in cell_pairs if cell1 in cell_pair and cell2 in cell_pair]
            if len(xy_diff_with_both_cells):
                continue

            cell1_var = cell2var(grid_vars, cell1)
            cell2_var = cell2var(grid_vars, cell2)

            target_cell = grid.getCell(
                0, cell1.col) if cell1.col == cell2.col else grid.getCell(cell1.row, 0)
            if target_cell is None:
                continue

            target_var = cell2var(grid_vars, target_cell)

            diff = model.NewIntVar(
                0, ub, f"{prefix} - |{cell1.format_cell()}-{cell2.format_cell()}|")
            model.AddAbsEquality(diff, cell1_var - cell2_var)
            model.Add(diff != target_var)


def set_edge_square_number_constraints(model: PuzzleModel,
                                       puzzle: Puzzle):
    """
    Cells in green cages are a square number read left to right or top to bottom.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """

    prefix = f"square_number_border"

    min_value = 0
    max_value = 100

    numbers_vars: list[IntVar] = []
    for i, (cells, cells_vars, _) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.EDGE_SQUARE_NUMBER)):
        number_var = model.NewIntVar(
            min_value, max_value, f"{prefix} - {cells[0].format_cell()}_{cells[1].format_cell()}")

        model.Add(cells_vars[0] * 10 + cells_vars[1] == number_var)
        member_of(model, SQUARE_NUMBERS_LIST2, number_var,
                  f"{prefix}_{i} - {cells[0].format_cell()}_{cells[1].format_cell()}")

        numbers_vars.append(number_var)

    # square_numbers_all_different = puzzle.bool_constraints.get(BoolConstraints.SQUARE_NUMBER_BORDER_ALL_DIFFERENT,
    #                                                            False)
    # if square_numbers_all_different:
    #     model.AddAllDifferent(numbers_vars)


def set_edge_exactly_one_friendly_cell_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Two cells joined by X must sum to 10. Two cells joined by a V must sum to 5.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """

    prefix = f"edge_exactly_one_friendly_cell"

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    # shared_vars = model.shared_vars_dict

    for i, (cells, _, _) in enumerate(genEdgeConstraintProperties(model, puzzle, EdgeConstraintsE.EDGE_EXACTLY_ONE_FRIENDLY_CELL)):
        friendly_bools: list[IntVar] = []
        for cell in cells:
            cell_var = cell2var(grid_vars, cell)
            row = cell.row + 1
            col = cell.col + 1
            region = cell.region + 1 if cell.region is not None else None

            values = [row, col]
            if region is not None:
                values.append(region)

            name = f"{prefix}_{i} - {cell.format_cell()} - is_friendly"
            is_friendly = is_member_of(model, values, cell_var, name)
            friendly_bools.append(is_friendly)

        model.AddExactlyOne(friendly_bools)
