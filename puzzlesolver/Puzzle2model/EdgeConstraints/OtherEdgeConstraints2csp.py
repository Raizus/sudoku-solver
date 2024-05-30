
from puzzlesolver.Puzzle.ConstraintEnums import EdgeConstraintsE, LocalConstraintsModifiersE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.EdgeConstraints.utils import genEdgeConstraintProperties
from puzzlesolver.Puzzle2model.OtherConstraints.AmbiguousEntropyConstraints2csp import get_or_set_ambiguous_entropy_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownRegionsConstraints2csp import get_or_set_unknown_regions_grid
from puzzlesolver.Puzzle2model.OtherConstraints.YinYangConstraints2csp import get_or_set_yin_yang_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import are_consecutive_csp, is_ratio_1_r_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, cells2vars


def set_yin_yang_kropki_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The given grey dots indicate that the two connected cells have the same colour.
    If a grey dot is between two black cells their digits are in a 1:2 ratio;
    if a grey dot is between two white cells, their digits are consecutive.
    ALL possible grey dots are given. [ie At the end of the puzzle, when all the cells are coloured and all the
    numbers are entered, two adjacent black cells may contain digits in a ratio of 1:2 only if there is a gray dot
    between them. Similarly, two adjacent white cells may contain consecutive numbers only if there is a grey dot
    between them. The following scenarios are possible without any problems: Two consecutive numbers in adjacent
    black cells; two digits in the ratio 1:2 in adjacent white cells; and any relationship between digits in
    adjacent cells with different colour.]

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = EdgeConstraintsE.YIN_YANG_KROPKI
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid_vars = model.grid_vars_dict['cells_grid_vars']
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for i, (cells, cells_vars, _) in enumerate(genEdgeConstraintProperties(model, puzzle, key)):
        cell1, cell2 = cells[0], cells[1]
        cell1_var = cells_vars[0]
        cell2_var = cells_vars[1]

        # cells have same shade
        yin_yang_var1 = cell2var(yin_yang_grid, cell1)
        yin_yang_var2 = cell2var(yin_yang_grid, cell2)
        model.Add(yin_yang_var1 == yin_yang_var2)

        # yin_yang_var1 == 0 (unshaded) -> ratio
        is_ratio = is_ratio_1_r_csp(
            model, cell1_var, cell2_var, 2, f"{prefix}_{i}")
        model.Add(is_ratio == 1).OnlyEnforceIf(yin_yang_var1.Not())

        # yin_yang_var1 == 1 (shaded) -> difference
        is_consecutive = are_consecutive_csp(
            model, cell1_var, cell2_var, f"{prefix}_{i}")
        model.Add(is_consecutive == 1).OnlyEnforceIf(yin_yang_var1)

    # all dots given
    all_yin_yang_kropki_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_YIN_YANG_KROPKI_GIVEN, False)

    if not all_yin_yang_kropki_given:
        return

    cell_pairs = [cells for cells, _, _ in genEdgeConstraintProperties(
        model, puzzle, EdgeConstraintsE.YIN_YANG_KROPKI)]

    for cell1, cell2 in puzzle.grid.genAllAdjacentPairs():
        kropki_with_both_cells = [
            cell_pair for cell_pair in cell_pairs if cell1 in cell_pair and cell2 in cell_pair]
        if len(kropki_with_both_cells):
            continue

        cell1_var = cell2var(grid_vars, cell1)
        cell2_var = cell2var(grid_vars, cell2)
        cell1_color = cell2var(yin_yang_grid, cell1)
        cell2_color = cell2var(yin_yang_grid, cell2)

        # if both black (cell_color == 0) -> can't be ratio
        prefix2 = f"{prefix} - all_kropki_given - {cell1.format_cell()}_{cell2.format_cell()}"
        is_ratio = is_ratio_1_r_csp(model, cell1_var, cell2_var, 2, prefix2)

        both_black_bool = model.NewBoolVar(
            f"{prefix2} both_black")
        model.AddBoolAnd(cell1_color.Not(), cell2_color.Not()
                         ).OnlyEnforceIf(both_black_bool)
        model.AddBoolOr(cell1_color, cell2_color).OnlyEnforceIf(
            both_black_bool.Not())

        model.Add(is_ratio == 0).OnlyEnforceIf(both_black_bool)

        # if both white (cell_color == 1) -> can't be consecutive
        is_consecutive = are_consecutive_csp(
            model, cell1_var, cell2_var, prefix2)
        both_white_bool = model.NewBoolVar(
            f"{prefix2} both_white")
        model.AddBoolAnd(cell1_color, cell2_color).OnlyEnforceIf(
            both_white_bool)
        model.AddBoolOr(cell1_color.Not(), cell2_color.Not()
                        ).OnlyEnforceIf(both_white_bool.Not())

        model.Add(is_consecutive == 0).OnlyEnforceIf(both_white_bool)


def set_same_ambiguous_entropy_border_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers that appear in the cells with a white dot between must be from the same entropy set.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = EdgeConstraintsE.SAME_AMBIGUOUS_ENTROPY_EDGE
    # prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # grid_vars = model.grid_vars_dict['cells_grid_vars']
    ambiguous_entropy_grid = get_or_set_ambiguous_entropy_constraint(
        model, puzzle)

    for _, (cells, _, _) in enumerate(genEdgeConstraintProperties(model, puzzle, key)):
        entropy_cells_vars = cells2vars(ambiguous_entropy_grid, cells)
        model.Add(entropy_cells_vars[0] == entropy_cells_vars[1])


def set_different_ambiguous_entropy_border_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers that appear in the cells with a black dot between must have a ratio of 2:1,
    AND from different entropy sets.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = EdgeConstraintsE.DIFFERENT_AMBIGUOUS_ENTROPY_EDGE
    # prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # grid_vars = model.grid_vars_dict['cells_grid_vars']
    ambiguous_entropy_grid = get_or_set_ambiguous_entropy_constraint(
        model, puzzle)

    for _, (cells, _, _) in enumerate(genEdgeConstraintProperties(model, puzzle, key)):
        entropy_cells_vars = cells2vars(ambiguous_entropy_grid, cells)
        model.Add(entropy_cells_vars[0] != entropy_cells_vars[1])


def set_unknown_region_border_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Black lines between cell borders represent region borders.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = EdgeConstraintsE.UNKNOWN_REGION_BORDER
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)

    for _, (cells, _, _) in enumerate(genEdgeConstraintProperties(model, puzzle, key)):
        cell1, cell2 = cells
        region_var1 = cell2var(regions_grid, cell1)
        region_var2 = cell2var(regions_grid, cell2)

        model.Add(region_var1 != region_var2)
