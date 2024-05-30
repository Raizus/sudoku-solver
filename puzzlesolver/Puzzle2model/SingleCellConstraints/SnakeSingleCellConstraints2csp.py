

# def set_surround_snake_cells_count_constraints(model: PuzzleModel,

#                                                puzzle: Puzzle):
#     """
#     A digit in a circle is equal to the number of snake cells in the (up to) 9 surrounding cells, including itself.

#     :param model:
#     :param grid_vars_dict:
#     :param puzzle:
#     :return:
#     """
#     tool_constraints = puzzle.tool_constraints
#     surround_snake_cells_count_list: List[SurroundSnakeCellsCount] = \
#         tool_constraints.get(
#             SingleCellConstraintsE.SURROUND_SNAKE_CELLS_COUNT_9)
#     if not surround_snake_cells_count_list:
#         return

#     cells_grid_vars = grid_vars_dict['cells_grid_vars']
#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)
#     prefix = f"surround_snake_cells_count"

#     for surround_snake_cells_count in surround_snake_cells_count_list:
#         cell = surround_snake_cells_count.cell
#         cell_var = cell2var(cells_grid_vars, cell)
#         neighbour_cells = puzzle.grid.get_neighbour_cells(cell)
#         neighbour_cells.append(cell)
#         neighbour_snake_vars = cells2vars(snake_grid, neighbour_cells)
#         n = len(neighbour_snake_vars)
#         count_not_snake = count_vars(
#             model, neighbour_snake_vars, 0, f"{prefix} - count_0_{cell.format_cell()}")
#         model.Add(n - count_not_snake == cell_var)


# def set_snake_cell_constraints(model: PuzzleModel,

#                                puzzle: Puzzle):
#     """
#     A green cell is part of a snake.

#     :param model:
#     :param grid_vars_dict:
#     :param puzzle:
#     :return:
#     """

#     tool_constraints = puzzle.tool_constraints
#     snake_cell_list: List[SnakeCell] = \
#         tool_constraints.get(SingleCellConstraintsE.SNAKE_CELL)
#     if not snake_cell_list:
#         return

#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)

#     for snake_cell in snake_cell_list:
#         cell = snake_cell.cell
#         snake_var = cell2var(snake_grid, cell)
#         model.Add(snake_var != 0)


# def set_not_snake_cell_constraints(model: PuzzleModel,

#                                    puzzle: Puzzle):
#     """
#     A grey cell is not part of a snake.

#     :param model:
#     :param grid_vars_dict:
#     :param puzzle:
#     :return:
#     """
#     tool_constraints = puzzle.tool_constraints
#     not_snake_cell_list: List[NotSnakeCell] = \
#         tool_constraints.get(SingleCellConstraintsE.NOT_SNAKE_CELL)
#     if not not_snake_cell_list:
#         return

#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)

#     for snake_cell in not_snake_cell_list:
#         cell = snake_cell.cell
#         snake_var = cell2var(snake_grid, cell)
#         model.Add(snake_var == 0)


# def set_snake_start_constraints(model: PuzzleModel,

#                                 puzzle: Puzzle):
#     """
#     The snake begins in the green cage.

#     :param model:
#     :param grid_vars_dict:
#     :param puzzle:
#     :return:
#     """
#     tool_constraints = puzzle.tool_constraints
#     snake_start_list: List[SnakeStart] = \
#         tool_constraints.get(SingleCellConstraintsE.SNAKE_START)
#     if not snake_start_list:
#         return

#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)
#     snake_neighbours_count_grid = grid_vars_dict[f"snake_1_neighbours_count_grid"]

#     for snake_start in snake_start_list:
#         cell = snake_start.cell
#         snake_neighbours_count_var = cell2var(
#             snake_neighbours_count_grid, cell)
#         model.Add(snake_neighbours_count_var == 1)
#         snake_var = cell2var(snake_grid, cell)
#         model.Add(snake_var != 0)


# def set_snake_end_constraints(model: PuzzleModel,

#                               puzzle: Puzzle):
#     """
#     The snake ends in the red cage.

#     :param model:
#     :param grid_vars_dict:
#     :param puzzle:
#     :return:
#     """
#     tool_constraints = puzzle.tool_constraints
#     snake_end_list: List[SnakeEnd] = \
#         tool_constraints.get(SingleCellConstraintsE.SNAKE_END)
#     if not snake_end_list:
#         return

#     snake_grid = get_or_set_snake_grid(model, grid_vars_dict, puzzle)
#     snake_neighbours_count_grid = grid_vars_dict[f"snake_1_neighbours_count_grid"]

#     for snake_end in snake_end_list:
#         cell = snake_end.cell
#         snake_neighbours_count_var = cell2var(
#             snake_neighbours_count_grid, cell)
#         model.Add(snake_neighbours_count_var == 1)
#         snake_var = cell2var(snake_grid, cell)
#         model.Add(snake_var != 0)
