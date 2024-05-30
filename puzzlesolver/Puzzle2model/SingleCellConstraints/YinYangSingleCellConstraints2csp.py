
from puzzlesolver.Puzzle.ConstraintEnums import SingleCellConstraintsE, SingleCellMultiArrowConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OtherConstraints.YinYangConstraints2csp import get_or_set_yin_yang_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.SingleCellConstraints.utils import genSingleCellConstraintProperties, genSingleCellMultiArrowConstraintProperties
from puzzlesolver.Puzzle2model.custom_constraints import count_uninterrupted_left_right_csp, count_vars
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, cells2vars
from ortools.sat.python.cp_model import IntVar


def set_yin_yang_seen_unshaded_cells_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Black circles represent unshaded cells. A digit on a circle is equal to the number of consecutive unshaded cells
    (including itself) the circle sees in its row and column.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    constraints_list = puzzle.tool_constraints.get(
        SingleCellConstraintsE.YIN_YANG_SEEN_UNSHADED_CELLS)
    if not len(constraints_list):
        return

    grid = puzzle.grid

    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for _, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.YIN_YANG_SEEN_UNSHADED_CELLS)):
        row_cells = grid.getRow(cell.row)
        col_cells = grid.getCol(cell.col)

        yin_yang_row = cells2vars(yin_yang_grid, row_cells)
        yin_yang_col = cells2vars(yin_yang_grid, col_cells)
        yin_yang_intersection = cell2var(yin_yang_grid, cell)
        idx_row = row_cells.index(cell)
        idx_col = col_cells.index(cell)

        count_uninterrupted_row = count_uninterrupted_left_right_csp(
            model, yin_yang_row, idx_row, 0)
        count_uninterrupted_col = count_uninterrupted_left_right_csp(
            model, yin_yang_col, idx_col, 0)

        model.Add(yin_yang_intersection == 0)
        model.Add(count_uninterrupted_row +
                  count_uninterrupted_col + 1 == cell_var)


def set_yin_yang_seen_shaded_cells_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Yellow circles represent shaded cells. A digit on a circle is equal to the number of consecutive shaded cells
    (including itself) the circle sees in its row and column.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    constraints_list = puzzle.tool_constraints.get(
        SingleCellConstraintsE.YIN_YANG_SEEN_SHADED_CELLS)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for _, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.YIN_YANG_SEEN_SHADED_CELLS)):
        row_cells = grid.getRow(cell.row)
        col_cells = grid.getCol(cell.col)

        yin_yang_row = cells2vars(yin_yang_grid, row_cells)
        yin_yang_col = cells2vars(yin_yang_grid, col_cells)
        yin_yang_intersection = cell2var(yin_yang_grid, cell)
        idx_row = row_cells.index(cell)
        idx_col = col_cells.index(cell)

        count_uninterrupted_row = count_uninterrupted_left_right_csp(
            model, yin_yang_row, idx_row, 1)
        count_uninterrupted_col = count_uninterrupted_left_right_csp(
            model, yin_yang_col, idx_col, 1)

        model.Add(yin_yang_intersection == 1)
        model.Add(count_uninterrupted_row +
                  count_uninterrupted_col + 1 == cell_var)


def set_yin_yang_minesweeper_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Circles act as 'minesweeper' clues. Cells containing a circle are always unshaded, and their value is the number
    of shaded cells in the surrounding 3x3 area (i.e. the up to eight cells that touch the circle either orthogonally
    or diagonally).

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    constraints_list = puzzle.tool_constraints.get(
        SingleCellConstraintsE.YIN_YANG_MINESWEEPER)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for _, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.YIN_YANG_MINESWEEPER)):
        surround_cells = grid.getNeighbourCells(cell)
        yin_yang_surround_cells = cells2vars(
            yin_yang_grid, surround_cells)
        yin_yang_cell_var = cell2var(yin_yang_grid, cell)
        model.Add(yin_yang_cell_var == 0)
        model.Add(sum(yin_yang_surround_cells) == cell_var)


def set_yin_yang_same_color_adjacent_count_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers in cells with yellow diamonds indicate how many of that cell's (up to four) orthogonal neighbours share
    the same shading as the cell.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    constraints_list = puzzle.tool_constraints.get(
        SingleCellConstraintsE.YIN_YANG_SAME_COLOR_ADJACENT_COUNT)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)
    prefix = f"yin_yang_same_color_adjacent_count"

    for _, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.YIN_YANG_SAME_COLOR_ADJACENT_COUNT)):

        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        yin_yang_adjacent_vars = cells2vars(yin_yang_grid, adjacent_cells)
        yin_yang_cell_var = cell2var(yin_yang_grid, cell)
        n = len(adjacent_cells)
        count_adjacent_unshaded = model.NewIntVar(
            0, n, f"{prefix} - count_adjacent_shaded_{cell.format_cell()}")
        count_adjacent_shaded = count_vars(model, yin_yang_adjacent_vars, 1,
                                           f"{prefix} - count_adjacent_shaded_{cell.format_cell()}")
        model.Add(count_adjacent_unshaded + count_adjacent_shaded == n)

        model.Add(cell_var == count_adjacent_shaded).OnlyEnforceIf(
            yin_yang_cell_var)
        model.Add(cell_var == count_adjacent_unshaded).OnlyEnforceIf(
            yin_yang_cell_var.Not())


def set_yin_yang_shaded_cell_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Cell is a shaded yin yang cell.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    constraints_list = puzzle.tool_constraints.get(
        SingleCellConstraintsE.YIN_YANG_SHADED_CELL)
    if not len(constraints_list):
        return

    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for _, (cell, _, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.YIN_YANG_SHADED_CELL)):
        yin_yang_cell_var = cell2var(yin_yang_grid, cell)
        model.Add(yin_yang_cell_var == 1)


def set_yin_yang_unshaded_cell_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Cell is an unshaded yin yang cell.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    constraints_list = puzzle.tool_constraints.get(
        SingleCellConstraintsE.YIN_YANG_UNSHADED_CELL)
    if not len(constraints_list):
        return

    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for _, (cell, _, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.YIN_YANG_UNSHADED_CELL)):
        yin_yang_cell_var = cell2var(yin_yang_grid, cell)
        model.Add(yin_yang_cell_var == 0)


def set_yin_yang_shaded_cell_count_in_directions_except_itself_constraints(model: PuzzleModel,
                                                                           puzzle: Puzzle):
    """
    The digit in a cell with one or more arrows is equal to the total number of shaded cells that appear in the
    indicated directions combined (not including the arrow cell itself).

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellMultiArrowConstraintsE.YIN_YANG_SHADED_CELL_COUNT_IN_DIRECTIONS_EXCEPT_ITSELF
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    prefix = f"{key.value}"
    grid = puzzle.grid
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    for _, (cell, cell_var, arrows, _) in enumerate(genSingleCellMultiArrowConstraintProperties(model, puzzle, key)):
        counts: list[IntVar] = []
        for direction in arrows:
            cells_in_direction = grid.getCellsInDirection(cell, direction)
            yin_yang_vars_in_direction = cells2vars(
                yin_yang_grid, cells_in_direction)
            count_in_dir = model.NewIntVar(0, len(yin_yang_vars_in_direction),
                                           f"{prefix} - {cell.format_cell()}, {direction} count_in_dir")
            model.Add(sum(yin_yang_vars_in_direction) == count_in_dir)
            counts.append(count_in_dir)
        model.Add(sum(counts) == cell_var)
