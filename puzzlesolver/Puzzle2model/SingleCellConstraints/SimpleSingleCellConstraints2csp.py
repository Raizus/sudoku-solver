
from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.ConstraintEnums import LocalConstraintsModifiersE, SingleCellConstraintsE
from puzzlesolver.Puzzle.Directions import getCardinalDirections
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.SingleCellConstraints.utils import genConstraint, genSingleCellConstraintProperties
from puzzlesolver.Puzzle2model.custom_constraints import are_all_true_csp, is_even_csp, is_farsight_csp, is_odd_csp, is_radar_csp, is_watchtower_csp, modulo_count_csp, sandwich_bools_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, cell2var, cells2vars
from puzzlesolver.utils.ParsingUtils import parse_int
from ortools.sat.python.cp_model import IntVar


def set_orthogonal_sum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """Cell is equal to the sum of all their orthogonally adjacent cells.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for cell, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.ORTHOGONAL_SUM):
        orth_cells = puzzle.grid.getOrthogonallyAdjacentCells(cell)
        orth_vars = cells2vars(grid_vars, orth_cells)

        model.Add(sum(orth_vars) == cell_var)


def set_diagonally_adjacent_sum_constraints(model: PuzzleModel,
                                            puzzle: Puzzle):
    """
    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for cell, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.DIAGONALLY_ADJACENT_SUM):
        diag_adjacent_cells = puzzle.grid.getDiagonallyAdjacentCells(cell)
        diag_adjacent_vars = cells2vars(grid_vars, diag_adjacent_cells)

        model.Add(sum(diag_adjacent_vars) == cell_var)


def set_odd_constraints(model: PuzzleModel, puzzle: Puzzle):
    """ Cell is odd.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    prefix = f"odd"

    for _, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.ODD):
        is_odd = is_odd_csp(model, cell_var, f"{prefix}")
        model.Add(is_odd == 1)


def set_even_constraints(model: PuzzleModel, puzzle: Puzzle):
    """ Cell is even.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    prefix = f"even"

    for _, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.EVEN):
        is_even = is_even_csp(model, cell_var, f"{prefix}")
        model.Add(is_even == 1)


def set_low_digit_constraints(model: PuzzleModel, puzzle: Puzzle):
    """ Cell is low digit {1,2,3,4}

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    for _, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.LOW_DIGIT):
        model.AddAllowedAssignments([cell_var], [(1,), (2,), (3,), (4,)])


def set_high_digit_constraints(model: PuzzleModel, puzzle: Puzzle):
    """ Cell is high digit {6,7,8,9}

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    for _, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.HIGH_DIGIT):
        model.AddAllowedAssignments([cell_var], [(6,), (7,), (8,), (9,)])


def set_friendly_cell_constraints(model: PuzzleModel, puzzle: Puzzle):
    """ Friendly cells contain their row, column or box number.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    for cell, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.FRIENDLY_CELL):
        row = cell.row + 1
        col = cell.col + 1
        if cell.region is not None:
            region = cell.region + 1
            model.AddAllowedAssignments(
                [cell_var], [(row,), (col,), (region,)])
        else:
            model.AddAllowedAssignments([cell_var], [(row,), (col,)])


def set_odd_minesweeper_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A digit in a cell with a circle is the same as the number of the surrounding cells (not counting the cell itself) with odd numbers. (So a total of 8 possible surrounding cells).

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    prefix = "odd_minesweeper"
    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.ODD_MINESWEEPER)):
        neighbours = puzzle.grid.getNeighbourCells(cell)
        neighbours_vars = cells2vars(grid_vars, neighbours)
        odd_count = modulo_count_csp(
            model, 1, 2, neighbours_vars, f"{prefix}_{i}")
        model.Add(odd_count == cell_var)


def set_maximum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """A number in a gray cell pointing outwards must be greater than all the orthogonally adjacent cells (if they're not maximum cells)

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    max_cells = [cell for cell, _, _ in genSingleCellConstraintProperties(
        model, puzzle, SingleCellConstraintsE.MAXIMUM)]

    for cell, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.MAXIMUM):
        adjacent = puzzle.grid.getOrthogonallyAdjacentCells(cell)
        adjacent = [cell2 for cell2 in adjacent if cell2 not in max_cells]
        for cell2 in adjacent:
            adjacent_var = cell2var(grid_vars, cell2)
            model.Add(cell_var > adjacent_var)


def set_minimum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A number in a gray cell pointing inwards must be lesser than all the orthogonally adjacent cells
    (if they're not minimum cells)

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    min_cells = [cell for cell, _, _ in genSingleCellConstraintProperties(
        model, puzzle, SingleCellConstraintsE.MINIMUM)]

    for cell, cell_var, _ in genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.MINIMUM):
        adjacent = puzzle.grid.getOrthogonallyAdjacentCells(cell)
        adjacent = [_cell for _cell in adjacent if _cell not in min_cells]
        for _cell in adjacent:
            adjacent_var = cell2var(grid_vars, _cell)
            model.Add(cell_var < adjacent_var)


def set_indexing_column_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers in red cells are indexing columns: Any number X appearing in the Yth column of a row indicates the
    column X where the number Y appears in that row.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    prefix = "indexing_column"
    max_col = puzzle.grid.nCols

    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.INDEXING_COLUMN)):
        row_cells = puzzle.grid.getRow(cell.row)
        row_vars = cells2vars(grid_vars, row_cells)

        index = model.NewIntVar(
            0, max_col - 1, f"{prefix}_{i} - {cell.format_cell()}")
        model.Add(cell_var == index + 1)
        model.AddElement(index, row_vars, cell.col + 1)

    all_indexing_column_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_INDEXING_COLUMN_GIVEN, False)
    prefix = f"all_indexing_column_given"

    all_indexing_column_in_used_columns_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_INDEXING_COLUMN_IN_USED_COLUMNS_GIVEN, False)
    prefix = f"all_indexing_column_in_used_columns_given"

    if all_indexing_column_given or all_indexing_column_in_used_columns_given:
        index_ub = puzzle.grid.nCols - 1
        min_digit = min(puzzle.valid_digits)
        max_digit = max(puzzle.valid_digits)
        cells = [cell for cell, _, _ in genSingleCellConstraintProperties(
            model, puzzle, SingleCellConstraintsE.INDEXING_COLUMN)]
        used_columns = set(cell.col for cell in cells)

        for cell in puzzle.grid.getAllCells():
            if cell in cells:
                continue

            if all_indexing_column_in_used_columns_given and cell.col not in used_columns:
                continue

            cell_var = cell2var(grid_vars, cell)
            row_cells = puzzle.grid.getRow(cell.row)
            row_vars = cells2vars(grid_vars, row_cells)

            index = model.NewIntVar(
                0, index_ub, f"{prefix} - {cell.format_cell()}")
            model.Add(cell_var == index + 1)
            target = model.NewIntVar(
                min_digit, max_digit, f"{prefix} - target - {cell.format_cell()}")
            model.AddElement(index, row_vars, target)
            model.Add(target != cell.col + 1)


def set_indexing_row_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers in blue cells are indexing rows: Any number X appearing in the Yth row of a column indicates the row X
    where the number Y appears in that column.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    prefix = "indexing_row"
    max_row = puzzle.grid.nRows
    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.INDEXING_ROW)):
        col_cells = puzzle.grid.getCol(cell.col)
        col_vars = cells2vars(grid_vars, col_cells)

        index = model.NewIntVar(
            0, max_row - 1, f"{prefix}_{i} - {cell.format_cell()}")
        model.Add(cell_var == index + 1)
        model.AddElement(index, col_vars, cell.row + 1)

    all_indexing_row_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_INDEXING_ROW_GIVEN, False)
    prefix = f"all_indexing_row_given"

    if all_indexing_row_given:
        index_ub = puzzle.grid.nRows - 1
        min_digit = min(puzzle.valid_digits)
        max_digit = max(puzzle.valid_digits)
        cells = [cell for cell, _, _ in genSingleCellConstraintProperties(
            model, puzzle, SingleCellConstraintsE.INDEXING_ROW)]

        for cell in puzzle.grid.getAllCells():
            if cell in cells:
                continue

            cell_var = cell2var(grid_vars, cell)
            col_cells = puzzle.grid.getCol(cell.col)
            col_vars = cells2vars(grid_vars, col_cells)

            index = model.NewIntVar(
                0, index_ub, f"{prefix} - {cell.format_cell()}")
            model.Add(cell_var == index + 1)
            target = model.NewIntVar(
                min_digit, max_digit, f"{prefix} - target - {cell.format_cell()}")
            model.AddElement(index, col_vars, target)
            model.Add(target != cell.row + 1)


def set_radar_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Radars are cells that have a value indicating the distance to the closest X (default 9) on their row or column.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    prefix = f"radar"
    targets: set[int | IntVar] = set()
    for i, (cell, cell_var, value) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.RADAR)):

        value2 = value if (value is not None and len(value)) else 9
        target_var = model.get_or_set_shared_var(value2, min_digit, max_digit,
                                                 f"{prefix}_{i}: target")

        targets.add(target_var)

        row = puzzle.grid.getRow(cell.row)
        row_vars = cells2vars(grid_vars, row)
        col = puzzle.grid.getCol(cell.col)
        col_vars = cells2vars(grid_vars, col)

        is_radar = is_radar_csp(model, cell_var, row_vars,
                                col_vars, target_var, f"{prefix}_{i}")
        model.Add(is_radar == 1)

    # all radars given
    all_radars_given = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_RADARS_GIVEN, False)
    if all_radars_given:
        radar_cells = [cell for cell, _, _ in genSingleCellConstraintProperties(
            model, puzzle, SingleCellConstraintsE.RADAR)]

        for cell in puzzle.grid.getAllCells():
            if cell in radar_cells:
                continue

            cell_var = cell2var(grid_vars, cell)

            row = puzzle.grid.getRow(cell.row)
            row_vars = cells2vars(grid_vars, row)
            col = puzzle.grid.getCol(cell.col)
            col_vars = cells2vars(grid_vars, col)

            for target in targets:
                is_radar = is_radar_csp(model, cell_var, row_vars, col_vars, target,
                                        f"{prefix} - all_radars_given - {cell.format_cell()}")
                model.Add(is_radar == 0)


def set_watchtower_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Small blue circles represent Watchtowers of height X, where X is the digit in that cell. Each watchtower
    must see exactly X cells (including itself) in its row and column combined. Watchtowers cannot see digits larger
    than their own height, nor past them.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    prefix = f"watchtower"
    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.WATCHTOWER)):
        row = puzzle.grid.getRow(cell.row)
        row_vars = cells2vars(grid_vars, row)
        col = puzzle.grid.getCol(cell.col)
        col_vars = cells2vars(grid_vars, col)

        is_watchtower = is_watchtower_csp(
            model, cell_var, row_vars, col_vars, f"{prefix}_{i}")
        model.Add(is_watchtower == 1)


def set_not_watchtower_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Small blue squares represent cells that are NOT Watchtowers, i.e., with a value different from X.
    A watchtower of height X, where X is the digit in that cell, must see exactly X cells (including itself)
    in its row and column combined. Watchtowers cannot see digits larger than their own height, nor past them.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    prefix = f"not_watchtower"

    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.NOT_WATCHTOWER)):
        row = puzzle.grid.getRow(cell.row)
        row_vars = cells2vars(grid_vars, row)
        col = puzzle.grid.getCol(cell.col)
        col_vars = cells2vars(grid_vars, col)

        is_watchtower = is_watchtower_csp(
            model, cell_var, row_vars, col_vars, f"{prefix}_{i}")
        model.Add(is_watchtower == 0)


def set_adjacent_cells_in_diff_directions_have_opposite_parity_constraints(model: PuzzleModel,
                                                                           puzzle: Puzzle):
    """
    For each cell marked with a green circle, the following is true: Either its two horizontally adjacent cells
    are both even and its two vertically adjacent cells both odd; or its two horizontally adjacent cells are both odd
    and its two vertically adjacent cells are both even.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    prefix = f"adjacent_cells_in_different_directions_have_opposite_parity"
    for i, (cell, _, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.ADJACENT_CELLS_IN_DIFFERENT_DIRECTIONS_HAVE_OPPOSITE_PARITY)):
        vertical_adjacent_cells = grid.getVerticallyAdjacentCells(cell)
        vertical_adjacent_cells_vars = cells2vars(
            grid_vars, vertical_adjacent_cells)
        horizontal_adjacent_cells = grid.getHorizontallyAdjacentCells(cell)
        horizontal_adjacent_cells_vars = cells2vars(
            grid_vars, horizontal_adjacent_cells)

        horiz_targets = [model.NewIntVar(0, 1, f"{prefix}_{i} - mod_target_{_cell.format_cell()}")
                         for _cell in horizontal_adjacent_cells]
        vert_targets = [model.NewIntVar(0, 1, f"{prefix}_{i} - mod_target_{_cell.format_cell()}")
                        for _cell in vertical_adjacent_cells]

        for (_cell_var, target_var) in zip(vertical_adjacent_cells_vars, vert_targets):
            model.AddModuloEquality(target_var, _cell_var, 2)

        for (_cell_var, target_var) in zip(horizontal_adjacent_cells_vars, horiz_targets):
            model.AddModuloEquality(target_var, _cell_var, 2)

        model.Add(horiz_targets[0] == horiz_targets[1])
        model.Add(vert_targets[0] == vert_targets[1])
        model.Add(vert_targets[0] != horiz_targets[0])


def set_snowball_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A blue circle in the grid is a Snowball. Snowballs roll in straight lines—either horizontally or
    vertically—through a set of orthogonally connected cells. The total length (in cells) of a Snowball's path is
    given by the number in the top left corner of its starting cell. The digits along a Snowball's path behave
    as follows: after the first two digits, each digit is the sum of the two preceding digits.
    Snowballs may cross paths, and therefore may share one or more cells with other Snowballs.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    prefix = f"snowball"
    directions = getCardinalDirections()
    for i, constraint in enumerate(genConstraint(puzzle, SingleCellConstraintsE.SNOWBALL)):
        cell_coord = constraint.cell
        cell = puzzle.grid.getCellFromCoords(cell_coord)
        if cell is None:
            continue

        if constraint.value is None:
            continue

        length = parse_int(constraint.value)
        if length is None or length <= 2:
            continue

        segment_dict: dict[str, list[Cell]] = dict()
        for direction in directions:
            segment = [cell] + grid.getCellsInDirection(cell, direction)
            segment_dict[direction.value] = segment

        bools: list[IntVar] = []
        for key, segment in segment_dict.items():
            bool_is_snowball = model.NewBoolVar(
                f"{prefix}_{i} - bool_is_snowball, {cell.format_cell()}-{key}")
            bools.append(bool_is_snowball)

            if len(segment) < length:
                model.Add(bool_is_snowball == 0)
                continue

            segment_vars = cells2vars(grid_vars, segment)
            for j, var in enumerate(segment_vars[2:length], 2):
                model.Add(
                    var == segment_vars[j - 1] + segment_vars[j - 2]).OnlyEnforceIf(bool_is_snowball)

        model.AddExactlyOne(bools)


def set_count_same_parity_neighbour_cells_constraints(model: PuzzleModel,
                                                      puzzle: Puzzle):
    """
    Cells marked with a circle show the number of digits with the same parity as that circled digit in that cell's
    3x3 neighbourhood (including the digit in the cell itself).
    Eg if r1c1 is a 1, all 3 cells surrounding it must be even.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    prefix = f"count_same_parity_neighbour_cells"
    for i, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.COUNT_SAME_PARITY_NEIGHBOUR_CELLS)):
        neighbour_cells = grid.getNeighbourCells(cell)
        neighbour_cells.append(cell)
        neighbour_cells_vars = cells2vars(grid_vars, neighbour_cells)

        is_odd = model.NewBoolVar(f"{prefix}_{i} - is_odd")
        model.AddModuloEquality(is_odd, cell_var, 2)
        name = f"{prefix}_{i} - odd_or_even_count"
        odd_or_even_count = modulo_count_csp(
            model, is_odd, 2, neighbour_cells_vars, name)
        model.Add(cell_var == odd_or_even_count)


def set_sandwich_row_col_count_constraints(model: PuzzleModel,
                                           puzzle: Puzzle):
    """
    A number in a circled cell indicates the total number of cells sandwiched between the 1's and the 9's in the row and column containing the circle. If a cell is simultaneously in a row sandwich and column sandwich, it is only counted once.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    prefix = f"sandwich_row_col_count"
    for _, (cell, cell_var, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.SANDWICH_ROW_COL_COUNT)):
        row_cells = grid.getRow(cell.row)
        col_cells = grid.getCol(cell.col)
        row_vars = cells2vars(grid_vars, row_cells)
        col_vars = cells2vars(grid_vars, col_cells)
        row_idx = row_vars.index(cell_var)
        col_idx = col_vars.index(cell_var)

        name = f"{prefix} - {cell.format_cell()}"
        row_sandwich_bools = sandwich_bools_csp(
            model, row_vars, min_digit, max_digit, f"{name} - row")
        col_sandwich_bools = sandwich_bools_csp(
            model, col_vars, min_digit, max_digit, f"{name} - col")

        cell_row_sandwich_var = row_sandwich_bools[row_idx]
        cell_col_sandwich_var = col_sandwich_bools[col_idx]
        interset_vars = [cell_row_sandwich_var, cell_col_sandwich_var]

        name = f"{prefix} - {cell.format_cell()} - row_and_col_sandwich"
        both_var = are_all_true_csp(model, interset_vars, name)

        model.Add(sum(row_sandwich_bools) +
                  sum(col_sandwich_bools) - both_var == cell_var)


def set_farsight_constraints(model: PuzzleModel,
                             puzzle: Puzzle):
    """
    A digit in a cage sees one or more consecutive digits exactly N cells away from itself in the same row or column, where N = the digit in the caged cell. For example, a caged 4 must see a 3 or 5 exactly 4 cells away from itself.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    prefix = f"farsight"
    directions = getCardinalDirections()
    for i, (cell, _, _) in enumerate(genSingleCellConstraintProperties(model, puzzle, SingleCellConstraintsE.FARSIGHT)):
        segment_dict: dict[str, list[Cell]] = dict()
        for direction in directions:
            segment = [cell] + grid.getCellsInDirection(cell, direction)
            segment_dict[direction.value] = segment

        bools: list[IntVar] = []
        for key, segment in segment_dict.items():
            segment_vars = cells2vars(grid_vars, segment)
            is_farsight = is_farsight_csp(model, segment_vars[0], segment_vars,
                                          f"{prefix}_{i} - {cell.format_cell()} - {key}")
            bools.append(is_farsight)

        model.Add(sum(bools) >= 1)
