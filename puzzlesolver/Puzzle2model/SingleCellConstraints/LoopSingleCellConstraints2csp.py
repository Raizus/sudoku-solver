

from puzzlesolver.Puzzle.ConstraintEnums import SingleCellConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OtherConstraints.CellEdgeLoopConstraints2csp import get_or_set_edge_loop_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.SingleCellConstraints.utils import genSingleCellConstraintProperties
from puzzlesolver.Puzzle2model.custom_constraints import count_uninterrupted_left_right_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, cells2vars


def set_cell_inside_edge_loop_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Green Cells are inside the edge loop.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.CELL_INSIDE_EDGE_LOOP
    # prefix = f"{key.value}"
    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    inside_outside_edge_loop_dict = get_or_set_edge_loop_constraint(
        model, puzzle)

    for _, (cell, _, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        inside_outside_edge_loop = cell2var(
            inside_outside_edge_loop_dict, cell)
        model.Add(inside_outside_edge_loop == 1)


def set_cell_outside_edge_loop_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Grey cells are outside the edge loop.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.CELL_OUTSIDE_EDGE_LOOP
    # prefix = f"{key.value}"
    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    inside_outside_edge_loop_dict = get_or_set_edge_loop_constraint(
        model, puzzle)
    for _, (cell, _, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        inside_outside_edge_loop = cell2var(
            inside_outside_edge_loop_dict, cell)
        model.Add(inside_outside_edge_loop == 0)


def set_count_seen_cells_inside_edge_loop_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A digit in a white circle is inside the loop and indicates the number of cells inside the loop “seen” horizontally
    and vertically, including the circled cell itself. Cells outside the loop obstruct vision.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.COUNT_SEEN_CELLS_INSIDE_EDGE_LOOP
    # prefix = f"{key.value}"
    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    grid = puzzle.grid

    inside_outside_edge_loop_dict = get_or_set_edge_loop_constraint(
        model, puzzle)

    for _, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        row = grid.getRow(cell.row)
        col = grid.getCol(cell.col)

        inside_outside_edge_loop_row = cells2vars(
            inside_outside_edge_loop_dict, row)
        inside_outside_edge_loop_col = cells2vars(
            inside_outside_edge_loop_dict, col)
        inside_outside_edge_loop_intersection = cell2var(
            inside_outside_edge_loop_dict, cell)
        idx_row = row.index(cell)
        idx_col = col.index(cell)

        count_uninterrupted_row = count_uninterrupted_left_right_csp(
            model, inside_outside_edge_loop_row, idx_row, 1)
        count_uninterrupted_col = count_uninterrupted_left_right_csp(
            model, inside_outside_edge_loop_col, idx_col, 1)

        model.Add(inside_outside_edge_loop_intersection == 1)
        model.Add(count_uninterrupted_row +
                  count_uninterrupted_col + 1 == cell_var)


def set_count_cell_edges_belonging_to_edge_loop_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A digit in a white square indicates the number of that cell's edges that are part of the edge loop.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    key = SingleCellConstraintsE.COUNT_CELL_EDGES_BELONGING_TO_EDGE_LOOP
    # prefix = f"{key.value}"
    constraint_list = puzzle.tool_constraints.get(key)
    if not len(constraint_list):
        return

    grid_vars_dict = model.grid_vars_dict
    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    get_or_set_edge_loop_constraint(model, puzzle)
    horizontal_loop_edges = grid_vars_dict["horizontal_loop_edges"]
    vertical_loop_edges = grid_vars_dict["vertical_loop_edges"]

    for _, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, key)):
        model.Add(cell_var <= 4)
        edges = [horizontal_loop_edges.get((cell.row, cell.col)),
                 horizontal_loop_edges.get((cell.row + 1, cell.col)),
                 vertical_loop_edges.get((cell.row, cell.col)),
                 vertical_loop_edges.get((cell.row, cell.col + 1))]
        edges = [x for x in edges if x is not None]
        model.Add(sum(edges) == cell_var)
