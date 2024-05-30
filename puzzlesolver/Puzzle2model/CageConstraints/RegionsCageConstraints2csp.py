from puzzlesolver.Puzzle.ConstraintEnums import CageConstraintsE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.CageConstraints.utils import genCageConstraintProperties
from puzzlesolver.Puzzle2model.OtherConstraints.YinYangConstraints2csp import get_or_set_yin_yang_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import masked_sum_csp, is_even_csp, multiplication_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cells2vars
from puzzlesolver.Puzzle2model.BoolConstraints.puzzle_values_modifiers import get_or_set_cold_cells_constraint, get_or_set_decrement_fountain_constraint, get_or_set_doublers_grid, get_or_set_hot_cells_constraint, get_or_set_multipliers_constraint, get_or_set_negators_grid


def set_doublers_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    A digit in a doubler cell counts for twice its value for the purposes of all cage sums. Digits may not repeat in
    cages, though values might.
    (e.g. a cage may not contain a doubled 2 and a regular 2 but may contain a doubled 2 and a regular 4).

    The numbers in the cage must sum to the given total in the top left (if one exists).

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.DOUBLERS_KILLER_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    doublers_bool_grid, _ = get_or_set_doublers_grid(model, puzzle)

    lb = min(puzzle.valid_digits)
    ub = max(puzzle.valid_digits)

    for i, (cells, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cells)
        model.AddAllDifferent(cells_vars)

        sum_var = model.get_or_set_shared_var(
            value, lb, 2*sum(puzzle.valid_digits), f"{prefix}_{i}: sum")

        # multipliers = vars_from_cells(doublers_grid, cells)
        doublers_bools = cells2vars(doublers_bool_grid, cells)

        # scalar product
        n = len(cells_vars)
        t = [model.NewIntVar(
            lb, 2 * ub, f"{prefix}_{i}: t_{j}") for j in range(n)]
        for j in range(n):
            model.Add(t[j] == cells_vars[j]).OnlyEnforceIf(
                doublers_bools[j].Not())
            model.Add(t[j] == 2 * cells_vars[j]
                      ).OnlyEnforceIf(doublers_bools[j])

        model.Add(sum(t) == sum_var)


def set_hot_cold_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits in cages do not include repeat digits, and must sum to the given total in the top left (if one exists).
    For cages values:
        - Hot cells increase the value of the contained digit by 1;
        - Cold cells decrease the value of the contained digit by 1.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.HOT_COLD_KILLER_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    cold_cells_grid = get_or_set_cold_cells_constraint(model, puzzle)
    hot_cells_grid = get_or_set_hot_cells_constraint(model, puzzle)

    min_digit = min(puzzle.valid_digits)

    for i, (cells, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        model.AddAllDifferent(cells_vars)
        cage_size = len(cells)

        lb = min_digit - cage_size
        ub = sum(puzzle.valid_digits)+cage_size

        sum_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix} {i} - sum")

        hot_vars = cells2vars(hot_cells_grid, cells)
        cold_vars = cells2vars(cold_cells_grid, cells)
        model.Add(sum(cells_vars) + sum(hot_vars) + sum(cold_vars) == sum_var)


def set_negators_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits in cages do not include repeat digits, and must sum to the given total in the top left (if one exists).
    A digit in a negator cell must be subtracted rather than added to achieve the given cage total.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.NEGATORS_KILLER_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    negators_bool_grid, _ = get_or_set_negators_grid(model, puzzle)

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    min_val = min(-min_digit, min_digit, -max_digit, max_digit)
    max_val = max(-min_digit, min_digit, -max_digit, max_digit)

    for i, (cells, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cells)
        model.AddAllDifferent(cells_vars)

        lb, ub = n*min_val, n*max_val

        sum_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix}_{i}: sum")

        # multipliers = vars_from_cells(doublers_grid, cells)
        negators_bools = cells2vars(negators_bool_grid, cells)

        # scalar product
        n = len(cells_vars)
        t = [model.NewIntVar(
            min_val, max_val, f"{prefix}_{i}: t_{j}") for j in range(n)]
        for j in range(n):
            model.Add(t[j] == cells_vars[j]).OnlyEnforceIf(
                negators_bools[j].Not())
            model.Add(t[j] == -1 * cells_vars[j]
                      ).OnlyEnforceIf(negators_bools[j])

        model.Add(sum(t) == sum_var)


def set_yin_yang_antithesis_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits in cages cannot repeat and must sum to the small clue in the top left corner of the cage.
    However, shaded cells are treated as negative. In other words, the cage total is the sum of unshaded cells
    minus the sum of shaded cells.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.YIN_YANG_ANTITHESIS_KILLER_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # grid_vars = model.grid_vars_dict['cells_grid_vars']
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    # min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for i, (cells, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cells)
        model.AddAllDifferent(cells_vars)

        lb = -sum(puzzle.valid_digits)
        ub = sum(puzzle.valid_digits)

        sum_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix}_{i}: sum")

        yin_yang_cage_vars = cells2vars(yin_yang_grid, cells)

        # scalar product
        t = [model.NewIntVar(-max_digit, max_digit, f"{prefix}_{i} - t_{j}")
             for j in range(n)]
        for j in range(n):
            model.Add(t[j] == cells_vars[j]).OnlyEnforceIf(
                yin_yang_cage_vars[j].Not())
            model.Add(t[j] == -cells_vars[j]
                      ).OnlyEnforceIf(yin_yang_cage_vars[j])
        model.Add(sum(t) == sum_var)


def set_yin_yang_breakeven_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits in a cage cannot repeat and must sum to the small clue in the top left corner of the cage.
    In cages, all shaded cells must contain even digits, and all unshaded cells must contain odd digits.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    key = CageConstraintsE.YIN_YANG_BREAKEVEN_KILLER_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # grid_vars = model.grid_vars_dict['cells_grid_vars']
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    lb = min(puzzle.valid_digits)
    ub = sum(puzzle.valid_digits)

    for i, (cells, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        model.AddAllDifferent(cells_vars)

        sum_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix}_{i}: sum")

        yin_yang_cage_vars = cells2vars(yin_yang_grid, cells)
        for j, cell_var in enumerate(cells_vars):
            is_even = is_even_csp(model, cell_var,
                                  f"{prefix}_{i} - {cells[j].format_cell()}_is_even")
            model.Add(yin_yang_cage_vars[j] == 1).OnlyEnforceIf(is_even)
            model.Add(yin_yang_cage_vars[j] == 0).OnlyEnforceIf(is_even.Not())

        model.Add(sum(cells_vars) == sum_var)


def set_multipliers_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Cage totals are shown in the upper left corner of the cage. If a multiplier appears in a cage, then it multiplies
    the sum of the other digits in the cage to produce the cage total. For instance, if a cage contains 3, 4, 5, 6 and
    3 is the multiplier, the cage total would be 3*(4+5+6)=45. A multiplier which is not in a cage has no effect.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.MULTIPLIERS_KILLER_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # grid = puzzle.grid
    # all_cells = puzzle.grid.getAllCells()
    # grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    multipliers_bools_grid = get_or_set_multipliers_constraint(model, puzzle)

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)
    valid_digits = puzzle.valid_digits

    for i, (cells, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cells)
        model.AddAllDifferent(cells_vars)

        lb = min(sum(valid_digits[:n]), sum(valid_digits[:n-1])*min_digit)
        ub = max(sum(valid_digits[-n:]), sum(valid_digits[-(n-1):])*max_digit)

        value_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix} {i}: sum")

        sum_part_var = model.NewIntVar(
            0, sum(puzzle.valid_digits), f"{prefix} - cage_{i} - sum_part_var")
        is_multiplier_bools = cells2vars(multipliers_bools_grid, cells)

        # scalar product
        mask_bools = [b.Not() for b in is_multiplier_bools]
        masked_sum_var = masked_sum_csp(model, cells_vars, mask_bools,  # type: ignore
                                        f"{prefix}_{i} - sum_part")

        model.Add(sum_part_var == masked_sum_var)

        # multiplier_part
        t2 = [model.NewIntVar(
            min(min_digit, 1), max_digit, f"t{j}") for j in range(n)]
        for j in range(n):
            model.Add(t2[j] == cells_vars[j]).OnlyEnforceIf(
                is_multiplier_bools[j])
            model.Add(t2[j] == 1).OnlyEnforceIf(
                is_multiplier_bools[j].Not())

        multiplier = multiplication_csp(
            model, t2, f"{prefix} - cage_{i}, multiplier")

        model.AddMultiplicationEquality(
            value_var, [sum_part_var, multiplier])


def set_fountain_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits do not repeat in cages, but values may. Each cage shows the sum of the VALUES of the cells in it,
    computed after being splashed by fountains.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.FOUNTAIN_KILLER_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    get_or_set_decrement_fountain_constraint(model, puzzle)
    after_decrement_fountain_values_grid = model.grid_vars_dict[
        'after_decrement_fountain_values_grid']

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    min_val = min_digit - 8*1
    max_val = max_digit

    for i, (cells, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cells)
        model.AddAllDifferent(cells_vars)

        lb, ub = n*min_val, n*max_val

        sum_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix}_{i}: sum")

        value_vars = cells2vars(after_decrement_fountain_values_grid, cells)
        model.Add(sum_var == sum(value_vars))
