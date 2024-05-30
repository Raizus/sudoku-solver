from puzzlesolver.Puzzle.Puzzle import Puzzle

from puzzlesolver.Puzzle2model.EdgeConstraints.OtherEdgeConstraints2csp import set_different_ambiguous_entropy_border_constraints, set_same_ambiguous_entropy_border_constraints, set_unknown_region_border_constraints, set_yin_yang_kropki_constraints
from puzzlesolver.Puzzle2model.EdgeConstraints.SimpleEdgeConstraints2csp import set_difference_constraints, set_edge_exactly_one_friendly_cell_constraints, set_edge_inequality_constraints, set_edge_modulo_constraints, set_edge_multiples_constraints, set_edge_product_constraints, set_edge_square_number_constraints, set_edge_sum_constraints, set_factor_dot_constraints, set_ratio_constraints, set_x_or_v_constraints, set_xv_constraints, set_xy_differences_constraints

from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel


def set_edge_constraints(model: PuzzleModel, puzzle: Puzzle):

    set_ratio_constraints(model, puzzle)
    set_difference_constraints(model, puzzle)
    set_xv_constraints(model,  puzzle)
    set_x_or_v_constraints(model,  puzzle)
    set_edge_multiples_constraints(model,  puzzle)
    set_edge_sum_constraints(model, puzzle)
    set_edge_product_constraints(model, puzzle)
    set_edge_inequality_constraints(model,  puzzle)
    set_edge_modulo_constraints(model, puzzle)
    set_factor_dot_constraints(model, puzzle)
    set_xy_differences_constraints(model, puzzle)
    set_edge_square_number_constraints(model, puzzle)

    set_edge_exactly_one_friendly_cell_constraints(model, puzzle)

    set_yin_yang_kropki_constraints(model, puzzle)
    set_unknown_region_border_constraints(model, puzzle)
    # set_two_snakes_border_constraints(model, grid_vars_dict, puzzle)
    set_same_ambiguous_entropy_border_constraints(model, puzzle)
    set_different_ambiguous_entropy_border_constraints(model, puzzle)
