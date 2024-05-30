from collections import Counter

from puzzlesolver.Puzzle.ConstraintEnums import CornerConstraintsE, LocalConstraintsModifiersE
from puzzlesolver.Puzzle.Coords import GridCoords
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.CornerConstraints.utils import genCornerConstraintProperties
from puzzlesolver.Puzzle2model.OtherConstraints.CellEdgeLoopConstraints2csp import get_or_set_edge_loop_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownRegionsConstraints2csp import get_or_set_unknown_regions_grid
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import all_equal, count_unique_values, count_vars, modulo_count_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cells2vars, \
    tuples2vars
from puzzlesolver.Puzzle2model.puzzle_model_types import GridVars
from puzzlesolver.utils.ParsingUtils import parse_int


def set_quadruple_constraints(model: PuzzleModel, puzzle: Puzzle):
    tool_constraints = puzzle.tool_constraints
    quadruple_list = tool_constraints.get(CornerConstraintsE.QUADRUPLE)
    if not quadruple_list:
        return

    prefix = f"quadruple"

    for i, (_, cells_vars, value) in enumerate(genCornerConstraintProperties(model, puzzle, CornerConstraintsE.QUADRUPLE)):
        if value is None:
            continue
        values_str = value.replace(' ', '').split(',')

        values: list[int] = []
        for val in values_str:
            val2 = parse_int(val)
            if val2 is not None:
                values.append(val2)

        values_counter = Counter(values)

        for value, val_count in values_counter.items():
            value = parse_int(value)
            if value is None:
                continue
            count = count_vars(model, cells_vars, value,
                               f"{prefix}_{i} - value={value} count={val_count}")
            model.Add(count >= val_count)


def set_corner_sum_of_three_equals_the_other_constraints(model: PuzzleModel, puzzle: Puzzle):

    prefix = "corner_sum_of_three_equals_the_other"

    for i, (_, cells_vars, _) in enumerate(genCornerConstraintProperties(model, puzzle, CornerConstraintsE.CORNER_SUM_OF_THREE_EQUALS_THE_OTHER)):

        bools = [model.NewBoolVar(
            f"{prefix}_{i} - b_{j}") for j in range(len(cells_vars))]

        for j, cell_var in enumerate(cells_vars):
            other_vars = cells_vars[:j] + cells_vars[j+1:]
            model.Add(sum(other_vars) == cell_var).OnlyEnforceIf(bools[j])

        model.AddExactlyOne(bools)


def set_corner_sum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits surrounding a circle must sum to the number in the circle. Digits may not repeat around a circle.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    max_digit = max(puzzle.valid_digits)
    prefix = f"corner_sum"

    for i, (_, cells_vars, value) in enumerate(genCornerConstraintProperties(model, puzzle, CornerConstraintsE.CORNER_SUM)):

        sum_var = model.get_or_set_shared_var(value, 0, 4 * max_digit,
                                              f"{prefix}_{i}: sum")

        model.AddAllDifferent(cells_vars)
        model.Add(sum(cells_vars) == sum_var)


def set_corner_x_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Pairs of digits diagonally adjacent to each other across the X sum to 10.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    # prefix = f"corner_x"

    for _, (_, cells_vars, _) in enumerate(genCornerConstraintProperties(model, puzzle, CornerConstraintsE.CORNER_X)):
        g1 = [cells_vars[0], cells_vars[3]]
        g2 = [cells_vars[1], cells_vars[2]]

        model.Add(sum(g1) == 10)
        model.Add(sum(g2) == 10)


def set_corner_count_even_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers in white circles show the amount of even numbers in the surrounding four cells.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    prefix = f"corner_count_even"

    for i, (_, cells_vars, value) in enumerate(genCornerConstraintProperties(model, puzzle, CornerConstraintsE.CORNER_EVEN_COUNT)):
        count_var = model.get_or_set_shared_var(
            value, 0, 4, f"corner_count_even_{i}: count")

        count = modulo_count_csp(model, 0, 2, cells_vars, f"{prefix}_{i}")
        model.Add(count == count_var)


def set_corner_count_odd_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers in white circles show the amount of even numbers in the surrounding four cells.

    :param model:
    :param grid_vars:
    :param shared_vars:
    :param puzzle:
    :return:
    """

    prefix = f"corner_count_odd"

    for i, (_, cells_vars, value) in enumerate(genCornerConstraintProperties(model, puzzle, CornerConstraintsE.CORNER_ODD_COUNT)):
        count_var = model.get_or_set_shared_var(
            value, 0, 4, f"corner_count_even_{i}: count")

        count = modulo_count_csp(model, 0, 2, cells_vars, f"{prefix}_{i}")
        model.Add(count == count_var)


def set_border_square_diagonals_sum_not_equal_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A border square is a 2x2 square that crosses at least one box border. For all border squares except for the four marked in grey, its two diagonals sum to the same number. The diagonals of different border squares may sum to different numbers.
    """
    key = CornerConstraintsE.BORDER_SQUARE_DIAGONALS_SUM_NOT_EQUAL
    # prefix = f"{key.value}"

    for _, (_, cells_vars, _) in enumerate(genCornerConstraintProperties(model, puzzle, key)):
        diag1_vars = [cells_vars[0], cells_vars[3]]
        diag2_vars = [cells_vars[1], cells_vars[2]]

        model.Add(sum(diag1_vars) != sum(diag2_vars))

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    all_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_BORDER_SQUARE_DIAGONALS_SUM_NOT_EQUAL_GIVEN, False)
    if all_given:
        cell_quads = [cells for (cells, _, _)
                      in genCornerConstraintProperties(model, puzzle, key)]

        all_cells = grid.getAllCells()
        for cell in all_cells:
            box = [cell for line in grid.getXByYBox(
                cell, 2, 2) for cell in line]
            if len(box) != 4:
                continue
            if any(all(_cell in box for _cell in cell_quad) for cell_quad in cell_quads):
                continue
            num_regions = len(
                set(cell.region for cell in box if cell.region is not None))
            if num_regions <= 1:
                continue

            box_vars = cells2vars(grid_vars, box)
            diag1_vars = [box_vars[0], box_vars[3]]
            diag2_vars = [box_vars[1], box_vars[2]]

            model.Add(sum(diag1_vars) == sum(diag2_vars))


def set_corner_cells_belong_to_the_same_region_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The 4 cells surrounding a circle must belong to the same region.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = CornerConstraintsE.CORNER_CELLS_BELONG_TO_SAME_REGION
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # prefix = f"corner_cells_belong_to_the_same_region"
    grid = puzzle.grid
    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)

    for _, (cells, _, _) in enumerate(genCornerConstraintProperties(model, puzzle, key)):
        regions_vars = cells2vars(regions_grid, cells)
        all_equal(model, regions_vars)

    all_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_CORNER_CELLS_BELONG_TO_THE_SAME_REGION_GIVEN, False)
    if not all_given:
        return

    prefix = f"all_corner_cells_belong_to_the_same_region_given"
    cell_quads = [cells for (cells, _, _)
                  in genCornerConstraintProperties(model, puzzle, key)]
    all_cells = grid.getAllCells()
    for cell in all_cells:
        box = [cell for line in grid.getXByYBox(cell, 2, 2) for cell in line]
        if len(box) != 4:
            continue
        if any(all(_cell in box for _cell in cell_quad) for cell_quad in cell_quads):
            continue

        regions_vars = cells2vars(regions_grid, box)
        count = count_unique_values(
            model, regions_vars, f"{prefix} - {box[0].format_cell()}")
        model.AddForbiddenAssignments([count], [(1,)])


def set_corner_cells_belong_to_three_regions_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The 4 cells surrounding a black square must belong to exactly three regions.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = CornerConstraintsE.CORNER_CELLS_BELONG_TO_EXACTLY_THREE_REGIONS
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    prefix = f"corner_cells_belong_to_three_regions"
    grid = puzzle.grid
    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)

    for i, (cells, _, _) in enumerate(genCornerConstraintProperties(model, puzzle, key)):
        regions_vars = cells2vars(regions_grid, cells)
        count = count_unique_values(model, regions_vars, f"{prefix}_{i}")
        model.Add(count == 3)

    all_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_CORNER_CELLS_BELONG_TO_EXACLT_THREE_REGIONS_GIVEN, False)
    if not all_given:
        return

    prefix = f"all_corner_cells_belong_to_three_regions_given"
    cell_quads = [cells for (cells, _, _)
                  in genCornerConstraintProperties(model, puzzle, key)]
    all_cells = grid.getAllCells()
    for cell in all_cells:
        box = [cell for line in grid.getXByYBox(cell, 2, 2) for cell in line]
        if len(box) != 4:
            continue
        if any(all(_cell in box for _cell in cell_quad) for cell_quad in cell_quads):
            continue

        regions_vars = cells2vars(regions_grid, box)
        count = count_unique_values(
            model, regions_vars, f"{prefix} - {box[0].format_cell()}")
        model.AddForbiddenAssignments([count], [(3,)])


def set_edge_loop_straight_on_corner_and_turns_at_least_once_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The loop passes through a white dot in a straight line, then makes a 90-degree turn on one or both of the nearest
    cell corners along the loop.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = CornerConstraintsE.EDGE_LOOP_PASSES_STRAIGHT_ON_CORNER_AND_TURNS_AFTER_AT_LEAST_ONCE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid_vars_dict = model.grid_vars_dict
    get_or_set_edge_loop_constraint(model, puzzle)
    loop_nodes_dict = grid_vars_dict["loop_nodes_dict"]
    horizontal_loop_edges = grid_vars_dict["horizontal_loop_edges"]
    vertical_loop_edges = grid_vars_dict["vertical_loop_edges"]

    for i, (cells, _, _) in enumerate(genCornerConstraintProperties(model, puzzle, key)):
        cell1_coord = GridCoords(cells[0].row, cells[0].col)
        aux = cell1_coord.toCornerCoords(2)
        r, c = int(aux.r), int(aux.c)
        loop_node_var = loop_nodes_dict[(r, c)]
        model.Add(loop_node_var == 1)

        vert_or_horiz_bool = model.NewBoolVar(
            f"{prefix}_{i} - vert_or_horiz_bool")

        # Vertical Edges
        coords = [(r - 1, c), (r, c)]
        vert_connected_edges = tuples2vars(vertical_loop_edges, coords)

        coords = [(r-1, c-1), (r-1, c), (r+1, c-1), (r+1, c)]
        connected_to_vert_edges = tuples2vars(horizontal_loop_edges, coords)

        model.AddBoolAnd(vert_connected_edges).OnlyEnforceIf(
            vert_or_horiz_bool.Not())

        model.Add(sum(connected_to_vert_edges) >= 1).OnlyEnforceIf(
            vert_or_horiz_bool.Not())

        # Horizontal Edges
        coords = [(r, c - 1), (r, c)]
        horiz_connected_edges = tuples2vars(horizontal_loop_edges, coords)

        coords = [(r-1, c-1), (r, c-1), (r-1, c+1), (r, c+1)]
        connected_to_horiz_edges = tuples2vars(vertical_loop_edges, coords)

        model.AddBoolAnd(horiz_connected_edges).OnlyEnforceIf(
            vert_or_horiz_bool)
        model.Add(sum(connected_to_horiz_edges) >=
                  1).OnlyEnforceIf(vert_or_horiz_bool)


def set_edge_loop_turns_on_corner_and_does_not_turn_after_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The edge loop makes a 90-degree turn on a black dot, and does not turn at the next opportunity in either direction.

    :param model:
    :param grid_vars_dict:
    :param shared_vars:
    :param puzzle:
    :return:
    """
    key = CornerConstraintsE.EDGE_LOOP_TURNS_ON_CORNER_AND_DOES_NOT_TURN_AFTER
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid_vars_dict = model.grid_vars_dict
    get_or_set_edge_loop_constraint(model, puzzle)
    loop_nodes_dict = grid_vars_dict["loop_nodes_dict"]
    horizontal_loop_edges = grid_vars_dict["horizontal_loop_edges"]
    vertical_loop_edges = grid_vars_dict["vertical_loop_edges"]

    for i, (cells, _, _) in enumerate(genCornerConstraintProperties(model, puzzle, key)):
        cell1_coord = GridCoords(cells[0].row, cells[0].col)
        aux = cell1_coord.toCornerCoords(2)
        r, c = int(aux.r), int(aux.c)
        loop_node_var = loop_nodes_dict[(r, c)]
        model.Add(loop_node_var == 1)

        vert_above_or_below_bool = model.NewBoolVar(
            f"{prefix}_{i} - vert_above_or_below_bool")

        coords = [(r-1, c), (r-2, c)]
        two_vert_connected_edges_above = tuples2vars(
            vertical_loop_edges, coords)
        coords = [(r, c), (r+1, c)]
        two_vert_connected_edges_below = tuples2vars(
            vertical_loop_edges, coords)

        model.AddBoolAnd(two_vert_connected_edges_above).OnlyEnforceIf(
            vert_above_or_below_bool.Not())
        model.AddBoolAnd(two_vert_connected_edges_below).OnlyEnforceIf(
            vert_above_or_below_bool)

        horiz_left_or_right_bool = model.NewBoolVar(
            f"{prefix}_{i} - horiz_left_or_right_bool")

        coords = [(r, c-1), (r, c-2)]
        two_horiz_connected_edges_left = tuples2vars(
            horizontal_loop_edges, coords)
        coords = [(r, c), (r, c+1)]
        two_horiz_connected_edges_right = tuples2vars(
            horizontal_loop_edges, coords)

        model.AddBoolAnd(two_horiz_connected_edges_left).OnlyEnforceIf(
            horiz_left_or_right_bool.Not())
        model.AddBoolAnd(two_horiz_connected_edges_right).OnlyEnforceIf(
            horiz_left_or_right_bool)


def set_corner_constraints(model: PuzzleModel,
                           puzzle: Puzzle):
    set_quadruple_constraints(model, puzzle)
    set_corner_x_constraints(model, puzzle)
    set_corner_sum_of_three_equals_the_other_constraints(model, puzzle)
    set_corner_sum_constraints(model, puzzle)
    set_corner_count_even_constraints(model, puzzle)
    set_corner_count_odd_constraints(model, puzzle)
    set_border_square_diagonals_sum_not_equal_constraints(model, puzzle)
    set_corner_cells_belong_to_the_same_region_constraints(model, puzzle)
    set_corner_cells_belong_to_three_regions_constraints(model, puzzle)
    set_edge_loop_straight_on_corner_and_turns_at_least_once_constraints(
        model, puzzle)
    set_edge_loop_turns_on_corner_and_does_not_turn_after_constraints(
        model, puzzle)
