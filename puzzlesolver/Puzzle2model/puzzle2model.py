from puzzlesolver.Puzzle.ConstraintEnums import SimpleGlobalConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.BoolConstraints.SimpleBoolConstraints2csp import set_permitted_digits_constraints, set_sudoku_constraints, set_sudoku_constraints_with_unknown_empty_cells_constraints
from puzzlesolver.Puzzle2model.BoolConstraints.boolConstraints2csp import set_bool_constraints
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownEmptyCellsConstraints2csp import get_or_set_unknown_empty_cells_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.constraintTools2csp import set_tool_constraints
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, \
    int_vars_grid_dict_from_puzzle_grid
from puzzlesolver.Puzzle2model.puzzle_model_types import GridVars

MAX_SOLS = 20


def puzzle2model(puzzle: Puzzle) -> PuzzleModel:
    puzzle_model: PuzzleModel = PuzzleModel()
    grid = puzzle.grid
    min_valid = min(puzzle.valid_digits)
    max_valid = max(puzzle.valid_digits)

    unknown_empty_cells = puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.UNKNOWN_EMPTY_CELLS, False)
    sudoku_rules_apply = not puzzle.bool_constraints.get(
        SimpleGlobalConstraintsE.NORMAL_SUDOKU_RULES_DO_NOT_APPLY, False)
    min_cell_value = min_valid if not unknown_empty_cells else min_valid - 1

    all_cells = grid.getAllCells()

    grid_vars_dict = puzzle_model.grid_vars_dict

    cells_grid_vars: GridVars = int_vars_grid_dict_from_puzzle_grid(
        puzzle_model, grid, min_cell_value, max_valid, "")
    grid_vars_dict['cells_grid_vars'] = cells_grid_vars

    if unknown_empty_cells:
        get_or_set_unknown_empty_cells_constraint(puzzle_model, puzzle)

    if sudoku_rules_apply and not unknown_empty_cells:
        set_sudoku_constraints(puzzle_model, puzzle)
    elif sudoku_rules_apply and unknown_empty_cells:
        set_sudoku_constraints_with_unknown_empty_cells_constraints(
            puzzle_model, puzzle)
    elif len(set(puzzle.valid_digits)) != len(puzzle.valid_digits) and not unknown_empty_cells:
        set_permitted_digits_constraints(puzzle_model, puzzle)

    # initial values
    for cell in all_cells:
        if cell.value is not None:
            cell_var = cell2var(cells_grid_vars, cell)
            puzzle_model.Add(cell_var == cell.value)

    set_bool_constraints(puzzle_model, puzzle)
    set_tool_constraints(puzzle_model, puzzle)

    return puzzle_model
