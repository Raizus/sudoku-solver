
from puzzlesolver.Puzzle.ConstraintEnums import GlobalRegionConstraintsE, ValueModifierConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OtherConstraints.AmbiguousEntropyConstraints2csp import get_or_set_ambiguous_entropy_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.CenterCellsLoopConstraints2csp import get_or_set_cell_center_loop_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.LShapedRegionsConstraints2csp import get_or_set_l_shaped_regions_grid
from puzzlesolver.Puzzle2model.OtherConstraints.YinYangConstraints2csp import get_or_set_yin_yang_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import count_vars, reif2
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, cells2vars, get_or_set_marked_cells_constraint, int_vars_grid_dict_from_puzzle_grid
from puzzlesolver.Puzzle2model.BoolConstraints.puzzle_values_modifiers import get_or_set_cold_cells_constraint, get_or_set_decrement_fountain_constraint, get_or_set_doublers_grid, get_or_set_hot_cells_constraint, get_or_set_vampires_prey_constraint


def set_vampires_prey_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        ValueModifierConstraintsE.VAMPIRE_AND_PREY, False)
    if constraint:
        get_or_set_vampires_prey_constraint(model, puzzle)


def set_doublers_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        ValueModifierConstraintsE.DOUBLERS, False)
    if constraint:
        get_or_set_doublers_grid(model, puzzle)


def set_decrement_fountain_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        ValueModifierConstraintsE.DECREMENT_FOUNTAINS, False)
    if constraint:
        get_or_set_decrement_fountain_constraint(model, puzzle)


def set_marked_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        ValueModifierConstraintsE.MARKED_CELLS, False)
    if constraint:
        get_or_set_marked_cells_constraint(model, puzzle)


def set_hot_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        ValueModifierConstraintsE.HOT_CELLS, False)
    if constraint:
        get_or_set_hot_cells_constraint(model, puzzle)


def set_cold_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        ValueModifierConstraintsE.COLD_CELLS, False)
    if constraint:
        get_or_set_cold_cells_constraint(model, puzzle)


def set_cell_cannot_be_both_hot_and_cold_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        ValueModifierConstraintsE.CELL_CANNOT_BE_BOTH_HOT_AND_COLD, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars_dict = model.grid_vars_dict
    all_cells = grid.getAllCells()

    get_or_set_cold_cells_constraint(model, puzzle)
    get_or_set_hot_cells_constraint(model, puzzle)

    cold_cells_bool_grid = grid_vars_dict["cold_cells_bool_grid"]
    hot_cells_bool_grid = grid_vars_dict["hot_cells_bool_grid"]

    for cell in all_cells:
        hot_bool_var = cell2var(hot_cells_bool_grid, cell)
        cold_bool_var = cell2var(cold_cells_bool_grid, cell)
        model.AddBoolOr(hot_bool_var.Not(), cold_bool_var.Not())


def set_yin_yang_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.YIN_YANG, False)
    if constraint:
        get_or_set_yin_yang_constraint(model, puzzle)


def set_l_shaped_regions_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.L_SHAPED_REGIONS, False)
    if constraint:
        get_or_set_l_shaped_regions_grid(model, puzzle)


def set_crossed_paths_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A path consisting of the digits 1 to 9, in order, crosses from left to right across the grid with each digit in
    its corresponding column (1 in column 1, 2 in column 2, etc.) The cells along the path
    are connected orthogonally or diagonally. A similar path crosses the grid from top to bottom,
    starting with a 1 in row 1, then a 2 in row 2, ending with a 9 in row 9.
    Again, cells along the path are connected orthogonally or diagonally. The paths (which do not share cells,
    nor appear in any cage) are to be determined by the solver.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """

    constraint = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.CROSSED_PATHS, False)
    if not constraint:
        return

    prefix = f"crossed_paths"
    grid = puzzle.grid
    grid_vars = model.grid_vars_dict['cells_grid_vars']

    n_rows = grid.nRows
    n_cols = grid.nCols
    # tool_constraints = puzzle.tool_constraints
    # killer_cage_list: List[KillerCage] = tool_constraints.get(
    #     CageConstraints.KILLER_CAGE)

    crossed_paths_grid = int_vars_grid_dict_from_puzzle_grid(
        model, grid, 0, 2, f"crossed_paths")

    # paths do not appear in cages
    # for i, cage in enumerate(killer_cage_list):
    #     cells = cage.cells
    #     crossed_paths_cage_vars = cells2vars(crossed_paths_grid, cells)
    #     for crossed_paths_cage_var in crossed_paths_cage_vars:
    #         model.Add(crossed_paths_cage_var == 0)

    # A path consisting of the digits 1 to 9, in order, crosses from top to bottom across the grid with each digit in its corresponding row (1 in row 1, 2 in row 2, etc.) The cells along the path are connected orthogonally or diagonally.

    # One path cell in each row
    for row in range(0, n_rows):
        cells = grid.getRow(row)
        crossed_paths_row_vars = cells2vars(crossed_paths_grid, cells)
        path_1_row_count = count_vars(
            model, crossed_paths_row_vars, 1, f"{prefix} - path_1_count_row_{row}")
        model.Add(path_1_row_count == 1)

        # each digit in the path is equal to it's corresponding row (1 in row 1, 2 in row 2, etc.)
        for cell in cells:
            cell_var = cell2var(grid_vars, cell)
            path_var = cell2var(crossed_paths_grid, cell)
            # if path_var == 1 => cell == row + 1
            cell_is_path = reif2(model, path_var == 1, path_var != 1,
                                 f"{prefix} - cell_is_path_1 - {cell.format_cell()}")
            model.Add(cell_var == row + 1).OnlyEnforceIf(cell_is_path)

    # The cells along the path are connected orthogonally or diagonally.
    for row in range(1, n_rows):
        row_cells = grid.getRow(row)
        for cell in row_cells:
            neighbours = grid.getNeighbourCells(cell)
            neighbours = [
                _cell for _cell in neighbours if _cell.row < cell.row]
            crossed_path_neighbours_vars = cells2vars(
                crossed_paths_grid, neighbours)
            crossed_path_cell_var = cell2var(crossed_paths_grid, cell)

            # if count_1 == 0 => crossed_path_cell_var != 1 (could be 2 tho)
            name = f"{prefix} - {cell.format_cell()}_previous_row_neighbours, count_1"
            count_1 = count_vars(model, crossed_path_neighbours_vars, 1, name)
            name = f"{prefix} - {cell.format_cell()}_previous_row_neighbours, count_1_is_zero"
            count_1_is_zero = reif2(model, count_1 == 0, count_1 != 0, name)
            model.Add(crossed_path_cell_var !=
                      1).OnlyEnforceIf(count_1_is_zero)

    # A path consisting of the digits 1 to 9, in order, crosses from left to right across the grid with each digit in its corresponding column (1 in column 1, 2 in column 2, etc.) The cells along the path are connected orthogonally or diagonally.
    for col in range(0, n_cols):
        cells = grid.getCol(col)
        crossed_paths_col_vars = cells2vars(crossed_paths_grid, cells)
        path_2_col_count = count_vars(
            model, crossed_paths_col_vars, 2, f"{prefix} - path_2_count_col_{col}")
        model.Add(path_2_col_count == 1)

        for cell in cells:
            cell_var = cell2var(grid_vars, cell)
            path_var = cell2var(crossed_paths_grid, cell)
            # if path_var == 2 => cell == col + 1
            cell_is_path = reif2(model, path_var == 2, path_var != 2, f"{prefix} - "
                                                                      f"cell_is_path_2 - {cell.format_cell()}")
            model.Add(cell_var == col + 1).OnlyEnforceIf(cell_is_path)

    for col in range(1, n_cols):
        cells = grid.getCol(col)
        for cell in cells:
            neighbours = grid.getNeighbourCells(cell)
            neighbours = [
                _cell for _cell in neighbours if _cell.col < cell.col]
            crossed_path_neighbours_vars = cells2vars(
                crossed_paths_grid, neighbours)
            crossed_path_cell_var = cell2var(crossed_paths_grid, cell)

            # if count_2 == 0 => crossed_path_cell_var != 2 (could be 1 tho)
            name = f"{prefix} - {cell.format_cell()}_previous_col_neighbours, count_2"
            count_2 = count_vars(model, crossed_path_neighbours_vars, 2, name)
            name = f"{prefix} - {cell.format_cell()}_previous_col_neighbours, count_2_is_zero"
            count_2_is_zero = reif2(model, count_2 == 0, count_2 != 0, name)
            model.Add(crossed_path_cell_var !=
                      2).OnlyEnforceIf(count_2_is_zero)

    model.grid_vars_dict["crossed_paths_grid"] = crossed_paths_grid


def set_center_cell_loop_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = GlobalRegionConstraintsE.CENTER_CELLS_LOOP
    constraint = puzzle.bool_constraints.get(key, False)
    if constraint:
        get_or_set_cell_center_loop_constraint(model, puzzle)


def set_ambiguous_entropy_constraint(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.AMBIGUOUS_ENTROPY, False)
    if constraint:
        get_or_set_ambiguous_entropy_constraint(model, puzzle)


#     elif key == BoolConstraints.UNKNOWN_REGIONS:
#         get_or_set_unknown_regions_grid(model, grid_vars_dict, puzzle)
#     elif key == BoolConstraints.NUMBERED_UNKNOWN_REGIONS:
#         get_or_set_unknown_regions_grid(model, grid_vars_dict, puzzle)
#     elif key == BoolConstraints.NINE_3X3_REGIONS:
#         set_nine_3x3_unknown_regions_constraint(
#             model, grid_vars_dict, puzzle)
