from itertools import combinations
from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.Directions import DIRECTIONS, getCardinalDirections


from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar

from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import count_vars
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars, int_vars_grid_dict_from_puzzle_grid


def l_shaped_regions_connects_to_bend(model: cp_model.CpModel, cells: list[Cell], is_bend_bools: list[IntVar],
                                      same_region_bools: list[IntVar], direction: DIRECTIONS) -> IntVar:
    cell0 = cells[0]
    links_to_bend_bool = model.NewBoolVar(
        f"l_shaped_regions - {cell0.format_cell()} links_to_bend {direction}")

    if len(cells) <= 1:
        model.Add(links_to_bend_bool == 0)
        return links_to_bend_bool

    bools: list[IntVar] = []
    for i, cell1 in enumerate(cells[1:], 1):
        bool_var = model.NewBoolVar(
            f"l_shaped_regions - {cell0.format_cell()} links to {cell1.format_cell()} bend")
        vars_aux = same_region_bools[0:i] + [is_bend_bools[i]]
        model.AddBoolAnd(vars_aux).OnlyEnforceIf(bool_var)
        model.AddBoolOr([var.Not() for var in vars_aux]
                        ).OnlyEnforceIf(bool_var.Not())
        bools.append(bool_var)

    model.AddBoolOr(bools).OnlyEnforceIf(links_to_bend_bool)
    model.AddBoolAnd([_bool_var.Not() for _bool_var in bools]
                     ).OnlyEnforceIf(links_to_bend_bool.Not())
    return links_to_bend_bool


def _set_l_shaped_regions_constraint(model: PuzzleModel,
                                     puzzle: Puzzle):
    grid = puzzle.grid
    n_rows = grid.nRows
    n_cols = grid.nCols
    grid_vars_dict = model.grid_vars_dict
    all_cells = grid.getAllCells()
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    prefix = f"l_shaped_regions"

    # all_cells_vars = cells2vars(cells_grid_vars, all_cells)
    # max_regions = floor(n_rows * n_cols / 3)
    # max_region_size = len(puzzle.valid_digits)

    # each var represents the cell region
    regions_grid = int_vars_grid_dict_from_puzzle_grid(
        model, grid, 0, n_rows * n_cols, f"l_shaped_regions_grid")
    l_shaped_regions_bend_bools_grid = \
        bool_vars_grid_dict_from_puzzle_grid(
            model, grid, f"l_shaped_regions_bend_bools_grid")

    for cell in all_cells:
        vert_adjacent_cells = grid.getVerticallyAdjacentCells(cell)
        horiz_adjacent_cells = grid.getHorizontallyAdjacentCells(cell)
        region_value_var = cell2var(regions_grid, cell)
        vert_adjacent_region_val_vars = cells2vars(
            regions_grid, vert_adjacent_cells)
        horiz_adjacent_region_val_vars = cells2vars(
            regions_grid, horiz_adjacent_cells)

        vert_adj_region_count = count_vars(model, vert_adjacent_region_val_vars, region_value_var,
                                           f"{prefix} - {cell.format_cell()}, count_adjacent_vert")
        horiz_adj_region_count = count_vars(model, horiz_adjacent_region_val_vars, region_value_var,
                                            f"{prefix} - {cell.format_cell()}, count_adjacent_horiz")

        # each region cell has either 1 or 2 other cells that belong to the same region
        model.Add(vert_adj_region_count +
                  horiz_adj_region_count >= 1)  # type: ignore
        model.Add(vert_adj_region_count + horiz_adj_region_count <= 2)

        count_vert_1_bool = model.NewBoolVar(
            f"{prefix} - {cell.format_cell()}, is_vert_1_bool")
        count_horiz_1_bool = model.NewBoolVar(
            f"{prefix} - {cell.format_cell()}, is_horiz_1_bool")
        count_vert_0_bool = model.NewBoolVar(
            f"{prefix} - {cell.format_cell()}, is_vert_0_bool")
        count_horiz_0_bool = model.NewBoolVar(
            f"{prefix} - {cell.format_cell()}, is_horiz_0_bool")
        cell_regions_bend_bool = cell2var(
            l_shaped_regions_bend_bools_grid, cell)

        model.Add(vert_adj_region_count == 1).OnlyEnforceIf(count_vert_1_bool)
        model.Add(vert_adj_region_count != 1).OnlyEnforceIf(
            count_vert_1_bool.Not())
        model.Add(horiz_adj_region_count == 1).OnlyEnforceIf(
            count_horiz_1_bool)
        model.Add(horiz_adj_region_count != 1).OnlyEnforceIf(
            count_horiz_1_bool.Not())

        model.Add(vert_adj_region_count == 0).OnlyEnforceIf(count_vert_0_bool)
        model.Add(vert_adj_region_count != 0).OnlyEnforceIf(
            count_vert_0_bool.Not())
        model.Add(horiz_adj_region_count == 0).OnlyEnforceIf(
            count_horiz_0_bool)
        model.Add(horiz_adj_region_count != 0).OnlyEnforceIf(
            count_horiz_0_bool.Not())

        # it's a bend if it has one adjacent cell belonging to the same region vertically and
        # one adjacent cell belonging to the same region horizontally
        model.AddBoolAnd(count_vert_1_bool, count_horiz_1_bool).OnlyEnforceIf(
            cell_regions_bend_bool)
        model.AddBoolOr(count_vert_1_bool.Not(), count_horiz_1_bool.Not()).OnlyEnforceIf(
            cell_regions_bend_bool.Not())

        # if not a bend then the region either goes vertical or horizontal
        model.Add(count_horiz_0_bool + count_vert_0_bool ==
                  1).OnlyEnforceIf(cell_regions_bend_bool.Not())

        # the number assigned to each region corresponds to its bend's cell linear index of the grid
        cell_region_var = cell2var(regions_grid, cell)
        model.Add(cell_region_var == cell.row * n_cols +
                  cell.col).OnlyEnforceIf(cell_regions_bend_bool)

    # all different values for each region
    same_region_dict: dict[tuple[tuple[int, int],
                                 tuple[int, int]], IntVar] = dict()
    for cell1, cell2 in combinations(all_cells, 2):
        cell1_var = cell2var(cells_grid_vars, cell1)
        cell2_var = cell2var(cells_grid_vars, cell2)
        cell1_region_var = cell2var(regions_grid, cell1)
        cell2_region_var = cell2var(regions_grid, cell2)
        same_region_bool = model.NewBoolVar(f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()}, "
                                            f"is_same_region_bool")
        model.Add(cell1_region_var == cell2_region_var).OnlyEnforceIf(
            same_region_bool)
        model.Add(cell1_region_var != cell2_region_var).OnlyEnforceIf(
            same_region_bool.Not())
        model.Add(cell1_var != cell2_var).OnlyEnforceIf(same_region_bool)
        same_region_dict[((cell1.row, cell1.col),
                          (cell2.row, cell2.col))] = same_region_bool
        same_region_dict[((cell2.row, cell2.col),
                          (cell1.row, cell1.col))] = same_region_bool

    # if a cell is not a region bend, then it must connect to a bend in a straight line
    directions = getCardinalDirections()
    for cell in all_cells:
        links_to_bend_bools: list[IntVar] = []
        for direction in directions:
            cells = grid.getCellsInDirection(cell, direction)
            cells = [cell] + cells
            same_region_bools: list[IntVar] = []
            for j, cell_b in enumerate(cells[1:], 1):
                cell_a = cells[j - 1]
                same_region_bool = same_region_dict[(
                    (cell_a.row, cell_a.col), (cell_b.row, cell_b.col))]
                same_region_bools.append(same_region_bool)
            is_bend_bools = cells2vars(
                l_shaped_regions_bend_bools_grid, cells)
            links_to_bend_bool = l_shaped_regions_connects_to_bend(model, cells, is_bend_bools,
                                                                   same_region_bools, direction)
            links_to_bend_bools.append(links_to_bend_bool)
        cell_is_bend = cell2var(l_shaped_regions_bend_bools_grid, cell)
        model.AddExactlyOne(*links_to_bend_bools, cell_is_bend)

    grid_vars_dict["l_shaped_regions_grid"] = regions_grid
    grid_vars_dict["l_shaped_regions_bend_bools_grid"] = l_shaped_regions_bend_bools_grid
    return regions_grid


def get_or_set_l_shaped_regions_grid(model: PuzzleModel,
                                     puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "l_shaped_regions_grid" in grid_vars_dict:
        return grid_vars_dict["l_shaped_regions_grid"]

    regions_grid = _set_l_shaped_regions_constraint(model, puzzle)
    return regions_grid
