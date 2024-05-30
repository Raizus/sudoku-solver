from puzzlesolver.Puzzle2model.CageConstraints.RegionsCageConstraints2csp import set_doublers_killer_cage_constraints, set_fountain_killer_cage_constraints, set_hot_cold_killer_cage_constraints, set_multipliers_killer_cage_constraints, set_negators_killer_cage_constraints, set_yin_yang_antithesis_killer_cage_constraints, set_yin_yang_breakeven_killer_cage_constraints
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.CageConstraints.SimpleCageConstraints2csp import set_aquarium_cage_constraints, set_cage_as_a_number_constraints, set_divisible_killer_cage_constraints, set_killer_cage_constraints, set_killer_cage_look_and_say_constraints, set_no_prime_dominos_cage_constraints, set_parity_balance_killer_cage_constraints, set_prime_dominos_cage_constraints, set_putteria_cage_constraints, set_spotlight_cage_constraints, set_sujiken_cage_constraints, set_sum_cage_constraints
from puzzlesolver.Puzzle.Puzzle import Puzzle


def set_cage_constraints(model: PuzzleModel, puzzle: Puzzle):

    set_killer_cage_constraints(model, puzzle)
    set_sum_cage_constraints(model, puzzle)
    set_aquarium_cage_constraints(model, puzzle)
    set_killer_cage_look_and_say_constraints(model, puzzle)
    set_spotlight_cage_constraints(model, puzzle)
    set_putteria_cage_constraints(model, puzzle)
    set_cage_as_a_number_constraints(model, puzzle)
    set_prime_dominos_cage_constraints(model, puzzle)
    set_no_prime_dominos_cage_constraints(model, puzzle)
    set_divisible_killer_cage_constraints(model, puzzle)
    set_parity_balance_killer_cage_constraints(model, puzzle)
    set_sujiken_cage_constraints(model, puzzle)

    set_doublers_killer_cage_constraints(model, puzzle)
    set_negators_killer_cage_constraints(model, puzzle)

    set_yin_yang_antithesis_killer_cage_constraints(model, puzzle)
    set_yin_yang_breakeven_killer_cage_constraints(model, puzzle)

    set_multipliers_killer_cage_constraints(model, puzzle)
    set_fountain_killer_cage_constraints(model, puzzle)
    set_hot_cold_killer_cage_constraints(model, puzzle)
