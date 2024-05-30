from puzzlesolver.Puzzle.Puzzle import Puzzle

from puzzlesolver.Puzzle2model.BoolConstraints.OtherBoolConstraints2csp import set_cells_along_nurimisaki_path_have_a_diff_of_at_least_5_constraints, set_digits_dont_repeat_on_any_diagonal_constraints, set_digits_dont_repeat_on_columns_constraints, set_one_column_is_magic, set_one_of_each_digit_on_columns_constraints, set_yin_yang_unknown_regions_fully_shaded_or_fully_unshaded

from puzzlesolver.Puzzle2model.BoolConstraints.SimpleBoolConstraints2csp import set_all_odd_digits_are_orthogonally_connected_constraints, set_antiking_constraints, set_antiknight_constraints, set_at_least_one_ace_rule_constraints, set_consecutive_close_neighbours, set_consecutive_entanglement_constraints, set_disjoint_groups_constraints, set_dutch_miracle_constraints, set_evens_must_see_identical_digit_by_knights_move_constraints, set_exactly_one_region_is_magic_square_constraints, set_exactly_two_friendly_cells_every_row_col_box_constraints, set_global_indexing_column_constraints, set_global_indexing_disjoint_groups_constraints, set_global_indexing_region_constraints, set_global_indexing_row_constraints, set_ndiagonal_constraints, set_negative_antidiagonal_constraints, set_nonconsecutive_constraints, set_nonratio_constraints, set_odd_digits_cannot_gather_in_2x2_square_constraints, set_odd_even_parity_mirror_along_negative_diagonal_constraint, set_odd_even_parity_mirror_along_positive_diagonal_constraint, set_orthogonally_adjacent_cells_are_not_divisors_constraints, set_pdiagonal_constraints, set_positive_antidiagonal_constraints, set_single_nadir_constraints, set_three_in_the_corner_constraints, set_two_by_two_box_global_entropy_constraints

from puzzlesolver.Puzzle2model.BoolConstraints.ValueModifierConstraints2csp import set_ambiguous_entropy_constraint, set_cell_cannot_be_both_hot_and_cold_constraint, set_center_cell_loop_constraints, set_cold_cells_constraint, set_crossed_paths_constraints, set_decrement_fountain_constraint, set_doublers_constraint, set_hot_cells_constraint, set_l_shaped_regions_constraint, set_marked_cells_constraint, set_vampires_prey_constraint

from puzzlesolver.Puzzle2model.OtherConstraints.NorinoriColouringConstraints2csp import set_all_shaded_norinori_cells_are_odd_constraints
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownRegionsConstraints2csp import set_nine_3x3_unknown_regions_constraint, set_unknown_regions_constraint

from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel


def set_bool_constraints(model: PuzzleModel, puzzle: Puzzle):
    set_unknown_regions_constraint(model, puzzle)
    set_nine_3x3_unknown_regions_constraint(model, puzzle)

    set_vampires_prey_constraint(model, puzzle)
    set_doublers_constraint(model, puzzle)
    set_decrement_fountain_constraint(model, puzzle)
    set_marked_cells_constraint(model, puzzle)
    set_hot_cells_constraint(model, puzzle)
    set_cold_cells_constraint(model, puzzle)
    set_cell_cannot_be_both_hot_and_cold_constraint(model, puzzle)
    set_l_shaped_regions_constraint(model, puzzle)
    set_center_cell_loop_constraints(model, puzzle)
    set_ambiguous_entropy_constraint(model, puzzle)

    set_all_shaded_norinori_cells_are_odd_constraints(model, puzzle)

    set_crossed_paths_constraints(model, puzzle)

    set_digits_dont_repeat_on_columns_constraints(model, puzzle)
    set_one_of_each_digit_on_columns_constraints(model, puzzle)
    set_digits_dont_repeat_on_any_diagonal_constraints(model, puzzle)

    set_pdiagonal_constraints(model, puzzle)
    set_ndiagonal_constraints(model, puzzle)
    set_negative_antidiagonal_constraints(model, puzzle)
    set_positive_antidiagonal_constraints(model, puzzle)

    set_antiknight_constraints(model, puzzle)
    set_antiking_constraints(model, puzzle)

    set_nonconsecutive_constraints(model, puzzle)
    set_nonratio_constraints(model, puzzle)
    set_disjoint_groups_constraints(model, puzzle)

    set_global_indexing_column_constraints(model, puzzle)
    set_global_indexing_row_constraints(model, puzzle)
    set_global_indexing_region_constraints(model, puzzle)
    set_global_indexing_disjoint_groups_constraints(model, puzzle)
    set_two_by_two_box_global_entropy_constraints(model, puzzle)

    set_consecutive_entanglement_constraints(model, puzzle)
    set_consecutive_close_neighbours(model, puzzle)

    set_odd_even_parity_mirror_along_negative_diagonal_constraint(
        model, puzzle)
    set_odd_even_parity_mirror_along_positive_diagonal_constraint(
        model, puzzle)

    set_evens_must_see_identical_digit_by_knights_move_constraints(
        model, puzzle)
    set_orthogonally_adjacent_cells_are_not_divisors_constraints(model, puzzle)
    set_at_least_one_ace_rule_constraints(model, puzzle)

    set_all_odd_digits_are_orthogonally_connected_constraints(model, puzzle)
    set_odd_digits_cannot_gather_in_2x2_square_constraints(model, puzzle)
    set_exactly_two_friendly_cells_every_row_col_box_constraints(model, puzzle)
    set_exactly_one_region_is_magic_square_constraints(model, puzzle)
    set_three_in_the_corner_constraints(model, puzzle)
    set_single_nadir_constraints(model, puzzle)
    set_dutch_miracle_constraints(model, puzzle)

    set_one_column_is_magic(model, puzzle)

    set_cells_along_nurimisaki_path_have_a_diff_of_at_least_5_constraints(
        model, puzzle)

    set_yin_yang_unknown_regions_fully_shaded_or_fully_unshaded(model, puzzle)
