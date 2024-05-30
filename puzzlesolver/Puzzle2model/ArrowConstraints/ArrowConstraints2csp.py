

from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.ArrowConstraints.SimpleArrowConstraints2csp import set_average_arrow_constraints, set_doublers_multiplier_arrow_constraints, set_sum_arrow_constraints, set_vampire_prey_arrow_constraints, set_yin_yang_arrow_constraints
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel


def set_arrow_constraints(model: PuzzleModel, puzzle: Puzzle):
    set_sum_arrow_constraints(model, puzzle)
    set_average_arrow_constraints(model, puzzle)
    set_yin_yang_arrow_constraints(model, puzzle)
    set_vampire_prey_arrow_constraints(model, puzzle)
    set_doublers_multiplier_arrow_constraints(model, puzzle)
