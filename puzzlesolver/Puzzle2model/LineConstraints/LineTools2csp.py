from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel

from puzzlesolver.Puzzle2model.LineConstraints.DoubleEndedLineConstraints2csp import set_between_line_constraints, set_double_arrow_constraints, set_doublers_between_line_constraints, set_doublers_double_arrow_constraints, set_lockout_line_constraints, set_parity_count_line_constraints, set_product_of_ends_equals_sum_of_line_constraints, set_tightrope_line_constraints

from puzzlesolver.Puzzle2model.LineConstraints.SimpleLineConstraints2csp import set_adjacent_cells_are_consecutive_or_ratio_line_constraints, set_adjacent_diff_at_least_x_or_sum_at_most_x_constraints, set_adjacent_multiples_line_constraints, set_adjacent_sum_is_prime_line_constraints, set_arithmetic_sequence_line_constraints, set_at_least_x_line_constraints, set_californian_mountain_snake_constraints, set_double_renban_line_constraints, set_doublers_region_sum_line_constraints, set_doublers_thermometer_constraints, set_entropic_line_constraints, set_entropic_or_modular_line_constraints, set_high_low_oscillator_line_constraints, set_hot_cold_thermometer_constraints, set_indexing_column_is_x_line_constraints, set_indexing_row_is_x_line_constraints, set_knabner_line_constraints, set_maximum_adjacent_difference_line_constraints, set_modular_line_constraints, set_modular_or_unimodular_line_constraints, set_n_consecutive_fuzzy_sum_line_constraints, set_n_consecutive_renban_line_constraints, set_n_repeated_digits_line_constraints, set_odd_even_oscillator_line_constraints, set_palindrome_constraints, set_product_line_constraints, set_red_carpet_constraints, set_region_sum_line_constraints, set_renban_line_constraints, set_renban_or_german_whispers_line_constraints, set_renrenbanban_constraints, set_repeated_digits_line_constraints, set_row_cycle_order_thermometers_constraints, set_sum_line_constraints, set_superfuzzy_arrow_constraints, set_thermometer_constraints, set_two_digit_sum_line_constraints, set_two_digit_thermometer_constraints, set_unimodular_line_constraints, set_unique_values_line_constraints, set_whispers_line_constraints, set_xv_line_constraints, set_yin_yang_region_sum_line_constraints


def set_line_constraints(model: PuzzleModel, puzzle: Puzzle):

    set_superfuzzy_arrow_constraints(model, puzzle)

    set_double_arrow_constraints(model, puzzle)
    set_between_line_constraints(model, puzzle)

    set_doublers_between_line_constraints(model, puzzle)
    set_doublers_double_arrow_constraints(model, puzzle)

    set_product_of_ends_equals_sum_of_line_constraints(model, puzzle)
    set_lockout_line_constraints(model, puzzle)
    set_tightrope_line_constraints(model, puzzle)
    set_parity_count_line_constraints(model, puzzle)

    set_renban_line_constraints(model, puzzle)
    set_double_renban_line_constraints(model, puzzle)
    set_n_consecutive_renban_line_constraints(model, puzzle)
    set_whispers_line_constraints(model, puzzle)
    set_unique_values_line_constraints(model, puzzle)
    set_maximum_adjacent_difference_line_constraints(model, puzzle)
    set_palindrome_constraints(model,  puzzle)
    set_thermometer_constraints(model, puzzle)
    set_two_digit_thermometer_constraints(model, puzzle)
    set_row_cycle_order_thermometers_constraints(model, puzzle)

    set_doublers_thermometer_constraints(model, puzzle)
    set_hot_cold_thermometer_constraints(model, puzzle)

    set_region_sum_line_constraints(model, puzzle)
    set_doublers_region_sum_line_constraints(model, puzzle)

    set_red_carpet_constraints(model, puzzle)
    set_repeated_digits_line_constraints(model, puzzle)
    set_n_repeated_digits_line_constraints(model, puzzle)
    set_entropic_line_constraints(model, puzzle)
    set_entropic_or_modular_line_constraints(model, puzzle)
    set_high_low_oscillator_line_constraints(model, puzzle)
    set_odd_even_oscillator_line_constraints(model, puzzle)
    set_at_least_x_line_constraints(model, puzzle)
    set_sum_line_constraints(model, puzzle)
    set_two_digit_sum_line_constraints(model, puzzle)
    set_product_line_constraints(model, puzzle)
    set_adjacent_multiples_line_constraints(model, puzzle)
    set_renrenbanban_constraints(model, puzzle)
    set_knabner_line_constraints(model, puzzle)
    set_arithmetic_sequence_line_constraints(model, puzzle)
    set_modular_line_constraints(model, puzzle)
    set_unimodular_line_constraints(model, puzzle)
    set_modular_or_unimodular_line_constraints(model, puzzle)
    set_xv_line_constraints(model, puzzle)
    set_renban_or_german_whispers_line_constraints(model, puzzle)
    set_n_consecutive_fuzzy_sum_line_constraints(model, puzzle)
    set_adjacent_cells_are_consecutive_or_ratio_line_constraints(model, puzzle)
    set_adjacent_sum_is_prime_line_constraints(model, puzzle)
    set_adjacent_diff_at_least_x_or_sum_at_most_x_constraints(model, puzzle)

    set_indexing_column_is_x_line_constraints(model, puzzle)
    set_indexing_row_is_x_line_constraints(model, puzzle)

    set_yin_yang_region_sum_line_constraints(model, puzzle)
    set_californian_mountain_snake_constraints(model, puzzle)
