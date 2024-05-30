

from puzzlesolver.Puzzle.ConstraintEnums import DoubleValuedGlobalConstraintsE, SimpleGlobalConstraintsE, ValuedGlobalConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownEmptyCellsConstraints2csp import get_or_set_unknown_empty_cells_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.ValuedGlobalConstraints.utils import genDoubleValuedGlobalConstraint, genValuedGlobalConstraint
from puzzlesolver.Puzzle2model.custom_constraints import are_all_true_csp, distance_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, cell2var
from puzzlesolver.utils.ParsingUtils import parse_int


def set_forbidden_adjacent_sum_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Orthogonally adjacent cells cannot sum to X.

    Args:
        model (PuzzleModel): _description_
        puzzle (Puzzle): _description_
    """
    key = ValuedGlobalConstraintsE.FORBIDDEN_ORTHOGONALLY_ADJACENT_SUM
    prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    all_cells = grid.getAllCells()

    key2 = SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS
    unknown_empty_cells = puzzle.bool_constraints.get(key2, False)

    for _, constraint in enumerate(genValuedGlobalConstraint(puzzle, key)):
        value = parse_int(constraint.value)
        if value is None:
            continue

        for cell1 in all_cells:
            cell1_var = cell2var(grid_vars, cell1)
            adjacent = grid.getOrthogonallyAdjacentCells(cell1)
            filtered = [_cell for _cell in adjacent if _cell.row >
                        cell1.row or _cell.col > cell1.col]

            for cell2 in filtered:
                cell2_var = cell2var(grid_vars, cell2)

                if not unknown_empty_cells:
                    model.Add(cell1_var + cell2_var != value)
                    continue

                filled_cells_grid = get_or_set_unknown_empty_cells_constraint(
                    model, puzzle)
                cell1_filled_var = cell2var(filled_cells_grid, cell1)
                cell2_filled_var = cell2var(filled_cells_grid, cell2)

                name = f"{prefix} - unknown_empty_cells - {cell1.format_cell()}, {cell2.format_cell()} both_filled_var"
                both_filled_var = are_all_true_csp(
                    model, [cell1_filled_var, cell2_filled_var], name)
                model.Add(cell1_var + cell2_var !=
                          value).OnlyEnforceIf(both_filled_var)


def set_forbidden_adjacent_sum_multiple_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The sum of two orthogonally adjacent cells cannot be a multiple of X

    Args:
        model (PuzzleModel): _description_
        puzzle (Puzzle): _description_
    """
    key = ValuedGlobalConstraintsE.FORBIDDEN_ORTHOGONALLY_ADJACENT_SUM_MULTIPLE
    prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    all_cells = grid.getAllCells()

    max_digit = max(puzzle.valid_digits)
    ub = 2*max_digit

    for _, constraint in enumerate(genValuedGlobalConstraint(puzzle, key)):
        value = parse_int(constraint.value)

        if value is None:
            continue

        for cell1 in all_cells:
            cell1_var = cell2var(grid_vars, cell1)
            adjacent = grid.getOrthogonallyAdjacentCells(cell1)
            filtered = [_cell for _cell in adjacent if _cell.row >
                        cell1.row or _cell.col > cell1.col]

            for cell2 in filtered:
                cell2_var = cell2var(grid_vars, cell2)

                target = model.NewIntVar(
                    0, max_digit, f"{prefix} target=({cell1.format_cell()}+{cell2.format_cell()}) % {value}")
                sum_var = model.NewIntVar(
                    0, ub, f"{prefix} - sum = {cell1.format_cell()}+{cell2.format_cell()}")
                model.Add(cell1_var + cell2_var == sum_var)
                model.AddModuloEquality(target, sum_var, 4)
                model.Add(target != 0)


def set_minimum_diagonally_adjacent_difference_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Orthogonally adjacent cells must have a difference of at least X.

    Args:
        model (PuzzleModel): _description_
        puzzle (Puzzle): _description_
    """
    key = ValuedGlobalConstraintsE.MINIMUM_DIAGONALLY_ADJACENT_DIFFERENCE
    prefix = f"{key.value}"
    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    all_cells = grid.getAllCells()

    for _, constraint in enumerate(genValuedGlobalConstraint(puzzle, key)):
        value = parse_int(constraint.value)

        if value is None:
            continue

        for cell1 in all_cells:
            cell1_var = cell2var(grid_vars, cell1)
            adjacent = grid.getDiagonallyAdjacentCells(cell1)
            filtered = [_cell for _cell in adjacent if _cell.row > cell1.row]

            for cell2 in filtered:
                cell2_var = cell2var(grid_vars, cell2)
                name = f"{prefix} - dist=|{cell1.format_cell()}-{cell2.format_cell()}|"
                dist = distance_csp(model, cell1_var, cell2_var, name)
                model.Add(dist >= value)


def set_maximum_orthogonally_adjacent_difference_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Orthogonally adjacent cells must have a difference of at most X.

    Args:
        model (PuzzleModel): _description_
        puzzle (Puzzle): _description_
    """
    key = ValuedGlobalConstraintsE.MAXIMUM_ORTHOGONALLY_ADJACENT_DIFFERENCE
    prefix = f"{key.value}"
    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    all_cells = grid.getAllCells()

    for _, constraint in enumerate(genValuedGlobalConstraint(puzzle, key)):
        value = parse_int(constraint.value)

        if value is None:
            continue

        for cell1 in all_cells:
            cell1_var = cell2var(grid_vars, cell1)
            adjacent = grid.getOrthogonallyAdjacentCells(cell1)
            filtered = [_cell for _cell in adjacent if _cell.row > cell1.row]

            for cell2 in filtered:
                cell2_var = cell2var(grid_vars, cell2)
                name = f"{prefix} - dist=|{cell1.format_cell()}-{cell2.format_cell()}|"
                dist = distance_csp(model, cell1_var, cell2_var, name)
                model.Add(dist <= value)


def set_forbidden_adjacencies_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits x and y cannot be orthogonally adjacent to each other.

    Args:
        model (PuzzleModel): _description_
        puzzle (Puzzle): _description_
    """
    key = DoubleValuedGlobalConstraintsE.FORBIDDEN_ORTHOGONAL_ADJACENCIES
    prefix = f"{key.value}"

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    all_cells = grid.getAllCells()

    for _, constraint in enumerate(genDoubleValuedGlobalConstraint(puzzle, key)):
        value1 = parse_int(constraint.value1)
        value2 = parse_int(constraint.value2)

        if value1 is None or value2 is None:
            continue

        for cell1 in all_cells:
            cell1_var = cell2var(grid_vars, cell1)
            adjacent = grid.getOrthogonallyAdjacentCells(cell1)
            filtered = [_cell for _cell in adjacent if _cell.row >
                        cell1.row or _cell.col > cell1.col]
            cell1_is_val1 = model.NewBoolVar(
                f"{prefix} - {value1}, {value2} not adjacent - {cell1.format_cell()} == {value1}")
            cell1_is_val2 = model.NewBoolVar(
                f"{prefix} - {value1}, {value2} not adjacent - {cell1.format_cell()} == {value2}")
            model.Add(cell1_var == value1).OnlyEnforceIf(cell1_is_val1)
            model.Add(cell1_var != value1).OnlyEnforceIf(cell1_is_val1.Not())
            model.Add(cell1_var == value2).OnlyEnforceIf(cell1_is_val2)
            model.Add(cell1_var != value2).OnlyEnforceIf(cell1_is_val2.Not())

            for cell2 in filtered:
                cell2_var = cell2var(grid_vars, cell2)
                model.Add(cell2_var != value2).OnlyEnforceIf(cell1_is_val1)
                model.Add(cell2_var != value1).OnlyEnforceIf(cell1_is_val2)


def set_valued_global_constraints(model: PuzzleModel, puzzle: Puzzle):
    set_forbidden_adjacent_sum_constraints(model, puzzle)
    set_forbidden_adjacent_sum_multiple_constraints(model, puzzle)

    set_forbidden_adjacencies_constraints(model, puzzle)

    set_minimum_diagonally_adjacent_difference_constraints(model, puzzle)
    set_maximum_orthogonally_adjacent_difference_constraints(model, puzzle)
