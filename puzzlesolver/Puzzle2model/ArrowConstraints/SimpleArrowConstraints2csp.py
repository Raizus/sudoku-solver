

from puzzlesolver.Puzzle.ConstraintEnums import ArrowConstraintsE
from puzzlesolver.Puzzle.Directions import RCToDirectionDict
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.ArrowConstraints.utils import genArrowConstraintProperties
from puzzlesolver.Puzzle2model.OtherConstraints.YinYangConstraints2csp import get_or_set_yin_yang_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import multiplication_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, cells2vars
from ortools.sat.python import cp_model

from puzzlesolver.Puzzle2model.BoolConstraints.puzzle_values_modifiers import get_or_set_doublers_grid, get_or_set_vampires_prey_constraint


def set_sum_arrow_constraints(model: PuzzleModel, puzzle: Puzzle):
    """    
    The digits along an arrow must sum to the number in the connecting pill (read left-to right or downwards) or circle.
    Digits may repeat on an arrow if allowed by other rules.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    key = ArrowConstraintsE.ARROW
    # prefix = f"{key.value}"

    for _, properties in enumerate(genArrowConstraintProperties(model, puzzle, key)):
        cells, _, cells_vars, lines_vars, _ = properties

        c_size = len(cells)
        multipliers = [10 ** (c_size - j - 1) for j in range(c_size)]

        for line_vars in lines_vars:
            arrow_vars = line_vars[1:]
            model.Add(sum(arrow_vars) == cp_model.LinearExpr.WeightedSum(
                cells_vars, multipliers))


def set_average_arrow_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    The digits along an arrow must average to the number in the connecting circle.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = ArrowConstraintsE.AVERAGE_ARROW
    prefix = f"{key.value}"

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)
    for i, properties in enumerate(genArrowConstraintProperties(model, puzzle, key)):
        _, _, cells_vars, lines_vars, _ = properties

        c_size = len(cells_vars)
        multipliers = [10 ** (c_size - j - 1) for j in range(c_size)]

        for j, line_vars in enumerate(lines_vars):
            arrow_vars = line_vars[1:]
            n = len(arrow_vars)

            total = model.NewIntVar(
                min_digit, n * max_digit, f"{prefix} {i}: arrow_sum_{j}")
            model.Add(sum(arrow_vars) == total)
            model.AddModuloEquality(0, total, n)
            model.Add(
                total == n * cp_model.LinearExpr.WeightedSum(cells_vars, multipliers))


def set_yin_yang_arrow_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Digits on an arrow sum to the digit in that arrow's circle. The digit in the arrow circle is equal to the sum of all shaded cells in the direction of the arrow tip (beginning from the next cell after the arrow tip).

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = ArrowConstraintsE.YIN_YANG_ARROW
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid_vars = model.grid_vars_dict['cells_grid_vars']
    yin_yang_grid = get_or_set_yin_yang_constraint(model, puzzle)

    max_digit = max(puzzle.valid_digits)
    for i, properties in enumerate(genArrowConstraintProperties(model, puzzle, key)):
        _, lines, cells_vars, _, _ = properties
        multipliers = [10 ** i for i in range(len(cells_vars) - 1, -1, -1)]

        for line in lines:
            arrow_cells = line[1:]
            arrow_vars = cells2vars(grid_vars, arrow_cells)
            model.Add(sum(arrow_vars) == cp_model.LinearExpr.WeightedSum(
                cells_vars, multipliers))

            dr, dc = line[-1].row - line[-2].row, line[-1].col - line[-2].col
            direction = RCToDirectionDict[(dr, dc)]
            cells_after_arrow = puzzle.grid.getCellsInDirection(
                line[-1], direction)
            after_arrow_yin_yang_vars = cells2vars(
                yin_yang_grid, cells_after_arrow)
            after_arrow_vars = cells2vars(grid_vars, cells_after_arrow)

            # scalar product
            n = len(cells_after_arrow)
            t = [model.NewIntVar(
                0, max_digit, f"{prefix} {i} - t_{j}") for j in range(n)]
            for j in range(n):
                model.Add(t[j] == after_arrow_vars[j]).OnlyEnforceIf(
                    after_arrow_yin_yang_vars[j])
                model.Add(t[j] == 0).OnlyEnforceIf(
                    after_arrow_yin_yang_vars[j].Not())

            model.Add(sum(t) == cp_model.LinearExpr.WeightedSum(
                cells_vars, multipliers))


def set_vampire_prey_arrow_constraints(model: PuzzleModel,  puzzle: Puzzle):
    """
    Digits along an arrow sum to the value in its circle. For Arrows/Circles: Prey cells contribute no value; Vampire cells contribute the sum of the digits in the Vampire cell and the Prey cell within the same box.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = ArrowConstraintsE.VAMPIRE_PREY_ARROW
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    # prefix = f"vampire_prey_arrow"
    # grid_vars = model.grid_vars_dict['cells_grid_vars']
    _, _, vampire_prey_values_grid = get_or_set_vampires_prey_constraint(
        model, puzzle)

    for _, properties in enumerate(genArrowConstraintProperties(model, puzzle, key)):
        cells, lines, cells_vars, _, _ = properties
        multipliers = [10 ** i for i in range(len(cells_vars) - 1, -1, -1)]

        for line in lines:
            arrow_cells = line[1:]
            cells_vampire_values_vars = cells2vars(
                vampire_prey_values_grid, cells)
            arrow_vampire_values_vars = cells2vars(
                vampire_prey_values_grid, arrow_cells)
            model.Add(sum(arrow_vampire_values_vars) == cp_model.LinearExpr.WeightedSum(
                cells_vampire_values_vars, multipliers))


def set_doublers_multiplier_arrow_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The digits along each arrow must multiply to the digit in the circled cell. Doublers count as double their value
    on arrows. Doublers aren't necessarily on arrows. The value of the Doubler is counted if
    it appears on a one cell arrow.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = ArrowConstraintsE.DOUBLERS_MULTIPLIER_ARROW
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid_vars = model.grid_vars_dict['cells_grid_vars']
    _, doublers_grid = get_or_set_doublers_grid(model, puzzle)

    lb = min(puzzle.valid_digits)
    ub = max(puzzle.valid_digits)

    for i, properties in enumerate(genArrowConstraintProperties(model, puzzle, key)):
        cells, lines, _, _, _ = properties

        circle_cell = cells[0]
        circle_var = cell2var(grid_vars, circle_cell)
        circle_multiplier = cell2var(doublers_grid, circle_cell)
        circle_t = model.NewIntVar(
            lb, 2 * ub, f"{prefix} {i} - circle_{circle_cell.format_cell()}_t")
        model.AddMultiplicationEquality(
            circle_t, [circle_var, circle_multiplier])

        for j, line in enumerate(lines):
            arrow_cells = line[1:]
            arrow_vars = cells2vars(grid_vars, arrow_cells)
            multipliers = cells2vars(doublers_grid, arrow_cells)

            n = len(arrow_cells)
            t = [model.NewIntVar(
                lb, 2 * ub, f"{prefix} {i} - line_j, t_{_cell.format_cell()}") for _cell in arrow_cells]
            for k in range(n):
                model.AddMultiplicationEquality(
                    t[k], [arrow_vars[k], multipliers[k]])
            product_var = multiplication_csp(
                model, t, f"{prefix} {i} - line_{j} - line_product")
            model.Add(product_var == circle_t)
