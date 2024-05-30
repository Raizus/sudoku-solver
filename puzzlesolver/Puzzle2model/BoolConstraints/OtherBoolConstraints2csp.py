

from puzzlesolver.Puzzle.ConstraintEnums import GlobalRegionConstraintsE, SimpleGlobalConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OtherConstraints.NurimisakiConstraints2csp import get_or_set_nurimisaki_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownEmptyCellsConstraints2csp import get_or_set_unknown_empty_cells_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownRegionsConstraints2csp import get_or_set_unknown_regions_grid
from puzzlesolver.Puzzle2model.OtherConstraints.YinYangConstraints2csp import get_or_set_yin_yang_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import are_all_true_csp, masked_count_vars, count_vars, is_whispers_csp, member_of
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, cells2vars, is_magic_column_constraint
from puzzlesolver.Puzzle2model.puzzle_model_types import GridVars
from ortools.sat.python.cp_model import IntVar


def set_digits_dont_repeat_on_columns_constraints(model: PuzzleModel, puzzle: Puzzle):
    key1 = SimpleGlobalConstraintsE.DIGITS_DO_NOT_REPEAT_ON_COLUMNS
    no_repeats_on_columns = puzzle.bool_constraints.get(key1, False)
    prefix = f"{key1.value}"

    if not no_repeats_on_columns:
        return

    key2 = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key2, False)

    grid_vars_dict = model.grid_vars_dict
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid
    valid_digits = puzzle.valid_digits

    if not unknown_empty_cells:
        for j in range(0, grid.nCols):
            col_cells = grid.getCol(j)
            col_vars = cells2vars(cells_grid_vars, col_cells)
            model.AddAllDifferent(col_vars)
    else:
        filled_cells_grid = get_or_set_unknown_empty_cells_constraint(
            model, puzzle)
        # AllDifferent on cols.
        for j in range(0, grid.nCols):
            col_cells = grid.getCol(j)
            col_vars = cells2vars(cells_grid_vars, col_cells)
            filled_cells_bool_col = cells2vars(filled_cells_grid, col_cells)
            for digit in valid_digits:
                name = f"{prefix} - col={j}, digit={digit} count"
                count_var = masked_count_vars(
                    model, col_vars, filled_cells_bool_col, digit, name)
                model.AddAllowedAssignments([count_var], [(0,), (1,)])


def set_digits_dont_repeat_on_any_diagonal_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = SimpleGlobalConstraintsE.DIGITS_DO_NOT_REPEAT_ON_ANY_DIAGONALS
    no_repeats_on_diags = puzzle.bool_constraints.get(key, False)
    if not no_repeats_on_diags:
        return

    key2 = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key2, False)
    cells_grid_vars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid
    valid_digits = puzzle.valid_digits
    prefix = f"{key.value}"

    if not unknown_empty_cells:
        # positive diagonals
        for diag_cells in grid.genAllPDiagonals():
            diag_vars = cells2vars(cells_grid_vars, diag_cells)
            model.AddAllDifferent(diag_vars)

        # negative diagonals
        for diag_cells in grid.genAllNDiagonals():
            diag_vars = cells2vars(cells_grid_vars, diag_cells)
            model.AddAllDifferent(diag_vars)

    else:
        filled_cells_grid = get_or_set_unknown_empty_cells_constraint(
            model, puzzle)

        # positive diagonal
        for i, diag_cells in enumerate(grid.genAllPDiagonals()):
            diag_vars = cells2vars(cells_grid_vars, diag_cells)
            filled_cells_bool_diag = cells2vars(filled_cells_grid, diag_cells)
            for digit in valid_digits:
                name = f"{prefix} - positive_diagonal {i} - digit={digit} count"
                count_var = masked_count_vars(
                    model, diag_vars, filled_cells_bool_diag, digit, name)
                model.AddAllowedAssignments([count_var], [(0,), (1,)])

        # negative diagonals
        for i, diag_cells in enumerate(grid.genAllNDiagonals()):
            diag_vars = cells2vars(cells_grid_vars, diag_cells)
            filled_cells_bool_diag = cells2vars(filled_cells_grid, diag_cells)
            for digit in valid_digits:
                name = f"{prefix} - negative_diagonal {i} - digit={digit} count"
                count_var = masked_count_vars(
                    model, diag_vars, filled_cells_bool_diag, digit, name)
                model.AddAllowedAssignments([count_var], [(0,), (1,)])


def set_one_of_each_digit_on_columns_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = SimpleGlobalConstraintsE.ONE_OF_EACH_DIGIT_ON_COLUMNS
    one_of_each_on_columns = puzzle.bool_constraints.get(key, False)
    if not one_of_each_on_columns:
        return

    key2 = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key2, False)

    cells_grid_vars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid
    valid_digits = puzzle.valid_digits
    prefix = f"{key.value}"

    if not unknown_empty_cells:
        for j in range(0, grid.nCols):
            col_cells = grid.getCol(j)
            col_vars = cells2vars(cells_grid_vars, col_cells)
            for digit in valid_digits:
                count_digit = count_vars(
                    model, col_vars, digit, f"{prefix} - col={j}, digit={digit} count")
                model.Add(count_digit == 1)
    else:
        prefix2 = f"{prefix} - {key2.value}"
        filled_cells_grid = get_or_set_unknown_empty_cells_constraint(
            model, puzzle)
        for j in range(0, grid.nCols):
            col_cells = grid.getCol(j)
            col_vars = cells2vars(cells_grid_vars, col_cells)
            filled_cells_bool_col = cells2vars(filled_cells_grid, col_cells)
            for digit in valid_digits:
                name = f"{prefix2} - col={j}, digit={digit} count"
                count_var = masked_count_vars(
                    model, col_vars, filled_cells_bool_col, digit, name)
                model.Add(count_var == 1)


def set_cells_along_nurimisaki_path_have_a_diff_of_at_least_5_constraints(model: PuzzleModel,
                                                                          puzzle: Puzzle):

    key = GlobalRegionConstraintsE.CELLS_ALONG_NURIMISAKI_PATH_HAVE_A_DIFFERENCE_OF_AT_LEAST_5
    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    prefix = f"cells_along_nurimisaki_path_have_a_diff_of_at_least_5"
    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    nurimisaki_grid = get_or_set_nurimisaki_constraint(model, puzzle)

    for cell1, cell2 in grid.genAllAdjacentPairs():
        cell1_var = cell2var(grid_vars, cell1)
        cell2_var = cell2var(grid_vars, cell2)
        nurimisaki_var1 = cell2var(nurimisaki_grid, cell1)
        nurimisaki_var2 = cell2var(nurimisaki_grid, cell2)

        is_german_whispers = is_whispers_csp(model, [cell1_var, cell2_var], 5)

        name = f"{prefix} - both_unshaded_bool - {cell1.format_cell()}, {cell2.format_cell()}"
        both_unshaded_bool = are_all_true_csp(
            model, [nurimisaki_var1, nurimisaki_var2], name)

        model.Add(is_german_whispers == 1).OnlyEnforceIf(both_unshaded_bool)


def set_one_column_is_magic(model: PuzzleModel, puzzle: Puzzle):
    key = SimpleGlobalConstraintsE.ONE_COLUMN_IS_MAGIC
    on_column_is_magic = puzzle.bool_constraints.get(key, False)
    if not on_column_is_magic:
        return

    grid = puzzle.grid
    # prefix = f"{key.value}"
    bools: list[IntVar] = []
    for col in range(grid.nCols):
        is_magic_column_bool = is_magic_column_constraint(
            model, puzzle, col)
        bools.append(is_magic_column_bool)
    model.AddExactlyOne(bools)


def set_yin_yang_unknown_regions_fully_shaded_or_fully_unshaded(model: PuzzleModel,
                                                                puzzle: Puzzle):
    """
    Each unknown region is either fully shaded or fully unshaded (with yin yang shading)

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = GlobalRegionConstraintsE.YIN_YANG_UNKNOWN_REGIONS_FULLY_SHADED_OR_FULLY_UNSHADED
    constraint = puzzle.bool_constraints.get(key, False)
    if not constraint:
        return

    prefix = f"{key.value}"

    grid = puzzle.grid
    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)
    yin_yang_negated_grid = model.grid_vars_dict["yin_yang_negated_grid"]

    all_cells = grid.getAllCells()
    regions_vars = cells2vars(regions_grid, all_cells)
    yin_yang_vars = cells2vars(yin_yang_grid, all_cells)
    yin_yang_negated_vars = cells2vars(yin_yang_negated_grid, all_cells)

    num_regions = 9
    region_size = 9

    for region in range(num_regions):
        name = f"{prefix} - region={region} - shaded count"
        count_var = masked_count_vars(
            model, regions_vars, yin_yang_vars, region, name)
        model.AddAllowedAssignments([count_var], [(0,), (region_size,)])

        name = f"{prefix} - region={region} - unshaded count"
        count_var2 = masked_count_vars(
            model, regions_vars, yin_yang_negated_vars, region, name)
        model.AddAllowedAssignments([count_var2], [(0,), (region_size,)])

        member_of(model, [count_var, count_var2],
                  region_size, f"{prefix} - region_{region}")
