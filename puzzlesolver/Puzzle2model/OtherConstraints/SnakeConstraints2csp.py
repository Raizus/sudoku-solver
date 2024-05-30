from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import count_vars
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, cells2vars
from puzzlesolver.Puzzle2model.puzzle_model_types import GridVars


def set_snake_constraints(model: PuzzleModel,
                          puzzle: Puzzle, num_snakes: int = 1, cannot_touch_itself_diagonally: bool = True):
    grid = puzzle.grid
    grid_vars_dict = model.grid_vars_dict
    all_cells = grid.getAllCells()
    prefix = f"snake"

    snake_grid: GridVars = {}
    for cell in all_cells:
        snake_grid[(cell.row, cell.col)] = model.NewIntVar(
            0, num_snakes, f"{prefix} - {cell.format_cell()}")

    grid_vars_dict["snake_grid"] = snake_grid

    for i in range(num_snakes):
        snake_neighbours_count_grid: GridVars = {}
        for cell in all_cells:
            snake_neighbours_count_grid[(cell.row, cell.col)] = \
                model.NewIntVar(
                    0, 4, f"{prefix} - snake_{i + 1} - neighbours_count_{cell.format_cell()}")

        grid_vars_dict[f"snake_{i + 1}_neighbours_count_grid"] = snake_neighbours_count_grid

    # snake cannot touch itself
    for i in range(num_snakes):
        is_snake_i_grid: GridVars = {}
        snake_neighbours_count_grid = grid_vars_dict[f"snake_{i + 1}_neighbours_count_grid"]
        for cell in all_cells:
            snake_cell_var = cell2var(snake_grid, cell)
            snake_neighbour_count_var = cell2var(
                snake_neighbours_count_grid, cell)
            orthogonal_cells = grid.getOrthogonallyAdjacentCells(cell)
            orthogonal_vars = cells2vars(snake_grid, orthogonal_cells)

            is_snake_var = model.NewBoolVar(
                f"{prefix} - is_snake_{i + 1} - {cell.format_cell()}")
            is_snake_i_grid[(cell.row, cell.col)] = is_snake_var
            model.Add(snake_cell_var == i + 1).OnlyEnforceIf(is_snake_var)
            model.Add(snake_cell_var != i +
                      1).OnlyEnforceIf(is_snake_var.Not())

            name = f"{prefix} - count_snake_{i + 1}_orthogonal_{cell.format_cell()}"
            snake_count_orthogonal = count_vars(
                model, orthogonal_vars, i + 1, name)
            model.Add(snake_count_orthogonal ==
                      snake_neighbour_count_var).OnlyEnforceIf(is_snake_var)
            # if a cell is part of the snake it must be connected to 1 or 2 other snake cells
            # if cell is snake ==> neighbour count == {1,2}
            # if cell is not snake ==> neighbour count == 0
            model.Add(snake_neighbour_count_var >=
                      1).OnlyEnforceIf(is_snake_var)
            model.Add(snake_neighbour_count_var <=
                      2).OnlyEnforceIf(is_snake_var)
            model.Add(snake_neighbour_count_var ==
                      0).OnlyEnforceIf(is_snake_var.Not())

            # if snake CANNOT TOUCH ITSELF DIAGONALLY, then a not snake cell must have, at most,
            # 3 orthogonally adjacent snake cells
            # if cannot_touch_itself_diagonally:
            #     model.Add(count_orthogonal <= 3).OnlyEnforceIf(is_snake_var.Not())

        grid_vars_dict[f"is_snake_{i + 1}_grid"] = is_snake_i_grid

    for i in range(num_snakes):
        # the start and end of the snake have 1 neighbour -> there must be 2 "1"s in counts
        # the middles of the snake have 2 neighbour -> there must be n-2 "2"s in counts
        snake_vars = cells2vars(snake_grid, all_cells)
        snake_cells_count = count_vars(
            model, snake_vars, i + 1, f"{prefix} - snake_{i + 1}_cells_count")

        snake_neighbours_count_grid = grid_vars_dict[f"snake_{i + 1}_neighbours_count_grid"]
        neighbour_count_vars = cells2vars(
            snake_neighbours_count_grid, all_cells)

        count_snake_ends = count_vars(
            model, neighbour_count_vars, 1, f"{prefix} - count_snake_{i + 1}_ends")
        model.Add(count_snake_ends == 2)
        count_snake_middles = count_vars(
            model, neighbour_count_vars, 2, f"{prefix} - count_snake_{i + 1}_middles")
        model.Add(count_snake_middles == snake_cells_count - 2)

    for i in range(num_snakes):
        # no 2x2 filled
        for cell in all_cells:
            box_2x2 = [cell for line in grid.getXByYBox(
                cell, 2, 2) for cell in line]
            if len(box_2x2) != 4:
                continue
            box_vars = cells2vars(snake_grid, box_2x2)
            snake_count = count_vars(model, box_vars, i + 1,
                                     f"{prefix} - count_{cell.format_cell()}_2x2, snake_{i + 1}")
            model.Add(snake_count != 4)

    # snake can't touch itself diagonally
    # no [1, 0] or [0, 1] patterns allowed
    #    [0, 1]    [1, 0]
    # for i in range(grid.nRows - 1):
    #     for j in range(grid.nCols - 1):
    #         cell = grid.get_cell(i, j)
    #         two_by_two = grid.get_x_by_y_box(cell, 2, 2)
    #         two_by_two_vars = vars_from_cells(snake_grid, two_by_two)
    #
    #         a = model.NewBoolVar(f"snake: no crossing a ({i}, {j}) == ({i + 1}, {j + 1})")
    #         b = model.NewBoolVar(f"snake: no crossing b ({i}, {j + 1}) == ({i + 1}, {j})")
    #         model.Add(two_by_two_vars[0] == two_by_two_vars[3]).OnlyEnforceIf(a)
    #         model.Add(two_by_two_vars[1] == two_by_two_vars[2]).OnlyEnforceIf(b)
    #         model.Add(two_by_two_vars[0] != two_by_two_vars[3]).OnlyEnforceIf(a.Not())
    #         model.Add(two_by_two_vars[1] != two_by_two_vars[2]).OnlyEnforceIf(b.Not())

    return snake_grid


def get_or_set_snake_grid(model: PuzzleModel,
                          puzzle: Puzzle, num_snakes: int = 1):
    grid_vars_dict = model.grid_vars_dict
    if "snake_grid" in grid_vars_dict:
        return grid_vars_dict["snake_grid"]

    snake_grid = set_snake_constraints(
        model, puzzle, num_snakes)
    return snake_grid


# def set_snake_ends_must_be_nines_constraints(model: PuzzleModel,
#                                              puzzle: Puzzle):
#     grid = puzzle.grid
#     cells_grid_vars = grid_vars_dict['cells_grid_vars']
#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)
#     snake_neighbours_count_grid = grid_vars_dict["snake_1_neighbours_count_grid"]
#     all_cells = grid.get_all_cells()

#     for cell in all_cells:
#         cell_neighbour_count = cell2var(snake_neighbours_count_grid, cell)
#         cell_var = cell2var(cells_grid_vars, cell)
#         b = model.NewBoolVar("b")
#         model.Add(cell_neighbour_count == 1).OnlyEnforceIf(b)
#         model.Add(cell_neighbour_count != 1).OnlyEnforceIf(b.Not())
#         model.Add(cell_var == 9).OnlyEnforceIf(b)


# def set_three_snakes_fill_the_grid_constraints(model: PuzzleModel,
#                                                puzzle: Puzzle):
#     grid = puzzle.grid
#     cells_grid_vars = grid_vars_dict['cells_grid_vars']
#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle, 3)
#     all_cells = grid.get_all_cells()

#     snake_grid_vars = cells2vars(snake_grid, all_cells)
#     count_not_snake = count_vars(
#         model, snake_grid_vars, 0, f"three_snakes_fill_the_grid")
#     model.Add(count_not_snake == 0)


# def set_adjacent_cells_along_a_snake_differ_by_4_or_5_constraints(model: PuzzleModel,
#                                                                   puzzle: Puzzle):
#     # ADJACENT_CELLS_ALONG_A_SNAKE_DIFFER_BY_4_OR_5
#     grid = puzzle.grid
#     cells_grid_vars = grid_vars_dict['cells_grid_vars']
#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle, 3)
#     all_cells = grid.get_all_cells()
#     prefix = f"adjacent_cells_along_a_snake_differ_by_4_or_5"

#     min_digit = min(puzzle.valid_digits)
#     max_digit = max(puzzle.valid_digits)

#     for cell in all_cells:
#         adjacent_cells = grid.get_orthogonally_adjacent_cells(cell)
#         cell_var = cell2var(cells_grid_vars, cell)
#         snake_var = cell2var(snake_grid, cell)
#         filtered_adjacent_cells = [_cell for _cell in adjacent_cells
#                                    if _cell.row >= cell.row and _cell.col >= cell.col]

#         for cell2 in filtered_adjacent_cells:
#             cell2_var = cell2var(cells_grid_vars, cell2)
#             snake2_var = cell2var(snake_grid, cell2)
#             name = f"{prefix} - belong_to_same_snake_{cell.format_cell()}_{cell2.format_cell()}"
#             belong_to_same_snake = model.NewBoolVar(name)
#             model.Add(snake_var == snake2_var).OnlyEnforceIf(
#                 belong_to_same_snake)
#             model.Add(snake_var != snake2_var).OnlyEnforceIf(
#                 belong_to_same_snake.Not())

#             dist = model.NewIntVar(0, max_digit - min_digit,
#                                    f"{prefix} - dist_{cell.format_cell()}_{cell2.format_cell()}")
#             model.AddAbsEquality(dist, cell_var - cell2_var)
#             bool_is_4_or_5_dist = is_member_of(model, [4, 5], dist, f"{prefix} - "
#                                                                     f"dist_{cell.format_cell()}_{cell2.format_cell()}")
#             model.Add(bool_is_4_or_5_dist == 1).OnlyEnforceIf(
#                 belong_to_same_snake)


# def set_adjacent_cells_along_a_snake_differ_by_at_least_5_constraints(model: PuzzleModel,
#                                                                       puzzle: Puzzle):
#     # ADJACENT_CELLS_ALONG_A_SNAKE_DIFFER_BY_4_OR_5
#     grid = puzzle.grid
#     cells_grid_vars = grid_vars_dict['cells_grid_vars']
#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)
#     all_cells = grid.get_all_cells()
#     prefix = f"adjacent_cells_along_a_snake_differ_by_at_least_5"

#     min_digit = min(puzzle.valid_digits)
#     max_digit = max(puzzle.valid_digits)
#     snake_1_dict = grid_vars_dict['is_snake_1_grid']

#     for cell in all_cells:
#         adjacent_cells = grid.get_orthogonally_adjacent_cells(cell)
#         cell_var = cell2var(cells_grid_vars, cell)
#         snake_var = cell2var(snake_1_dict, cell)
#         filtered_adjacent_cells = [_cell for _cell in adjacent_cells
#                                    if _cell.row >= cell.row and _cell.col >= cell.col]

#         for cell2 in filtered_adjacent_cells:
#             cell2_var = cell2var(cells_grid_vars, cell2)
#             snake_var2 = cell2var(snake_1_dict, cell2)
#             name = f"{prefix} - belong_to_same_snake_{cell.format_cell()}_{cell2.format_cell()}"
#             belong_to_same_snake = model.NewBoolVar(name)
#             model.AddBoolAnd(snake_var, snake_var2).OnlyEnforceIf(
#                 belong_to_same_snake)
#             model.AddBoolOr(snake_var.Not(), snake_var2.Not()
#                             ).OnlyEnforceIf(belong_to_same_snake.Not())

#             dist = model.NewIntVar(0, max_digit - min_digit,
#                                    f"{prefix} - dist_{cell.format_cell()}_{cell2.format_cell()}")
#             model.AddAbsEquality(dist, cell_var - cell2_var)
#             model.Add(dist >= 5).OnlyEnforceIf(belong_to_same_snake)


# def set_snake_cannot_touch_difference_dots_constraints(model: PuzzleModel,
#                                                        puzzle: Puzzle):
#     grid = puzzle.grid
#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)
#     prefix = f"snake_cannot_touch_difference_dots"
#     tool_constraints = puzzle.tool_constraints

#     difference_list: List[Difference] = tool_constraints.get(
#         EdgeConstraintsE.DIFFERENCE)
#     difference_cells = list(
#         set([cell for difference in difference_list for cell in difference.cells]))

#     for cell in difference_cells:
#         snake_var = cell2var(snake_grid, cell)
#         model.Add(snake_var == 0)


# def set_snake_must_visit_every_region_constraints(model: PuzzleModel,
#                                                   puzzle: Puzzle):
#     grid = puzzle.grid
#     cells_grid_vars = grid_vars_dict['cells_grid_vars']
#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)
#     prefix = f"snake_must_visit_every_region"
#     tool_constraints = puzzle.tool_constraints

#     regions = grid.get_used_regions()

#     for region_val in regions:
#         cells = grid.get_region_cells(region_val)
#         snake_vars = cells2vars(snake_grid, cells)
#         count_not_snake_cells_in_region = \
#             count_vars(model, snake_vars, 0,
#                        f"{prefix} - region_{region_val} count_not_snakes")
#         model.Add(count_not_snake_cells_in_region < len(snake_vars))


# def set_snake_next_cell_is_sum_of_previous_two_mod_10_constraints(model: PuzzleModel,
#                                                                   puzzle: Puzzle):
#     grid = puzzle.grid
#     n_rows = grid.nRows
#     n_cols = grid.nCols
#     cells_grid_vars = grid_vars_dict['cells_grid_vars']
#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)
#     prefix = f"snake_next_cell_is_sum_of_previous_two_mod_10"
#     all_cells = grid.get_all_cells()
#     tool_constraints = puzzle.tool_constraints

#     min_digit = min(puzzle.valid_digits)
#     max_digit = max(puzzle.valid_digits)
#     snake_1_dict = grid_vars_dict['is_snake_1_grid']
#     snake_start_list: List[SnakeStart] = tool_constraints.get(
#         SingleCellConstraintsE.SNAKE_START)
#     if not snake_start_list:
#         return

#     max_mod = max([digit % 10 for digit in puzzle.valid_digits])
#     snake_start = snake_start_list[0]
#     snake_start_cell = snake_start.cell

#     # snake_cells_count = model.NewIntVar(0, n_rows * n_cols, f"{prefix} - snake_1_cells_count")
#     # snake_vars = vars_from_cells(snake_grid, all_cells)
#     # count_vars(model, snake_vars, i + 1, snake_cells_count, f"{prefix} - snake_1_cells_count")

#     # TODO unfinished
#     # maybe an ordered floodfill?
#     # ordered_sake_grid: GridVars = {}
#     # for cell in all_cells:
#     #     ordered_sake_grid[(cell.row, cell.col)] = \
#     #         model.NewIntVar(0, n_rows * n_cols, f"{prefix} - ordered_snake_var - {cell.format_cell()}")
#     #
#     # start_ordered_snake_var = cell2var(ordered_sake_grid, snake_start_cell)
#     # model.Add(start_ordered_snake_var == 1)
