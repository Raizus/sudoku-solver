from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel

from puzzlesolver.Puzzle2model.SingleCellConstraints.LoopSingleCellConstraints2csp import set_cell_inside_edge_loop_constraints, set_cell_outside_edge_loop_constraints, set_count_cell_edges_belonging_to_edge_loop_constraints, set_count_seen_cells_inside_edge_loop_constraints

from puzzlesolver.Puzzle2model.SingleCellConstraints.OtherSingleCellConstraints2csp import set_count_cells_not_in_the_same_region_arrows_constraints, set_count_region_sum_line_cells_in_region_constraints, set_galaxy_sum_except_star_constraints, set_l_shaped_region_arrow_points_to_bend_constraints, set_l_shaped_region_bend_count_constraints, set_l_shaped_region_sum_constraints, set_neighbour_cells_same_region_count_except_itself_constraints, set_next_numbered_region_distance_arrows_constraints, set_nurimisaki_unshaded_endpoints_constraints, set_region_loop_sum_cell_constraints, set_seen_region_borders_count_constraints, set_two_contiguous_regions_row_col_opposite_set_count_constraints

from puzzlesolver.Puzzle2model.SingleCellConstraints.SimpleSingleCellConstraints2csp import set_adjacent_cells_in_diff_directions_have_opposite_parity_constraints, set_count_same_parity_neighbour_cells_constraints, set_diagonally_adjacent_sum_constraints, set_even_constraints, set_farsight_constraints, set_friendly_cell_constraints, set_high_digit_constraints, set_indexing_column_constraints, set_indexing_row_constraints, set_low_digit_constraints, set_maximum_constraints, set_minimum_constraints, set_not_watchtower_constraints, set_odd_constraints, set_odd_minesweeper_constraints, set_orthogonal_sum_constraints, set_radar_constraints, set_sandwich_row_col_count_constraints, set_snowball_constraints, set_watchtower_constraints

from puzzlesolver.Puzzle2model.SingleCellConstraints.YinYangSingleCellConstraints2csp import set_yin_yang_minesweeper_constraints, set_yin_yang_same_color_adjacent_count_constraints, set_yin_yang_seen_shaded_cells_constraints, set_yin_yang_seen_unshaded_cells_constraints, set_yin_yang_shaded_cell_constraints, set_yin_yang_shaded_cell_count_in_directions_except_itself_constraints, set_yin_yang_unshaded_cell_constraints


def set_single_cell_constraints(model: PuzzleModel,
                                puzzle: Puzzle):

    set_orthogonal_sum_constraints(model, puzzle)
    set_odd_constraints(model, puzzle)
    set_even_constraints(model, puzzle)
    set_odd_minesweeper_constraints(model, puzzle)
    set_maximum_constraints(model, puzzle)
    set_minimum_constraints(model, puzzle)
    set_indexing_column_constraints(model, puzzle)
    set_indexing_row_constraints(model, puzzle)
    set_radar_constraints(model, puzzle)
    set_watchtower_constraints(model, puzzle)
    set_not_watchtower_constraints(model, puzzle)
    set_low_digit_constraints(model, puzzle)
    set_high_digit_constraints(model, puzzle)
    set_friendly_cell_constraints(model, puzzle)
    set_diagonally_adjacent_sum_constraints(model, puzzle)
    set_farsight_constraints(model, puzzle)
    set_adjacent_cells_in_diff_directions_have_opposite_parity_constraints(
        model, puzzle)
    set_snowball_constraints(model, puzzle)
    set_count_same_parity_neighbour_cells_constraints(model, puzzle)
    set_sandwich_row_col_count_constraints(model, puzzle)

    # set_surround_snake_cells_count_constraints(model, puzzle)
    # set_snake_start_constraints(model, puzzle)
    # set_snake_end_constraints(model, puzzle)
    # set_snake_cell_constraints(model, puzzle)
    # set_not_snake_cell_constraints(model, puzzle)

    set_cell_inside_edge_loop_constraints(model, puzzle)
    set_cell_outside_edge_loop_constraints(model, puzzle)
    set_count_seen_cells_inside_edge_loop_constraints(model, puzzle)
    set_count_cell_edges_belonging_to_edge_loop_constraints(model, puzzle)

    set_yin_yang_seen_unshaded_cells_constraints(model, puzzle)
    set_yin_yang_seen_shaded_cells_constraints(model, puzzle)
    set_yin_yang_minesweeper_constraints(model, puzzle)
    set_yin_yang_same_color_adjacent_count_constraints(model, puzzle)
    set_yin_yang_shaded_cell_constraints(model, puzzle)
    set_yin_yang_unshaded_cell_constraints(model, puzzle)
    set_yin_yang_shaded_cell_count_in_directions_except_itself_constraints(
        model, puzzle)

    set_two_contiguous_regions_row_col_opposite_set_count_constraints(
        model, puzzle)

    set_count_region_sum_line_cells_in_region_constraints(model, puzzle)

    set_l_shaped_region_bend_count_constraints(model, puzzle)
    set_l_shaped_region_arrow_points_to_bend_constraints(model, puzzle)
    set_l_shaped_region_sum_constraints(model, puzzle)

    set_nurimisaki_unshaded_endpoints_constraints(model, puzzle)

    set_galaxy_sum_except_star_constraints(model, puzzle)
    set_seen_region_borders_count_constraints(model, puzzle)
    set_neighbour_cells_same_region_count_except_itself_constraints(
        model, puzzle)
    set_next_numbered_region_distance_arrows_constraints(model, puzzle)
    set_count_cells_not_in_the_same_region_arrows_constraints(model, puzzle)
    # set_same_colored_region_distance_arrows_constraints(
    #     model, puzzle)

    set_region_loop_sum_cell_constraints(model, puzzle)
