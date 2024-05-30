
from puzzlesolver.Puzzle2model.OtherConstraints.BattlestarConstraints2csp import get_or_set_battlestar_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.LShapedRegionsConstraints2csp import get_or_set_l_shaped_regions_grid
from puzzlesolver.Puzzle2model.OtherConstraints.NurimisakiConstraints2csp import get_or_set_nurimisaki_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.TwoContiguousRegionsConstraints2csp import get_or_set_two_contiguous_regions_constraint
from puzzlesolver.utils.ParsingUtils import parse_int

from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars

from puzzlesolver.Puzzle2model.LineConstraints.utils import genLineConstraintProperties
from puzzlesolver.Puzzle2model.OtherConstraints.CenterCellsLoopConstraints2csp import get_or_set_cell_center_loop_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownRegionsConstraints2csp import get_or_set_unknown_regions_grid
from puzzlesolver.Puzzle2model.custom_constraints import are_all_equal_csp, are_all_true_csp, masked_sum_csp, count_different_vars, count_transitions_csp, count_uninterrupted_left_right_csp, count_vars
from puzzlesolver.Puzzle2model.SingleCellConstraints.utils import genSingleCellArrowConstraintProperties, genSingleCellConstraintProperties, genSingleCellMultiArrowConstraintProperties

from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel

from puzzlesolver.Puzzle.Cell import sortCells
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle.Directions import getCardinalDirections
from puzzlesolver.Puzzle.ConstraintEnums import LineConstraintsE, LocalConstraintsModifiersE, SingleCellArrowConstraintsE, SingleCellConstraintsE, SingleCellMultiArrowConstraintsE

from ortools.sat.python.cp_model import IntVar


def set_count_region_sum_line_cells_in_region_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits in a circle indicate the number of cells that are part of a line in that cell's region.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key1 = SingleCellConstraintsE.COUNT_REGION_SUM_LINE_CELLS_IN_REGION
    prefix = f"{key1.value}"

    constraint_list = puzzle.tool_constraints.get(key1)
    if not len(constraint_list):
        return

    key2 = LineConstraintsE.REGION_SUM_LINE
    constraint_list = puzzle.tool_constraints.get(key2)
    if not len(constraint_list):
        return

    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)
    region_sum_line_cells = [cell for (cells, _, _) in genLineConstraintProperties(
        model, puzzle, key2) for cell in cells]
    region_sum_line_cells = sortCells(list(set(region_sum_line_cells)))

    region_sum_line_cells_region_vars = cells2vars(
        regions_grid, region_sum_line_cells)

    cell_region_vars: list[IntVar] = []

    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key1)):
        region_var = cell2var(regions_grid, cell)
        count = count_vars(model, region_sum_line_cells_region_vars,
                           region_var, f"{prefix} {i} - {cell.format_cell()}")
        model.Add(count == cell_var)
        cell_region_vars.append(region_var)

    model.AddAllDifferent(cell_region_vars)


def set_l_shaped_region_bend_count_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A circle in a cell means that cell is the bend in a region, and also the number in that cell is how many cells
    are in that region (this rule does not apply to regions without a circle).

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.L_SHAPED_REGION_BEND_COUNT
    prefix = f"{key.value}"
    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    grid = puzzle.grid
    regions_grid = get_or_set_l_shaped_regions_grid(model, puzzle)
    l_shaped_regions_bend_bools_grid = model.grid_vars_dict["l_shaped_regions_bend_bools_grid"]
    all_cells = grid.getAllCells()
    all_region_vars = cells2vars(regions_grid, all_cells)

    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        bend_bool_var = cell2var(l_shaped_regions_bend_bools_grid, cell)
        model.Add(bend_bool_var == 1)
        cell1_region_var = cell2var(regions_grid, cell)

        cell_region_size = count_vars(model, all_region_vars, cell1_region_var,
                                      f"{prefix}_{i} - {cell.format_cell()} region_size")
        model.Add(cell_region_size == cell_var)

        # if the cell is a region bend, then, there is 1 cell vertically adjacent to the bend and one cell horizontally adjacent to the bend
        vert_adj_cells = grid.getVerticallyAdjacentCells(cell)
        if len(vert_adj_cells) == 1:
            cell2 = vert_adj_cells[0]
            cell2_region_var = cell2var(regions_grid, cell2)
            model.Add(cell2_region_var == cell1_region_var)
            cell2_bend_bool_var = cell2var(
                l_shaped_regions_bend_bools_grid, cell2)
            model.Add(cell2_bend_bool_var == 0)

        horiz_adj_cells = grid.getHorizontallyAdjacentCells(cell)
        if len(horiz_adj_cells) == 1:
            cell2 = horiz_adj_cells[0]
            cell2_region_var = cell2var(regions_grid, cell2)
            model.Add(cell2_region_var == cell1_region_var)
            cell2_bend_bool_var = cell2var(
                l_shaped_regions_bend_bools_grid, cell2)
            model.Add(cell2_bend_bool_var == 0)


def set_l_shaped_region_arrow_points_to_bend_constraints(model: PuzzleModel,
                                                         puzzle: Puzzle):
    """
    An arrow in a cell means that cell is an end of a region, the arrow points to the bend, and also the value in the
    cell counts the number of cells in that leg of the region, including the bend cell (this rule does not apply to
    end-cells without arrows).

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellArrowConstraintsE.L_SHAPED_REGION_ARROW_POINTS_TO_BEND
    prefix = f"{key.value}"

    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    prefix = "l_shaped_region_arrow_points_to_bend"
    grid = puzzle.grid
    regions_grid = get_or_set_l_shaped_regions_grid(model, puzzle)
    l_shaped_regions_bend_bools_grid = model.grid_vars_dict["l_shaped_regions_bend_bools_grid"]
    # all_region_vars = cells2vars(regions_grid, all_cells)

    directions = getCardinalDirections()

    for i, (cell, cell_var, direction, _) in enumerate(genSingleCellArrowConstraintProperties(model, puzzle, key)):
        region_cell_var = cell2var(regions_grid, cell)

        is_bend_bool_var = cell2var(l_shaped_regions_bend_bools_grid, cell)
        model.Add(is_bend_bool_var == 0)

        other_directions = [_dir for _dir in directions if _dir != direction]
        cells = grid.getCellsInDirection(cell, direction)
        region_cells_vars = cells2vars(regions_grid, cells)

        model.Add(cell_var <= len(cells) + 1)
        model.Add(cell_var >= 2)

        # adjacent cells in directions different from where the arrow is pointing belong to a different region
        # (i.e. the cell is at an end of a region)
        for _dir in other_directions:
            adj_cell = grid.getAdjacentCellInDirection(cell, _dir)
            if not adj_cell:
                continue
            adj_cell_region_var = cell2var(regions_grid, adj_cell)
            model.Add(region_cell_var != adj_cell_region_var)

        for j, (cell2, region_cell_var_2) in enumerate(zip(cells, region_cells_vars), 2):
            same_region_bool_var = model.NewBoolVar(
                f"{prefix}_{i} - {cell.format_cell()}, dist_{j}, same_region_bool_var")
            model.Add(j <= cell_var).OnlyEnforceIf(same_region_bool_var)
            model.Add(j > cell_var).OnlyEnforceIf(same_region_bool_var.Not())
            model.Add(region_cell_var_2 == region_cell_var).OnlyEnforceIf(
                same_region_bool_var)
            model.Add(region_cell_var_2 != region_cell_var).OnlyEnforceIf(
                same_region_bool_var.Not())

            bool_var_2 = model.NewBoolVar(
                f"{prefix}_{i} - {cell.format_cell()}, dist_{j}, bool_var_2")
            model.Add(j < cell_var).OnlyEnforceIf(bool_var_2)
            model.Add(j >= cell_var).OnlyEnforceIf(bool_var_2.Not())

            bool_var_3 = model.NewBoolVar(
                f"{prefix}_{i} - {cell.format_cell()}, dist_{j}, bool_var_3")
            model.Add(j == cell_var).OnlyEnforceIf(bool_var_3)
            model.Add(j != cell_var).OnlyEnforceIf(bool_var_3.Not())

            is_bend_bool_var = cell2var(
                l_shaped_regions_bend_bools_grid, cell2)
            model.Add(is_bend_bool_var == 1).OnlyEnforceIf(bool_var_3)
            model.Add(is_bend_bool_var == 0).OnlyEnforceIf(bool_var_2)


def set_l_shaped_region_sum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A small clue in the top left corner of a cell gives the sum of the cells in that cell's region. Corner clues
    do not need to be in the top left cell of a region.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.L_SHAPED_REGION_SUM
    prefix = f"{key.value}"

    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid
    regions_grid = get_or_set_l_shaped_regions_grid(model, puzzle)

    all_cells = grid.getAllCells()
    all_cells_vars = cells2vars(grid_vars, all_cells)

    prefix = "l_shaped_region_sum"
    for i, (cell, _, value) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        sum_val = parse_int(value)
        if sum_val is None:
            continue

        # create a grid of bools indicating weather a cell belongs to the same region as the constraint's cell
        region_cell_var = cell2var(regions_grid, cell)
        region_bools_grid = \
            bool_vars_grid_dict_from_puzzle_grid(
                model, grid, f"{prefix}_{i} - region_bools_grid_{cell.format_cell()}")

        for cell2 in all_cells:
            region_cell2_var = cell2var(regions_grid, cell2)
            region_cell2_bool = cell2var(region_bools_grid, cell2)
            model.Add(region_cell_var == region_cell2_var).OnlyEnforceIf(
                region_cell2_bool)
            model.Add(region_cell_var != region_cell2_var).OnlyEnforceIf(
                region_cell2_bool.Not())

        # sum of cells in the region
        all_region_bools_vars = cells2vars(region_bools_grid, all_cells)
        masked_sum = masked_sum_csp(model, all_cells_vars, all_region_bools_vars,
                                    f"{prefix} - {cell.format_cell()} sum")
        model.Add(masked_sum == sum_val)


def set_two_contiguous_regions_row_col_opposite_set_count_constraints(model: PuzzleModel,
                                                                      puzzle: Puzzle):
    """
    Digits in a circled cell indicate the number of cells in the corresponding row and column combined that
    are in the other set.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.TWO_CONTIGUOUS_REGIONS_ROW_COLUMN_OPPOSITE_SET_COUNT
    prefix = f"{key.value}"

    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    two_contiguous_regions_grid = get_or_set_two_contiguous_regions_constraint(
        model, puzzle)

    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):

        row_cells = grid.getRow(cell.row)
        col_cells = grid.getCol(cell.col)
        cells = list(set(row_cells + col_cells))
        cells_regions_vars = cells2vars(two_contiguous_regions_grid, cells)
        cell_region_var = cell2var(two_contiguous_regions_grid, cell)

        n = len(cells)
        count_1 = model.NewIntVar(
            0, n, f"{prefix}_{i} - {cell.format_cell()} - count_1")
        count_0 = count_vars(model, cells_regions_vars, 0,
                             f"{prefix}_{i} - {cell.format_cell()} - count_0")
        model.Add(count_1 + count_0 == n)
        # if cell_region_var == 1 => count 0's
        model.Add(cell_var == count_0).OnlyEnforceIf(cell_region_var)
        # if cell_region_var == 0 => count 1's
        model.Add(cell_var == count_1).OnlyEnforceIf(cell_region_var.Not())


def set_nurimisaki_unshaded_endpoints_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Circles mark an instance of a cell which is unshaded and orthogonally adjacent to exactly one other unshaded cell
    (i.e. the circles mark 'endpoints' of the unshaded area). The digit in a circle indicates how many cells are in the
    straight line of unshaded cells coming out of the cell with the circle, including itself.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.NURIMISAKI_UNSHADED_ENDPOINTS
    # prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    nurimisaki_grid = get_or_set_nurimisaki_constraint(model, puzzle)
    grid = puzzle.grid

    for _, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        nurimisaki_adjacent_cells = cells2vars(nurimisaki_grid, adjacent_cells)
        nurimisaki_cell_var = cell2var(nurimisaki_grid, cell)

        # cell is unshaded (1)
        model.Add(nurimisaki_cell_var == 1)
        # only one adjacent cell is shaded
        model.Add(sum(nurimisaki_adjacent_cells) == 1)

        # The digit in a circle indicates how many cells are in the straight line of unshaded cells coming out of
        # the cell with the circle, including itself.
        row_cells = grid.getRow(cell.row)
        col_cells = grid.getCol(cell.col)

        nurimisaki_row = cells2vars(nurimisaki_grid, row_cells)
        nurimisaki_col = cells2vars(nurimisaki_grid, col_cells)
        idx_row = row_cells.index(cell)
        idx_col = col_cells.index(cell)

        count_uninterrupted_row = count_uninterrupted_left_right_csp(
            model, nurimisaki_row, idx_row, 1)
        count_uninterrupted_col = count_uninterrupted_left_right_csp(
            model, nurimisaki_col, idx_col, 1)

        model.Add(count_uninterrupted_row +
                  count_uninterrupted_col + 1 == cell_var)

    all_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_NURIMISAKI_UNSHADED_ENDPOINTS_GIVEN, False)

    if not all_given:
        return

    all_cells = grid.getAllCells()
    endpoint_cells = [cell for cell, _,
                      _ in genSingleCellConstraintProperties(model, puzzle, key)]

    for cell in all_cells:
        if cell in endpoint_cells:
            continue

        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        nurimisaki_adjacent_cells = cells2vars(nurimisaki_grid, adjacent_cells)
        nurimisaki_cell_var = cell2var(nurimisaki_grid, cell)

        model.Add(sum(nurimisaki_adjacent_cells) !=
                  1).OnlyEnforceIf(nurimisaki_cell_var)


def set_galaxy_sum_except_star_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Each galaxy with a small number clue in it sums to the number indicated. Digits can't repeat within a galaxy and
    “star” cells do not contribute to the totals shown.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.GALAXY_SUM_EXCEPT_STAR
    # prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    all_cells = grid.getAllCells()
    stars_bools_grid = get_or_set_battlestar_constraint(model, puzzle)
    galaxies_grid = model.grid_vars_dict["galaxies_grid"]
    prefix = "galaxy_sum_except_star"
    all_cells_vars = cells2vars(grid_vars, all_cells)

    for _, (cell, _, value) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        # value_var = model.get_or_set_shared_var(
        #     value, lb, n * ub, f"{prefix}_{i} - sum")
        value = parse_int(value)
        if value is None:
            continue

        cell_galaxy_var = cell2var(galaxies_grid, cell)
        bools = bool_vars_grid_dict_from_puzzle_grid(
            model, grid, f"{prefix} - {cell.format_cell()}")
        for cell2 in all_cells:
            bool_var = cell2var(bools, cell2)
            cell2_galaxy_var = cell2var(galaxies_grid, cell2)
            cell2_star_var = cell2var(stars_bools_grid, cell2)

            name = f"{prefix} - {cell.format_cell()}, {cell2.format_cell()}"
            same_galaxy_bool_var = are_all_equal_csp(
                model, [cell_galaxy_var, cell2_galaxy_var], name)

            # cell counts towards sum if same galaxy and not star
            model.AddBoolAnd(same_galaxy_bool_var,
                             cell2_star_var.Not()).OnlyEnforceIf(bool_var)
            model.AddBoolOr(same_galaxy_bool_var.Not(),
                            cell2_star_var).OnlyEnforceIf(bool_var.Not())

        all_bools_vars = cells2vars(bools, all_cells)
        masked_sum = masked_sum_csp(
            model, all_cells_vars, all_bools_vars, f"{prefix} - {cell.format_cell()}")
        model.Add(masked_sum == value)


def set_seen_region_borders_count_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A digit in a circle indicates the number of borders between regions it sees in its row and column. Note that the
    edge of the grid does not count toward this total.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.SEEN_REGION_BORDERS_COUNT
    prefix = f"{key.value}"

    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)
    grid = puzzle.grid

    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        row_cells = grid.getRow(cell.row)
        col_cells = grid.getCol(cell.col)

        region_row_vars = cells2vars(regions_grid, row_cells)
        region_col_vars = cells2vars(regions_grid, col_cells)

        count_row = count_transitions_csp(
            model, region_row_vars, f"{prefix}_{i} - count_row")
        count_col = count_transitions_csp(
            model, region_col_vars, f"{prefix}_{i} - count_col")
        model.Add(count_row + count_col == cell_var)


def set_neighbour_cells_same_region_count_except_itself_constraints(model: PuzzleModel,
                                                                    puzzle: Puzzle):
    """
    A digit in a circle shows the amount of cells touching it, orthogonally and diagonally, not including itself,
    which are part of the same region.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.UNKNOWN_REGIONS_NEIGHBOUR_CELLS_SAME_REGION_COUNT_EXCEPT_ITSELF
    prefix = f"{key.value}"

    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    prefix = "neighbour_cells_same_region_count_except_itself"
    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        cell_region_var = cell2var(regions_grid, cell)
        neighbour_cells = grid.getNeighbourCells(cell)
        neighbour_cells_region_vars = cells2vars(regions_grid, neighbour_cells)

        same_region_count = count_vars(model, neighbour_cells_region_vars, cell_region_var,
                                       f"{prefix}_{i} - {cell.format_cell()}")
        model.Add(same_region_count == cell_var)

    all_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_UNKNOWN_REGIONS_NEIGHBOUR_CELLS_SAME_REGION_COUNT_EXCEPT_ITSELF_GIVEN)
    if not all_given:
        return

    cells = [cell for (cell, _, _) in genSingleCellConstraintProperties(
        model, puzzle, key)]
    prefix = f"unknown_regions_neighbour_cells_same_region_count_except_itself"
    for cell in puzzle.grid.getAllCells():
        if cell in cells:
            continue

        cell_var = cell2var(grid_vars, cell)
        cell_region_var = cell2var(regions_grid, cell)
        neighbour_cells = grid.getNeighbourCells(cell)
        neighbour_cells_region_vars = cells2vars(regions_grid, neighbour_cells)

        same_region_count = count_vars(model, neighbour_cells_region_vars, cell_region_var,
                                       f"{prefix} - {cell.format_cell()}")
        model.Add(same_region_count != cell_var)


def set_next_numbered_region_distance_arrows_constraints(model: PuzzleModel,
                                                         puzzle: Puzzle):
    """
    If a cell with the digit X in a region with the number N contains an arrow, then the cell X steps away in the
    indicated direction belongs to the region numbered N+1.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellMultiArrowConstraintsE.NEXT_NUMBERED_REGION_DISTANCE_ARROWS
    prefix = f"{key.value}"

    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)

    grid = puzzle.grid
    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    # all_cells = grid.getAllCells()

    for _, (cell, cell_var, arrows, _) in enumerate(genSingleCellMultiArrowConstraintProperties(model, puzzle, key)):
        cell_region_var = cell2var(regions_grid, cell)

        for direction in arrows:
            prefix2 = f"{prefix} - {cell.format_cell()}, {direction}"
            cells_in_direction = grid.getCellsInDirection(cell, direction)
            cells_regions_in_direction_vars = cells2vars(
                regions_grid, cells_in_direction)
            n = len(cells_in_direction)
            model.Add(cell_var <= n)
            idx_var = model.NewIntVar(0, n - 1, f"{prefix2} - idx_var")
            model.Add(idx_var == cell_var - 1)
            region_target = model.NewIntVar(
                0, 9, f"{prefix2} - region_target")
            model.AddElement(
                idx_var, cells_regions_in_direction_vars, region_target)
            model.Add(region_target == cell_region_var + 1)


def set_region_loop_sum_cell_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A small clue in the top left corner of a cell indicates the sum of the digits in all cells visited by the loop in
     that cell's region.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.REGION_LOOP_SUM_CELL
    prefix = f"{key.value}"

    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)
    grid = puzzle.grid
    cells_grid_vars = model.grid_vars_dict['cells_grid_vars']
    all_cells = grid.getAllCells()

    loop_bools_grid, _ = get_or_set_cell_center_loop_constraint(
        model, puzzle)

    constraint_cells = [
        cell for (cell, _, _) in genSingleCellConstraintProperties(model, puzzle, key)]
    cells_region_vars = cells2vars(regions_grid, constraint_cells)
    model.AddAllDifferent(cells_region_vars)

    all_cells_vars = cells2vars(cells_grid_vars, all_cells)
    min_digit = min(puzzle.valid_digits)
    ub = sum(puzzle.valid_digits)

    for i, (cell, _, value) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        cell_region_var = cell2var(regions_grid, cell)

        sum_var = model.get_or_set_shared_var(
            value, min_digit, ub, f"{prefix} {i}: sum_var")

        name = f"{prefix} - region of {cell.format_cell()} and loop"
        same_region_loop_bools_dict = bool_vars_grid_dict_from_puzzle_grid(
            model, grid, name)
        model.grid_vars_dict[name] = same_region_loop_bools_dict

        for cell2 in all_cells:
            cell2_region_var = cell2var(regions_grid, cell2)
            cell2_loop_var = cell2var(loop_bools_grid, cell2)
            name = f"{prefix} - same region as {cell.format_cell()} - {cell2.format_cell()}"
            same_region_bool = are_all_equal_csp(
                model, [cell_region_var, cell2_region_var], name)

            name = f"{prefix} - same region and loop as {cell.format_cell()} - {cell2.format_cell()}"
            same_region_and_loop_bool_2 = are_all_true_csp(
                model, [same_region_bool, cell2_loop_var], name)

            same_region_and_loop_bool = cell2var(
                same_region_loop_bools_dict, cell2)

            model.Add(same_region_and_loop_bool == same_region_and_loop_bool_2)

        same_region_loop_bools = cells2vars(
            same_region_loop_bools_dict, all_cells)
        masked_sum = masked_sum_csp(model, all_cells_vars, same_region_loop_bools,
                                    f"{prefix} - {cell.format_cell()} loop_sum")
        model.Add(masked_sum == sum_var)


def set_count_cells_not_in_the_same_region_arrows_constraints(model: PuzzleModel,
                                                              puzzle: Puzzle):
    """
    A cell with an arrow (or arrows) indicates how many cells in the indicated directions combined that do not belong to the same region as that cell.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellMultiArrowConstraintsE.COUNT_CELLS_NOT_IN_THE_SAME_REGION_ARROWS
    prefix = f"{key.value}"

    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)
    grid = puzzle.grid
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)
    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    # all_cells = grid.getAllCells()

    for i, (cell, cell_var, arrows, _) in enumerate(genSingleCellMultiArrowConstraintProperties(model, puzzle, key)):
        cell_region_var = cell2var(regions_grid, cell)

        sum_var = model.get_or_set_shared_var(
            None, min_digit, max_digit, f"{prefix} {i} - sum_var")

        direction_counts: list[IntVar] = []
        for direction in arrows:
            prefix2 = f"{prefix} {i} - {cell.format_cell()}, {direction}"
            cells_in_direction = grid.getCellsInDirection(cell, direction)

            cells_regions_vars_in_direction = cells2vars(
                regions_grid, cells_in_direction)

            name = f"{prefix2} - count"
            count_var = count_different_vars(
                model, cells_regions_vars_in_direction, cell_region_var, name)

            direction_counts.append(count_var)

        model.Add(sum(direction_counts) == sum_var)
        model.Add(sum_var == cell_var)
