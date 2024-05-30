
from collections import Counter
from puzzlesolver.Puzzle.ConstraintEnums import SimpleGlobalConstraintsE
from puzzlesolver.Puzzle.Directions import getDirections
from puzzlesolver.Puzzle.Puzzle import Puzzle

from puzzlesolver.Puzzle2model.OtherConstraints.UnknownEmptyCellsConstraints2csp import get_or_set_unknown_empty_cells_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import are_all_true_csp, are_consecutive_csp, at_least_n_in_each_group_csp, masked_count_vars, count_unique_values, count_vars, distance_csp, is_even_csp, is_increasing_strict_csp, is_magic_square_csp, is_member_of, is_odd_csp, is_ratio_1_r_csp, is_sum_csp, modulo_count_csp, nonconsecutive_csp, reif2, same_remainder_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars, orthogonally_connected_region_csp
from ortools.sat.python.cp_model import IntVar

from puzzlesolver.Puzzle2model.puzzle_model_types import build_adjacency_dict


def set_sudoku_constraints(model: PuzzleModel, puzzle: Puzzle):
    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.NORMAL_SUDOKU_RULES_DO_NOT_APPLY, False)
    if constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    # AllDifferent on rows.
    for i in range(0, grid.nRows):
        row_cells = grid.getRow(i)
        row_vars = cells2vars(grid_vars, row_cells)
        model.AddAllDifferent(row_vars)

    # AllDifferent on cols.
    for j in range(0, grid.nCols):
        col_cells = grid.getCol(j)
        col_vars = cells2vars(grid_vars, col_cells)
        model.AddAllDifferent(col_vars)

    # AllDifferent on boxes.
    for i in grid.getUsedRegions():
        box_cells = grid.getRegionCells(i)
        box_vars = cells2vars(grid_vars, box_cells)
        model.AddAllDifferent(box_vars)


def set_sudoku_constraints_with_unknown_empty_cells_constraints(model: PuzzleModel, puzzle: Puzzle):
    key1 = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key1, False)
    key2 = SimpleGlobalConstraintsE.NORMAL_SUDOKU_RULES_DO_NOT_APPLY
    sudoku_rules_apply = not puzzle.bool_constraints.get(key2, False)

    if not (unknown_empty_cells and sudoku_rules_apply):
        return

    grid_vars_dict = model.grid_vars_dict
    filled_cells_grid = get_or_set_unknown_empty_cells_constraint(
        model, puzzle)
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid
    valid_digits = puzzle.valid_digits
    prefix = f"sudoku_constraints_with_unknown_empty_cells"

    # AllDifferent on rows.
    for i in range(0, grid.nRows):
        row_cells = grid.getRow(i)
        row_vars = cells2vars(cells_grid_vars, row_cells)
        filled_cells_bool_row = cells2vars(filled_cells_grid, row_cells)
        for digit in valid_digits:
            name = f"{prefix} - row={i}, digit={digit} - count"
            count_var = masked_count_vars(
                model, row_vars, filled_cells_bool_row, digit, name)
            model.AddAllowedAssignments([count_var], [(0,), (1,)])

    # AllDifferent on cols.
    for j in range(0, grid.nCols):
        col_cells = grid.getCol(j)
        col_vars = cells2vars(cells_grid_vars, col_cells)
        filled_cells_bool_col = cells2vars(filled_cells_grid, col_cells)
        for digit in valid_digits:
            name = f"{prefix} - col={j}, digit={digit} - count"
            count_var = masked_count_vars(
                model, col_vars, filled_cells_bool_col, digit, name)
            model.AddAllowedAssignments([count_var], [(0,), (1,)])


def set_permitted_digits_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    If Sudoku rules

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key, False)

    prefix = f"permitted_digits"

    if len(set(puzzle.valid_digits)) == len(puzzle.valid_digits) or unknown_empty_cells:
        return

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid
    # Rows.
    counts = Counter(puzzle.valid_digits)
    if len(puzzle.valid_digits) == grid.nRows:
        for i in range(0, grid.nRows):
            row = grid.getRow(i)
            row_vars = cells2vars(grid_vars, row)
            for value, count in counts.items():
                digits_count = count_vars(
                    model, row_vars, value, f"{prefix} - row={i}, digit={value}")
                model.Add(digits_count == count)

    # Cols.
    if len(puzzle.valid_digits) == grid.nCols:
        for i in range(0, grid.nCols):
            col = grid.getCol(i)
            col_vars = cells2vars(grid_vars, col)

            for value, count in counts.items():
                digit_count = count_vars(
                    model, col_vars, value, f"{prefix} - col={i}, digit={value}")
                model.Add(digit_count == count)

    # Boxes.
    for i in grid.getUsedRegions():
        box_cells = grid.getRegionCells(i)
        box_vars = cells2vars(grid_vars, box_cells)

        for value, count in counts.items():
            digit_count = count_vars(
                model, box_vars, value, f"{prefix} - box={i}, digit={value}")
            model.Add(digit_count == count)


def set_pdiagonal_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = SimpleGlobalConstraintsE.POSITIVE_DIAGONAL
    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    diag_cells = grid.getPositiveDiagonal()
    if len(diag_cells):
        diag_vars = cells2vars(grid_vars, diag_cells)
        model.AddAllDifferent(diag_vars)


def set_ndiagonal_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = SimpleGlobalConstraintsE.NEGATIVE_DIAGONAL
    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    diag_cells = grid.getNegativeDiagonal()
    if len(diag_cells):
        diag_vars = cells2vars(grid_vars, diag_cells)
        model.AddAllDifferent(diag_vars)


def set_positive_antidiagonal_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The positive diagonal contains only 3 different numbers.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    key = SimpleGlobalConstraintsE.POSITIVE_ANTIDIAGONAL
    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    prefix = f"{key.value}"
    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    diag_cells = grid.getPositiveDiagonal()
    diag_vars = cells2vars(grid_vars, diag_cells)

    unique_count = count_unique_values(model, diag_vars, f"{prefix}")
    model.Add(unique_count == 3)


def set_negative_antidiagonal_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The negative diagonal contains only 3 different numbers.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    key = SimpleGlobalConstraintsE.NEGATIVE_ANTIDIAGONAL
    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    prefix = f"{key.value}"
    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    diag_cells = grid.getNegativeDiagonal()
    diag_vars = cells2vars(grid_vars, diag_cells)

    unique_count = count_unique_values(model, diag_vars, f"{prefix}")
    model.Add(unique_count == 3)


def set_odd_even_parity_mirror_along_negative_diagonal_constraint(model: PuzzleModel, puzzle: Puzzle):
    key = SimpleGlobalConstraintsE.ODD_EVEN_PARITY_MIRROR_ALONG_NEGATIVE_DIAGONAL
    prefix = f"{key.value}"

    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    diag_cells = grid.getNegativeDiagonal()
    if not len(diag_cells):
        return

    for dcell in diag_cells:
        dr, dc = dcell.row, dcell.col

        for i in range(dr):
            cell = grid.getCell(i, dc)
            mirror_cell = grid.getCell(dr, dc - (dr-i))

            if cell is None or mirror_cell is None:
                continue

            cell_var = cell2var(grid_vars, cell)
            mirror_cell_var = cell2var(grid_vars, mirror_cell)

            name = f"{prefix} - {cell.format_cell()}_{mirror_cell.format_cell()}"
            same_residue_bool = same_remainder_csp(
                model, cell_var, mirror_cell_var, 2, name)
            model.Add(same_residue_bool == 1)


def set_odd_even_parity_mirror_along_positive_diagonal_constraint(model: PuzzleModel,
                                                                  puzzle: Puzzle):
    prefix = f"odd_even_parity_mirror_along_positive_diagonal"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.ODD_EVEN_PARITY_MIRROR_ALONG_POSITIVE_DIAGONAL, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    diag_cells = grid.getPositiveDiagonal()
    if not len(diag_cells):
        return

    for dcell in diag_cells:
        dr, dc = dcell.row, dcell.col

        for i in range(dr):
            cell = grid.getCell(i, dc)
            mirror_cell = grid.getCell(dr, dc + (dr-i))

            if cell is None or mirror_cell is None:
                continue

            cell_var = cell2var(grid_vars, cell)
            mirror_cell_var = cell2var(grid_vars, mirror_cell)

            name = f"{prefix} - {cell.format_cell()}_{mirror_cell.format_cell()}"
            same_residue_bool = same_remainder_csp(
                model, cell_var, mirror_cell_var, 2, name)
            model.Add(same_residue_bool == 1)


def set_antiknight_constraints(model: PuzzleModel, puzzle: Puzzle):
    # prefix = f"antiknight"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.ANTIKNIGHT, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for cell in grid.getAllCells():
        cell_var = cell2var(grid_vars, cell)
        knight_moves = grid.getKnigthMoveCells(cell)
        filtered = [_cell for _cell in knight_moves if _cell.row > cell.row]
        for cell2 in filtered:
            _cell_var = cell2var(grid_vars, cell2)
            model.Add(cell_var != _cell_var)


def set_antiking_constraints(model: PuzzleModel, puzzle: Puzzle):
    # prefix = f"antiking"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.ANTIKING, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for cell in grid.getAllCells():
        cell_var = cell2var(grid_vars, cell)
        king_moves = grid.getNeighbourCells(cell)
        filtered = [cell2 for cell2 in king_moves if cell2.row +
                    cell2.col >= cell.row + cell.col]
        for _cell in filtered:
            _cell_var = cell2var(grid_vars, _cell)
            model.Add(cell_var != _cell_var)


def set_nonconsecutive_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = SimpleGlobalConstraintsE.NONCONSECUTIVE
    prefix = f"{key.value}"

    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    key2 = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key2, False)

    for cell1, cell2 in grid.genAllAdjacentPairs():
        cell1_var = cell2var(grid_vars, cell1)
        cell2_var = cell2var(grid_vars, cell2)

        if not unknown_empty_cells:
            nonconsecutive_csp(model, cell1_var, cell2_var)
            continue

        # if there are unknown empty cells
        filled_cells_grid = get_or_set_unknown_empty_cells_constraint(
            model, puzzle)
        cell1_filled_var = cell2var(filled_cells_grid, cell1)
        cell2_filled_var = cell2var(filled_cells_grid, cell2)

        name = f"{prefix} - unknown_empty_cells - {cell1.format_cell()}, {cell2.format_cell()} both_filled_var"
        both_filled_var = are_all_true_csp(
            model, [cell1_filled_var, cell2_filled_var], name)

        name = f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()} - are_consecutive_bool"
        are_consecutive_bool = are_consecutive_csp(
            model, cell1_var, cell2_var, name)

        model.Add(are_consecutive_bool ==
                  0).OnlyEnforceIf(both_filled_var)


def set_nonratio_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = SimpleGlobalConstraintsE.NONRATIO
    prefix = f"{key.value}"

    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    key2 = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key2, False)

    for cell1, cell2 in grid.genAllAdjacentPairs():
        cell1_var = cell2var(grid_vars, cell1)
        cell2_var = cell2var(grid_vars, cell2)

        if not unknown_empty_cells:
            model.Add(2 * cell1_var != cell2_var)
            model.Add(2 * cell2_var != cell1_var)
            continue

        # if there are unknown empty cells
        filled_cells_grid = get_or_set_unknown_empty_cells_constraint(
            model, puzzle)
        cell1_filled_var = cell2var(filled_cells_grid, cell1)
        cell2_filled_var = cell2var(filled_cells_grid, cell2)

        name = f"{prefix} - unknown_empty_cells - {cell1.format_cell()}, {cell2.format_cell()} both_filled_var"
        both_filled_var = are_all_true_csp(
            model, [cell1_filled_var, cell2_filled_var], name)

        name = f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()} - are_ratio_bool"
        are_ratio_bool = is_ratio_1_r_csp(
            model, cell1_var, cell2_var, 2, name)

        model.Add(are_ratio_bool == 0).OnlyEnforceIf(both_filled_var)


def set_disjoint_groups_constraints(model: PuzzleModel, puzzle: Puzzle):
    # prefix = f"disjoint_groups"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.DISJOINT_GROUPS, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    regions = grid.getUsedRegions()
    for idx, _ in enumerate(regions):
        disjoint_group = grid.getCellsInDisjointGroup(idx)
        disjoint_group_vars = cells2vars(grid_vars, disjoint_group)
        model.AddAllDifferent(disjoint_group_vars)


def set_evens_must_see_identical_digit_by_knights_move_constraints(model: PuzzleModel,
                                                                   puzzle: Puzzle):
    """
    Every even number must see at least one identical number via a knight's move (in chess).
    Eg if r5c2 is a 2 then there must be at least one 2 in r3c1, r3c3, r4c4, r6c4, r7c3 and r7c1.

    :param model:
    :param grid_vars:
    :param grid:
    :return:
    """
    prefix = f"evens_must_see_identical_digit_by_knights_move"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.EVENS_MUST_SEE_IDENTICAL_DIGIT_BY_KNIGHTS_MOVE, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for cell in grid.getAllCells():
        cell_var = cell2var(grid_vars, cell)
        knight_moves = grid.getKnigthMoveCells(cell)
        knight_moves_vars = cells2vars(grid_vars, knight_moves)

        is_even = is_even_csp(
            model, cell_var, f"{prefix} - {cell.format_cell()}")
        count_equal_to_cell = count_vars(model, knight_moves_vars, cell_var,
                                         f"{prefix} - identical_digit_count_{cell.format_cell()}")
        model.Add(count_equal_to_cell > 0).OnlyEnforceIf(is_even)


def set_global_indexing_column_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Any number X appearing in the Yth column of a row indicates the column X where the number Y appears in that row.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    prefix = f"global_indexing_column"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.GLOBAL_INDEXING_COLUMN, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    index_ub = grid.nCols - 1

    for cell in grid.getAllCells():
        cell_var = cell2var(grid_vars, cell)

        row_cells = puzzle.grid.getRow(cell.row)
        _row_vars = cells2vars(grid_vars, row_cells)

        index = model.NewIntVar(
            0, index_ub, f"{prefix} - {cell.format_cell()}")
        model.Add(cell_var == index + 1)
        model.AddElement(index, _row_vars, cell.col + 1)


def set_global_indexing_row_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Any number X appearing in the Yth row of a column indicates the row X
    where the number Y appears in that column.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    prefix = f"global_indexing_row"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.GLOBAL_INDEXING_ROW, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    index_ub = grid.nRows - 1

    for cell in grid.getAllCells():
        cell_var = cell2var(grid_vars, cell)

        row_cells = puzzle.grid.getRow(cell.row)
        _row_vars = cells2vars(grid_vars, row_cells)

        index = model.NewIntVar(
            0, index_ub, f"{prefix} - {cell.format_cell()}")
        model.Add(cell_var == index + 1)
        model.AddElement(index, _row_vars, cell.col + 1)


def set_global_indexing_region_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Any number X appearing in the Yth index of a region indicates the index Xth
    where the number Y appears in that region.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    prefix = f"global_indexing_region"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.GLOBAL_INDEXING_REGION, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    regions = grid.getUsedRegions()
    index_ub = len(regions) - 1

    for cell in grid.getAllCells():
        region = cell.region
        if region is None:
            continue

        region_cells = grid.getRegionCells(region)
        pos_in_region = region_cells.index(cell)
        region_vars = cells2vars(grid_vars, region_cells)

        cell_var = cell2var(grid_vars, cell)

        index = model.NewIntVar(
            0, index_ub, f"{prefix} - {cell.format_cell()}")
        model.Add(cell_var == index + 1)
        model.AddElement(index, region_vars, pos_in_region + 1)


def set_global_indexing_disjoint_groups_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    For every digit X in a cell in box Y, there is a digit Y in the same position in box X.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    prefix = f"global_indexing_disjoint_groups"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.GLOBAL_INDEXING_DISJOINT_GROUPS, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    regions = grid.getUsedRegions()
    index_ub = len(regions) - 1

    for cell in grid.getAllCells():
        region = cell.region
        if region is None:
            continue

        disjoint_idx = grid.getDisjointGroupIdx(cell)
        disjoint_group = grid.getCellsInDisjointGroup(disjoint_idx)
        disjoint_group_vars = cells2vars(grid_vars, disjoint_group)

        cell_var = cell2var(grid_vars, cell)

        index = model.NewIntVar(
            0, index_ub, f"{prefix} - {cell.format_cell()}")
        model.Add(cell_var == index + 1)
        model.AddElement(index, disjoint_group_vars, region + 1)


def set_two_by_two_box_global_entropy_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Consider the low digits (1, 2, 3), middle digits (4, 5, 6) and high digits (7, 8, 9) as three different groups. Each 2x2 box in the grid has to contain at least one digit of each group.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    prefix = f"two_by_two_box_global_entropy"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.TWO_BY_TWO_BOX_GLOBAL_ENTROPY, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    entropy_groups = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    for cell in grid.getAllCells():
        box = [cell2 for line in grid.getXByYBox(cell, 2, 2) for cell2 in line]
        if len(box) != 4:
            continue

        box_vars = cells2vars(grid_vars, box)
        at_least_n_in_each_group_csp(
            model, box_vars, entropy_groups, 1, f"{prefix} - {cell.format_cell()} 2x2_box")  # type: ignore


def set_consecutive_entanglement_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A digit must share a row, column, or box with exactly two instances of each digit that it is consecutive with.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    prefix = f"consecutive_entanglement"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.CONSECUTIVE_ENTANGLEMENT, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for cell in puzzle.grid.getAllCells():
        row = grid.getRow(cell.row)
        col = grid.getCol(cell.col)
        box = grid.getRegionCells(cell.region)
        seen = list(set(row + col + box))

        cell_var = cell2var(grid_vars, cell)
        seen_vars = cells2vars(grid_vars, seen)

        adj_var_1 = model.NewIntVar(
            min_digit - 1, max_digit + 1, f"{prefix} - adj_var_1 = {cell.format_cell()} - 1")
        adj_var_2 = model.NewIntVar(
            min_digit - 1, max_digit + 1, f"{prefix} - adj_var_2 = {cell.format_cell()} + 1")
        model.Add(adj_var_1 == cell_var - 1)
        model.Add(adj_var_2 == cell_var + 1)

        count_adjacent_1 = count_vars(
            model, seen_vars, adj_var_1, f"{prefix} - count_{cell.format_cell()}-1")
        count_adjacent_2 = count_vars(
            model, seen_vars, adj_var_2, f"{prefix} - count_{cell.format_cell()}+1")

        b1 = is_member_of(model, puzzle.valid_digits, adj_var_1,
                          f"{prefix} - {cell.format_cell()}-1")
        b2 = is_member_of(model, puzzle.valid_digits, adj_var_2,
                          f"{prefix} - {cell.format_cell()}+1")

        model.Add(count_adjacent_1 == 2).OnlyEnforceIf(b1)
        model.Add(count_adjacent_2 == 2).OnlyEnforceIf(b2)


def set_consecutive_close_neighbours(model: PuzzleModel, puzzle: Puzzle):
    """
    Every number must share a side with at least one other consecutive number.
    For example, 2 must share a side with either a 1 or a 3 (possibly both).

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    prefix = f"consecutive_close_neighbours"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.CONSECUTIVE_CLOSE_NEIGHBORS, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for cell in puzzle.grid.getAllCells():
        adjacent = grid.getOrthogonallyAdjacentCells(cell)
        adjacent_vars = cells2vars(grid_vars, adjacent)
        cell_var = cell2var(grid_vars, cell)

        count1 = count_vars(model, adjacent_vars, cell_var - 1,
                            f"{prefix} - count {cell.format_cell()}-1")
        count2 = count_vars(model, adjacent_vars, cell_var + 1,
                            f"{prefix} - count {cell.format_cell()}+1")

        model.Add(sum([count1, count2]) > 0)


def set_orthogonally_adjacent_cells_are_not_divisors_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    No digit can be orthogonally adjacent with one of its divisors (apart from 1) eg 6 cannot touch a 2 or 3.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    prefix = f"orthogonally_adjacent_cells_are_not_divisors"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.ORTHOGONALLY_ADJACENT_CELLS_ARE_NOT_DIVISORS, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    max_digit = max(puzzle.valid_digits)
    for cell1, cell2 in grid.genAllAdjacentPairs(mode="permutations"):
        cell1_var = cell2var(grid_vars, cell1)
        cell2_var = cell2var(grid_vars, cell2)

        bool_is_1 = model.NewBoolVar(
            f"{prefix} - is_1 = ({cell1.format_cell()}==1) ")
        model.Add(cell1_var == 1).OnlyEnforceIf(bool_is_1)
        model.Add(cell1_var != 1).OnlyEnforceIf(bool_is_1.Not())
        target = model.NewIntVar(
            0, max_digit, f"modulo-target-{cell1.format_cell()}-{cell2.format_cell()}")
        model.AddModuloEquality(target, cell2_var, cell1_var)
        model.Add(target != 0).OnlyEnforceIf(bool_is_1.Not())


def set_at_least_one_ace_rule_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Each region obeys at least one 'Ace' rule within it:
        - either no two orthogonal neighbours can have a difference of 1;
        - OR no two orthogonal neighbours can have a sum of 11.
    """
    prefix = f"at_least_one_ace_rule"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.AT_LEAST_ONE_ACE_RULE, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    def genRegionAdjacencies(region: int | None):
        region_cells = grid.getRegionCells(region)

        for cell1 in region_cells:
            adj = grid.getOrthogonallyAdjacentCells(cell1)
            adj = [cell2 for cell2 in adj if cell2.region == cell1.region]
            adj = [cell2 for cell2 in adj if cell2.row >=
                   cell1.row and cell2.col >= cell1.col]

            for cell2 in adj:
                yield cell1, cell2

    regions = grid.getUsedRegions()
    for region in regions:
        bools_consecutive: list[IntVar] = []
        bools_sum_is_11: list[IntVar] = []

        for cell1, cell2 in genRegionAdjacencies(region):
            cell1_var = cell2var(grid_vars, cell1)
            cell2_var = cell2var(grid_vars, cell2)
            name = f"{prefix} - region_{region}, bool_1 = |{cell1.format_cell()} - {cell2.format_cell()}| == 1"
            is_consecutive = are_consecutive_csp(
                model, cell1_var, cell2_var, name)
            bools_consecutive.append(is_consecutive)

            name = f"{prefix} - region_{region}, bool_2 = {cell1.format_cell()} + {cell2.format_cell()} == 11"
            is_sum_11 = is_sum_csp(model, [cell1_var, cell2_var], 11, name)
            bools_sum_is_11.append(is_sum_11)

        is_rule_1 = model.NewBoolVar(f"{prefix} - region_{region} is_rule_1")
        is_rule_2 = model.NewBoolVar(f"{prefix} - region_{region} is_rule_2")

        # check ace rule 1: no two orthogonal neighbours can have a difference of 1;
        model.AddBoolOr(bools_consecutive).OnlyEnforceIf(is_rule_1.Not())
        model.AddBoolAnd([x.Not() for x in bools_consecutive]
                         ).OnlyEnforceIf(is_rule_1)

        # check ace rule 2: no two orthogonal neighbours can have a sum of 11.
        model.AddBoolOr(bools_sum_is_11).OnlyEnforceIf(is_rule_2.Not())
        model.AddBoolAnd([x.Not() for x in bools_sum_is_11]
                         ).OnlyEnforceIf(is_rule_2)

        # rule 1 or rule 2
        model.AddBoolOr(is_rule_1, is_rule_2)


def set_all_odd_digits_are_orthogonally_connected_constraints(model: PuzzleModel, puzzle: Puzzle):
    prefix = f"all_odd_digits_are_orthogonally_connected"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.ALL_ODD_DIGITS_ARE_ORTHOGONALLY_CONNECTED, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    n_rows = grid.nRows
    n_cols = grid.nCols

    odds_grid = bool_vars_grid_dict_from_puzzle_grid(model, grid, "odds_grid")
    all_cells = puzzle.grid.getAllCells()

    for cell in all_cells:
        cell_var = cell2var(grid_vars, cell)
        odds_grid_var = cell2var(odds_grid, cell)
        is_odd = is_odd_csp(
            model, cell_var, f"{prefix} - {cell.format_cell()}")
        model.Add(odds_grid_var == is_odd)

    # no lone 1s
    for cell in all_cells:
        var = cell2var(odds_grid, cell)
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
        adjacent_vars = cells2vars(odds_grid, adjacent_cells)

        count_name = f"{prefix} - count_odds_{cell.format_cell()}_neighbours"
        odds_count = count_vars(model, adjacent_vars, 1, count_name)
        model.Add(odds_count > 0).OnlyEnforceIf(var)

    count1_total = model.NewIntVar(
        0, n_rows * n_cols, f"{prefix} - count1_total")
    all_vars = cells2vars(odds_grid, all_cells)
    model.Add(sum(all_vars) == count1_total)

    adjacency_dict = build_adjacency_dict(puzzle.grid)
    orthogonally_connected_region_csp(
        model, adjacency_dict, odds_grid, n_rows * n_cols)

    model.grid_vars_dict["odds_grid"] = odds_grid


def set_odd_digits_cannot_gather_in_2x2_square_constraints(model: PuzzleModel, puzzle: Puzzle):
    prefix = f"odd_digits_cannot_gather_in_2x2_square"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.ODD_DIGITS_CANNOT_GATHER_IN_A_2X2_SQUARE, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for cell in puzzle.grid.getAllCells():
        box = [cell2 for line in grid.getXByYBox(cell, 2, 2) for cell2 in line]
        if len(box) != 4:
            continue

        box_vars = cells2vars(grid_vars, box)
        odds_count = modulo_count_csp(
            model, 1, 2, box_vars, f"{prefix} - {cell.format_cell()} - odds_count")
        model.Add(odds_count < 4)


def set_exactly_two_friendly_cells_every_row_col_box_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Friendly cells contain their row, column or region number

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    prefix = f"exactly_two_friendly_cells_every_row_col_box"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.EXACTLY_TWO_FRIENDLY_CELLS_IN_EVERY_ROW_COL_BOX, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    all_cells = puzzle.grid.getAllCells()

    n_rows = grid.nRows
    n_cols = grid.nCols

    friendlies_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"friendly_cells_grid")

    for cell in all_cells:
        r = cell.row + 1
        c = cell.col + 1
        cell_var = cell2var(grid_vars, cell)
        friendly_var = friendlies_grid[(cell.row, cell.col)]
        name = f"{prefix} - {cell.format_cell()}"
        equal_to_row = reif2(model, cell_var == r,
                             cell_var != r, f"{name} - equal_to_row")
        equal_to_col = reif2(model, cell_var == c,
                             cell_var != c, f"{name} - equal_to_col")

        if cell.region is not None:
            region = cell.region + 1
            equal_to_region = reif2(model, cell_var == region,
                                    cell_var != region, f"{name} - equal_to_region")
        else:
            equal_to_region = model.NewBoolVar(f"{name}- equal_to_region")
            model.Add(equal_to_region == 0)

        model.AddBoolOr(equal_to_row, equal_to_col,
                        equal_to_region).OnlyEnforceIf(friendly_var)
        model.AddBoolAnd(equal_to_row.Not(), equal_to_col.Not(), equal_to_region.Not()).OnlyEnforceIf(
            friendly_var.Not())

    for row in range(n_rows):
        row_cells = grid.getRow(row)
        friendly_row_vars = cells2vars(friendlies_grid, row_cells)
        model.Add(sum(friendly_row_vars) == 2)

    for col in range(n_cols):
        col_cells = grid.getCol(col)
        friendly_col_vars = cells2vars(friendlies_grid, col_cells)
        model.Add(sum(friendly_col_vars) == 2)

    for region in grid.getUsedRegions():
        region_cells = grid.getRegionCells(region)
        friendly_region_vars = cells2vars(friendlies_grid, region_cells)
        model.Add(sum(friendly_region_vars) == 2)

    model.grid_vars_dict["friendly_cells_grid"] = friendlies_grid


def set_exactly_one_region_is_magic_square_constraints(model: PuzzleModel, puzzle: Puzzle):
    # prefix = f"exactly_one_region_is_magic_square"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.EXACTLY_ONE_REGION_IS_A_MAGIC_SQUARE, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    n_rows = grid.nRows
    n_cols = grid.nCols

    if n_cols != n_rows or n_cols != 9:
        return

    regions = grid.getUsedRegions()

    bools: list[IntVar] = []
    for region in regions:
        box = grid.getRegionCells(region)
        box = [[box[i * 3 + j] for j in range(3)] for i in range(3)]
        vars_box = [[cell2var(grid_vars, cell) for cell in row] for row in box]
        b = is_magic_square_csp(model, vars_box)
        if b is not None:
            bools.append(b)
    model.AddExactlyOne(bools)


def set_three_in_the_corner_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    There is at least one '3' in one of the grid corner cells.

    :param model:
    :param grid_vars:
    :param puzzle:
    :return:
    """
    prefix = f"three_in_the_corner"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.THREE_IN_THE_CORNER, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    grid = puzzle.grid
    corners = [grid.getCell(0, 0),
               grid.getCell(0, grid.nCols - 1),
               grid.getCell(grid.nRows - 1, grid.nCols - 1),
               grid.getCell(grid.nRows - 1, 0)]

    corners2 = [corner for corner in corners if corner is not None]
    corner_vars = cells2vars(grid_vars, corners2)
    count_threes = count_vars(model, corner_vars, 3,
                              f"{prefix} - count_threes")
    model.Add(count_threes > 0)


def set_single_nadir_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    One cell in the grid is the nadir. Cells must increase in value as they move away from the nadir in every
    straight-line direction (ie vertically, horizontally and diagonally) until they reach the edge of the grid.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    prefix = f"single_nadir"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.SINGLE_NADIR, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    nadir_vars_dict = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix}")
    all_nadir_vars = list(nadir_vars_dict.values())
    model.AddExactlyOne(all_nadir_vars)

    directions = getDirections()
    all_cells = grid.getAllCells()

    for cell in all_cells:
        nadir_var = cell2var(nadir_vars_dict, cell)

        bools: list[IntVar] = []
        for direction in directions:
            segment = [cell] + grid.getCellsInDirection(cell, direction)
            segment_vars = cells2vars(grid_vars, segment)

            name = f"{prefix} - {cell.format_cell()}, {direction.value}"
            is_increasing_strict = is_increasing_strict_csp(
                model, segment_vars, name)
            bools.append(is_increasing_strict)

        model.AddBoolAnd(bools).OnlyEnforceIf(nadir_var)
        model.AddBoolOr([b.Not() for b in bools]
                        ).OnlyEnforceIf(nadir_var.Not())

    model.grid_vars_dict["nadir_bool_grid"] = nadir_vars_dict


def set_dutch_miracle_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Along each positive diagonal (ie from SW to NE): 1) all the digits are different; and 2) adjacent digits (ie those touching at a corner) must have a difference of at least 4.

    Args:
        model (PuzzleModel): 
        grid_vars (dict[): 
        puzzle (Puzzle): 
    """
    prefix = f"dutch_miracle"

    constraint = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.DUTCH_MIRACLE, False)
    if not constraint:
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    value = 4

    for diag in grid.genAllPDiagonals():
        diag_vars = cells2vars(grid_vars, diag)
        model.AddAllDifferent(diag_vars)

        for cell1, cell2 in zip(diag, diag[1:]):
            cell1_var = cell2var(grid_vars, cell1)
            cell2_var = cell2var(grid_vars, cell2)

            name = f"{prefix} - dist = |{cell1.format_cell()}-{cell2.format_cell()}|"
            dist = distance_csp(model, cell1_var, cell2_var, name)
            model.Add(dist >= value)
