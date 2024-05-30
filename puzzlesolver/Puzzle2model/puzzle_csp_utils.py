from itertools import product
from typing import Union, List, Iterable

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar

from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.Coords import GridCoords
from puzzlesolver.Puzzle.Grid import Grid


from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_model_types import AdjacencyDict, AdjacencyVarsDict, GridVars
from puzzlesolver.Puzzle2model.custom_constraints import are_all_equal_csp, are_all_true_csp, are_any_true_csp, count_vars, only_first_of_bools, expand

PRIME_LIST = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103,
              107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223,
              227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347,
              349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
              467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
              613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743,
              751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883,
              887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

SQUARE_NUMBERS_LIST2 = [1, 4, 9, 16, 25, 36, 49, 64, 81]


def edge_from_cells(adjacency_vars_dict: AdjacencyVarsDict, cell1: Cell, cell2: Cell) -> Union[IntVar, None]:
    edges_of_cell1 = adjacency_vars_dict.get((cell1.row, cell1.col))
    if not edges_of_cell1:
        return None
    return edges_of_cell1.get((cell2.row, cell2.col))


def cell2var(grid_vars: GridVars, cell: Cell) -> IntVar:
    var = grid_vars.get((cell.row, cell.col))
    if var is None:
        raise Exception(f"{(cell.row, cell.col)} is not a member of grid_vars")
    return var


def tuple2var(grid_vars: GridVars, coords: tuple[int, int]) -> IntVar:
    r, c = coords
    var = grid_vars.get((r, c))
    if var is None:
        raise Exception(f"{(r, c)} is not a member of grid_vars")
    return var


def tuples2vars(grid_vars: GridVars, coords: list[tuple[int, int]]) -> list[IntVar]:
    coords_vars: list[IntVar] = []
    for coord in coords:
        var = tuple2var(grid_vars, coord)
        coords_vars.append(var)
    return coords_vars


def coord2var(grid_vars: GridVars, coord: GridCoords) -> IntVar:
    if not isinstance(coord.r, int) or not isinstance(coord.c, int):
        raise Exception(f"{(coord.r, coord.c)} is not a member of grid_vars")
    var = grid_vars.get((coord.r, coord.c))
    if var is None:
        raise Exception(f"{(coord.r, coord.c)} is not a member of grid_vars")
    return var


def cells2vars(grid_vars: dict[tuple[int, int], IntVar], cells: List[Cell]) -> List[IntVar]:
    cell_vars: list[IntVar] = []
    for cell in cells:
        try:
            cell_var = cell2var(grid_vars, cell)
            cell_vars.append(cell_var)
        except Exception:
            pass
    return cell_vars


def coords2vars(grid_vars: dict[tuple[int, int], IntVar], coords: list[GridCoords]) -> List[IntVar]:
    cell_vars: list[IntVar] = []
    for coord in coords:
        try:
            cell_var = coord2var(grid_vars, coord)
            cell_vars.append(cell_var)
        except Exception:
            pass
    return cell_vars


def get_row_or_col_from_outside_cell(grid: Grid, cell: Cell) -> List[Cell]:
    # cell might be part of the grid, but outside cell or not part of the grid (defaults to outside cell)
    if not cell.outside:
        return []

    in_grid = True if grid.getCell(cell.row, cell.col) else False
    # points to row if the col is outside the grid
    is_row = True if not in_grid and (cell.col < 0 or cell.col >= grid.nCols) else \
        True if in_grid and (cell.col == 0 or cell.col ==
                             grid.nCols - 1) else False

    # points to row if the col is outside the grid
    is_col = True if not in_grid and (cell.row < 0 or cell.row >= grid.nRows) else \
        True if in_grid and (cell.row == 0 or cell.row ==
                             grid.nRows - 1) else False

    cells = []
    if is_row and is_row != is_col:
        cells = grid.getRow(cell.row)
        right_side = True if (not in_grid and cell.col >= grid.nCols) or (
            in_grid and cell.col == grid.nCols - 1) else False
        if right_side:
            cells.reverse()
    elif is_col and is_col != is_row:
        cells = grid.getCol(cell.col)
        bottom = True if (not in_grid and cell.row >= grid.nRows) or (
            in_grid and cell.row == grid.nRows - 1) else False
        if bottom:
            cells.reverse()

    return cells


def min_in_n_cells(n: int) -> int:
    return sum(range(1, n + 1))


def max_in_n_cells(n: int, max_val: int) -> int:
    return sum(range(max_val, max_val - n - 1, -1))


def min_cells_to_sum(sum_val: int, max_val: int) -> int:
    for n in range(1, max_val):
        val = max_in_n_cells(n, max_val)
        if val < sum_val:
            continue
        return n
    return 0


def max_cells_to_sum(sum_val: int, max_val: int) -> int:
    for n in range(1, max_val):
        val = min_in_n_cells(n)
        if val < sum_val:
            continue
        return n
    return 0


def bool_vars_grid_dict_from_cells(model: cp_model.CpModel,
                                   cells: List[Cell],
                                   prefix: str) -> GridVars:
    """
    Creates a dictionary of BoolVar with for every cell in the puzzle grid, with keys (cell.row, cell.col)
    Useful for yin_yang_grid, doublers_grid, odd/even_grid, etc
    :param cells:
    :param model:
    :param prefix: the boolean variables' name prefix
    :return: bool_grid
    """
    bool_grid: GridVars = dict()

    for cell in cells:
        bool_grid[(cell.row, cell.col)] = model.NewBoolVar(
            f"{prefix} - {cell.format_cell()}")

    return bool_grid


def bool_vars_grid_dict_from_puzzle_grid(model: cp_model.CpModel,
                                         grid: Grid,
                                         prefix: str) -> GridVars:
    """
    Creates a dictionary of BoolVar with for every cell in the puzzle grid, with keys (cell.row, cell.col)
    Useful for yin_yang_grid, doublers_grid, odd/even_grid, etc
    :param model:
    :param grid:
    :param prefix: the boolean variables' name prefix
    :return: bool_grid
    """
    all_cells = grid.getAllCells()
    return bool_vars_grid_dict_from_cells(model, all_cells, prefix)


def int_vars_grid_dict_from_puzzle_grid(model: cp_model.CpModel, grid: Grid, lb: int, ub: int,
                                        prefix: str) -> GridVars:
    """Creates a dictionary of IntVar with for every cell in the puzzle grid, with keys (cell.row, cell.col)

    Args:
        model (cp_model.CpModel): 
        grid (Grid): 
        lb (int): 
        ub (int): 
        prefix (str): 

    Returns:
        GridVars: 
    """
    grid_dict: GridVars = dict()
    all_cells = grid.getAllCells()
    prefix = f"{prefix} - " if len(prefix) else ""
    for cell in all_cells:
        grid_dict[(cell.row, cell.col)] = model.NewIntVar(
            lb, ub, f"{prefix}{cell.format_cell()}")

    return grid_dict


def exactly_n_per_row(model: cp_model.CpModel, grid: Grid, bools_grid_dict: GridVars, n: int = 1):
    n_rows = grid.nRows
    for row in range(n_rows):
        cells = grid.getRow(row)
        _vars = cells2vars(bools_grid_dict, cells)
        model.Add(sum(_vars) == n)


def exactly_n_per_col(model: cp_model.CpModel, grid: Grid, bools_grid_dict: GridVars, n: int = 1):
    n_cols = grid.nCols
    for col in range(n_cols):
        cells = grid.getCol(col)
        _vars = cells2vars(bools_grid_dict, cells)
        model.Add(sum(_vars) == n)


def exactly_n_per_region(model: cp_model.CpModel, grid: Grid, bools_grid_dict: GridVars, n: int = 1):
    regions = grid.getUsedRegions()
    for region in regions:
        cells = grid.getRegionCells(region)
        _vars = cells2vars(bools_grid_dict, cells)
        model.Add(sum(_vars) == n)


def exactly_n_per_row_col_region(model: cp_model.CpModel, grid: Grid, bools_grid_dict: GridVars, n: int = 1):
    exactly_n_per_row(model, grid, bools_grid_dict, n)

    # Only 1 multiplier per col
    exactly_n_per_col(model, grid, bools_grid_dict, n)

    # Only 1 multiplier per region
    exactly_n_per_region(model, grid, bools_grid_dict, n)


def one_of_each_digit(model: cp_model.CpModel, valid_digits: List[int], int_vars_list: List[IntVar], prefix: str):
    for value in valid_digits:
        digit_count = count_vars(model, int_vars_list,
                                 value, f"{prefix} - count_(digit={value})")
        model.Add(digit_count == 1)


def get_masked_vars_grid_dict(model: cp_model.CpModel, valid_digits: List[int], grid: Grid,
                              mask_bools_grid_dict: GridVars, cells_vars_dict: GridVars,
                              prefix: str) -> GridVars:
    min_digit = min(valid_digits)
    max_digit = max(valid_digits)
    masked_vars_grid_dict: GridVars = \
        int_vars_grid_dict_from_puzzle_grid(model, grid, min_digit - 1, max_digit,
                                            f"{prefix}")
    all_cells = grid.getAllCells()
    for cell in all_cells:
        bool_var = cell2var(mask_bools_grid_dict, cell)
        cell_var = cell2var(cells_vars_dict, cell)
        masked_digit_var = cell2var(masked_vars_grid_dict, cell)
        model.Add(masked_digit_var == cell_var).OnlyEnforceIf(bool_var)
        model.Add(masked_digit_var == min_digit -
                  1).OnlyEnforceIf(bool_var.Not())

    return masked_vars_grid_dict


def is_magic_column_constraint(model: PuzzleModel, puzzle: Puzzle, col: int):
    grid = puzzle.grid
    prefix = f"is_magic_column - col={col}"

    cells_grid_vars = model.grid_vars_dict['cells_grid_vars']
    filled_cells_grid = model.grid_vars_dict.get("filled_cells_grid")

    bools: list[IntVar] = []
    for cell in grid.getCol(col):
        prefix2 = f"{prefix} - row={cell.row}"
        row_cells = grid.getRow(cell.row)
        cell_var = cell2var(cells_grid_vars, cell)
        row_vars = cells2vars(cells_grid_vars, row_cells)
        name = f"{prefix2} - count"
        count = count_vars(model, row_vars, cell_var, name)
        bool_var = model.NewBoolVar(f"{prefix} - count_matches_bool")
        count_equal_cell = are_all_equal_csp(
            model, [count, cell_var], f"{prefix2} - count==cell bool")

        if not filled_cells_grid:
            model.Add(bool_var == count_equal_cell)
        else:
            filled_cell_var = cell2var(filled_cells_grid, cell)
            model.Add(bool_var == count_equal_cell).OnlyEnforceIf(
                filled_cell_var)
            model.Add(bool_var == 1).OnlyEnforceIf(filled_cell_var.Not())

        bools.append(bool_var)

    bool_is_magic_column = are_all_true_csp(
        model, bools, f"{prefix} - bool_is_magic_column")

    return bool_is_magic_column


# -------------------------------------------------------------------------------------------------------------------- #
# region Regions Constraints ----------------------------------------------------------------------------------------- #

def _set_marked_cells_constraint(model: PuzzleModel,
                                 puzzle: Puzzle):

    grid_vars_dict = model.grid_vars_dict
    grid = puzzle.grid
    n_rows = grid.nRows
    n_cols = grid.nCols
    all_cells = grid.getAllCells()
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    prefix = f"marked_cells"

    # create marked cells bool grid, var == 1 if marked cell, else var == 0
    marked_cells_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix} - bools_grid")

    # one marked cell per col, row and region
    exactly_n_per_row_col_region(model, grid, marked_cells_bools_grid, 1)

    # grid with the marked digits: if digit is marked then var == digit, else var = min_digit - 1
    marked_digits_grid: GridVars = \
        get_masked_vars_grid_dict(model, puzzle.valid_digits, grid,
                                  marked_cells_bools_grid, cells_grid_vars, f"marked_digits_grid")

    # One of each digit is a marked cell
    all_marked_digits_vars = cells2vars(marked_digits_grid, all_cells)
    one_of_each_digit(model, puzzle.valid_digits,
                      all_marked_digits_vars, prefix)

    # The digit in the first cell of a row, column, or region gives the position of the marked cell in that row, column or region.
    for row in range(n_rows):
        cells = grid.getRow(row)
        cells_vars = cells2vars(cells_grid_vars, cells)
        first_cell_var = cells_vars[0]
        for i, cell in enumerate(cells, 1):
            marked_cell_var = cell2var(marked_cells_bools_grid, cell)
            model.Add(first_cell_var == i).OnlyEnforceIf(marked_cell_var)
            model.Add(first_cell_var != i).OnlyEnforceIf(marked_cell_var.Not())

    for col in range(n_cols):
        cells = grid.getCol(col)
        cells_vars = cells2vars(cells_grid_vars, cells)
        first_cell_var = cells_vars[0]
        for i, cell in enumerate(cells, 1):
            marked_cell_var = cell2var(marked_cells_bools_grid, cell)
            model.Add(first_cell_var == i).OnlyEnforceIf(marked_cell_var)
            model.Add(first_cell_var != i).OnlyEnforceIf(marked_cell_var.Not())

    for region in grid.getUsedRegions():
        cells = grid.getRegionCells(region)
        cells_vars = cells2vars(cells_grid_vars, cells)
        first_cell_var = cells_vars[0]
        for i, cell in enumerate(cells, 1):
            marked_cell_var = cell2var(marked_cells_bools_grid, cell)
            model.Add(first_cell_var == i).OnlyEnforceIf(marked_cell_var)
            model.Add(first_cell_var != i).OnlyEnforceIf(marked_cell_var.Not())

    grid_vars_dict["marked_digits_grid"] = marked_digits_grid
    grid_vars_dict["marked_cells_bools_grid"] = marked_cells_bools_grid

    return marked_cells_bools_grid, marked_digits_grid


def get_or_set_marked_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "marked_digits_grid" in grid_vars_dict:
        return grid_vars_dict["marked_digits_grid"]

    marked_digits_grid = _set_marked_cells_constraint(model, puzzle)
    return marked_digits_grid


# endregion Regions Constraints -------------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# region Orthogonally Connected Regions ------------------------------------------------------------------------------ #

def orthogonally_connected_region_csp(model: cp_model.CpModel, adjacency_dict: AdjacencyDict,
                                      region_vars_dict: GridVars, region_max_size: int,
                                      seed: list[tuple[int, int]] | None = None):
    """
    Given a grid of bool vars (region), and an adjacency dictionary,
    all the 1's in the grid must be orthogonally connected.

    :param model:
    :param adjacency_dict:
    :param region_vars_dict:
    :param region_max_size:
    :param seed:
    :return:
    """
    # volume: set[tuple[int, int, int]] = set()

    exact: bool = False
    # (r, c, depth)
    volume_vars_dict: dict[tuple[int, int, int], IntVar] = dict()
    base = set(adjacency_dict.keys()) & set(region_vars_dict.keys())
    prefix = f"orthogonally_connected_region"

    all_region_vars = list(region_vars_dict.values())
    enforce_layer_sum_bool = model.NewBoolVar(
        f"{prefix} - enforce_layer_sum_bool")
    model.AddBoolOr(all_region_vars).OnlyEnforceIf(enforce_layer_sum_bool)
    model.AddBoolAnd([x.Not() for x in all_region_vars]
                     ).OnlyEnforceIf(enforce_layer_sum_bool.Not())

    current_layer_cells: set[tuple[int, int]] = base
    if seed is not None:
        current_layer_cells = set(seed)

    for layer in range(region_max_size):
        current_layer_coords = [(row, col, layer)
                                for row, col in current_layer_cells]
        # volume |= set(cells2)
        for r, c, l in current_layer_coords:
            volume_vars_dict[(r, c, l)] = model.NewBoolVar(
                f"{prefix} - floodfill_volume: ({r},{c},{l})")

        # at layer 0 only 1 variable can be 1 (the seed)
        # if exact => only one cell can be 1 per layer (and its only 1 at most once per column)
        if layer == 0 or exact:
            layer_vars = [volume_vars_dict[coords]
                          for coords in current_layer_coords]
            model.Add(sum(layer_vars) == 1).OnlyEnforceIf(
                enforce_layer_sum_bool)
        if layer == 0:
            seed_cells = [(r, c) for r, c, _ in current_layer_coords]
            seed_cells.sort(key=lambda cell: cell[1])
            seed_cells.sort(key=lambda cell: cell[0])
            layer_0_summary_vars = [
                region_vars_dict[(r, c)] for r, c in seed_cells]
            layer_0_vars = [volume_vars_dict[(r, c, 0)] for r, c in seed_cells]
            bools = only_first_of_bools(
                model, layer_0_summary_vars, f"{prefix}")
            for i, layer_0_var in enumerate(layer_0_vars):
                model.Add(bools[i] == layer_0_var)

        # growth rules
        prev_layer = (layer - 1) % region_max_size
        for r, c in current_layer_cells:
            cell_and_adjacent = expand(adjacency_dict, [(r, c)])
            current_layer_cell_var = volume_vars_dict[(r, c, layer)]
            cell_summary_var = region_vars_dict[(r, c)]
            if layer == 0:
                continue

            if exact:
                cell_and_adjacent.discard((r, c))
                previous_layers = [_l for _l in range(layer)]
                prev_layer_cell_and_adj = set((_r, _c, _l) for (_r, _c), _l
                                              in product(cell_and_adjacent, previous_layers))
            else:
                # if a cell is 1 in the previous layer then it cannot be 1 in the current one
                prev_layer_cell_var = volume_vars_dict.get((r, c, prev_layer))
                if prev_layer_cell_var is not None:
                    model.Add(current_layer_cell_var == 1).OnlyEnforceIf(
                        prev_layer_cell_var)
                prev_layer_cell_and_adj = set(
                    (_r, _c, prev_layer) for _r, _c in cell_and_adjacent)

            prev_layer_cell_and_adj &= set(volume_vars_dict.keys())
            cells3_vars = [volume_vars_dict[coords]
                           for coords in prev_layer_cell_and_adj]

            if not exact:
                bool_aux = model.NewBoolVar(
                    f"{prefix} - any_cell_or_adj_in_previous_layer ({r}, {c})")
                model.AddBoolOr(cells3_vars).OnlyEnforceIf(bool_aux)
                model.AddBoolAnd([x.Not() for x in cells3_vars]
                                 ).OnlyEnforceIf(bool_aux.Not())
                model.AddBoolAnd(bool_aux, cell_summary_var).OnlyEnforceIf(
                    current_layer_cell_var)
                model.AddBoolOr(bool_aux.Not(), cell_summary_var.Not()).OnlyEnforceIf(
                    current_layer_cell_var.Not())

            # if the cell and adjacent in the previous layer are all zero, then the cell in the current layer must
            # be zero also
            model.AddBoolOr(*cells3_vars, current_layer_cell_var.Not())

        current_layer_cells = expand(adjacency_dict, current_layer_cells)

    # wrapping up
    columns: dict[tuple[int, int], set[IntVar]] = dict()
    for (r, c, _l), var in volume_vars_dict.items():
        curr_set = columns.setdefault((r, c), {var})
        curr_set.add(var)
    for (r, c), variables in columns.items():
        if exact:
            # at most 1 per column
            model.Add(sum(variables) <= 1)

        summary_var = region_vars_dict[(r, c)]
        # at least 1 in column <= summary_var
        model.AddBoolOr(variables).OnlyEnforceIf(summary_var)
        # !summary_var => none in the column (all zero)
        model.AddBoolAnd([var.Not() for var in variables]
                         ).OnlyEnforceIf(summary_var.Not())

    # dead columns (happens if the grid is not fully connected, because the cells cannot expand to the part of
    # the grid that's not connected)
    flat_volume = set((r, c) for r, c, _ in volume_vars_dict.keys())
    dead = base - flat_volume
    for x in dead:
        summary_var = region_vars_dict[x]
        model.Add(summary_var == 0)


def expand2(adjacency_vars_dict: AdjacencyVarsDict, cells: Iterable[tuple[int, int]]):
    cells2 = set(cells)
    for c in cells:
        edges = adjacency_vars_dict[c]
        cells3 = set(edges.keys())
        cells2 |= cells3
    return cells2


def orthogonally_connected_region_adjacency_vars_csp(model: cp_model.CpModel, adjacency_dict: AdjacencyVarsDict,
                                                     region_vars_dict: GridVars, region_max_size: int,
                                                     seed: list[tuple[int, int]] | None = None):
    """
    Given a grid of bool vars (region), and an adjacency variables dictionary,
    all the 1's in the grid must be orthogonally connected.

    :param model:
    :param adjacency_dict:
    :param region_vars_dict:
    :param region_max_size:
    :param seed:
    :return:
    """
    # volume: set[tuple[int, int, int]] = set()

    exact: bool = False
    # (r, c, depth)
    volume_vars_dict: dict[tuple[int, int, int], IntVar] = dict()
    base = set(adjacency_dict.keys()) & set(region_vars_dict.keys())
    prefix = f"orthogonally_connected_region_adjacency_vars"

    all_region_vars = list(region_vars_dict.values())

    current_layer_cells: set[tuple[int, int]] = base
    if seed is not None:
        current_layer_cells = set(seed)

    for layer in range(region_max_size):
        cells2 = [(row, col, layer) for row, col in current_layer_cells]
        # volume |= set(cells2)
        for r, c, l in cells2:
            volume_vars_dict[(r, c, l)] = model.NewBoolVar(
                f"{prefix} - floodfill_volume: ({r},{c},{l})")

        # at layer 0 only 1 variable can be 1 (the seed)
        # if exact => only one cell can be 1 per layer (and its only 1 at most once per column)
        if layer == 0 or exact:
            enforce_layer_sum_bool = are_any_true_csp(
                model, all_region_vars, f"{prefix} - enforce_layer_sum_bool")
            layer_vars = [volume_vars_dict[coords] for coords in cells2]
            model.Add(sum(layer_vars) == 1).OnlyEnforceIf(
                enforce_layer_sum_bool)
        if layer == 0:
            # make sure that when starting floodfill,
            # the starting cell is the first that belongs to the region.
            # This ensures a unique solution to the floodfill problem,
            # otherwise there would be a a solution for each cell in the region,
            # assuming the region is orthogonally connected
            seed_cells = [(r, c) for r, c, _ in cells2]
            seed_cells.sort(key=lambda cell: cell[1])
            seed_cells.sort(key=lambda cell: cell[0])
            layer_0_summary_vars = [
                region_vars_dict[(r, c)] for r, c in seed_cells]
            layer_0_vars = [volume_vars_dict[(r, c, 0)] for r, c in seed_cells]
            bools = only_first_of_bools(
                model, layer_0_summary_vars, f"{prefix}")
            for i, layer_0_var in enumerate(layer_0_vars):
                model.Add(bools[i] == layer_0_var)

        # growth rules
        prev_layer = (layer - 1) % region_max_size
        for r, c in current_layer_cells:
            cell_and_adjacent = expand2(adjacency_dict, [(r, c)])
            current_layer_cell_var = volume_vars_dict[(r, c, layer)]
            if layer == 0:
                continue

            if exact:
                cell_and_adjacent.discard((r, c))
                previous_layers = [_l for _l in range(layer)]
                prev_layer_cell_and_adj = set((_r, _c, _l) for (_r, _c), _l
                                              in product(cell_and_adjacent, previous_layers))
            else:
                # if a cell is 1 in the previous layer then it is also 1 in the current one
                prev_layer_cell_var = volume_vars_dict.get((r, c, prev_layer))
                if prev_layer_cell_var is not None:
                    model.Add(current_layer_cell_var == 1).OnlyEnforceIf(
                        prev_layer_cell_var)
                prev_layer_cell_and_adj = set(
                    (_r, _c, prev_layer) for _r, _c in cell_and_adjacent)

            prev_layer_cell_and_adj &= set(volume_vars_dict.keys())
            cells3_vars = [volume_vars_dict[coords]
                           for coords in prev_layer_cell_and_adj]

            if not exact:
                prev_layer_cell_var = volume_vars_dict.get((r, c, prev_layer))
                if prev_layer_cell_var is None:
                    raise Exception('Something went wrong')

                edges_dict = adjacency_dict.get((r, c))
                if edges_dict is None:
                    model.Add(current_layer_cell_var == 0)
                else:
                    adj_nodes = list(edges_dict.keys())
                    bools: list[IntVar] = []
                    for _r, _c in adj_nodes:
                        prev_layer_adj_cell_var = volume_vars_dict.get(
                            (_r, _c, prev_layer))
                        edge_var = edges_dict.get((_r, _c))
                        if edge_var is None or prev_layer_adj_cell_var is None:
                            continue
                        bool_aux = model.NewBoolVar(
                            f"{prefix} - ({r},{c},{layer}) connects to ({_r},{_c},{prev_layer}) bool")
                        model.AddBoolAnd(prev_layer_adj_cell_var,
                                         edge_var).OnlyEnforceIf(bool_aux)
                        model.AddBoolOr(prev_layer_adj_cell_var.Not(
                        ), edge_var.Not()).OnlyEnforceIf(bool_aux.Not())
                        bools.append(bool_aux)
                    model.AddBoolOr(
                        *bools, prev_layer_cell_var).OnlyEnforceIf(current_layer_cell_var)
                    model.AddBoolAnd(*[b.Not() for b in bools], prev_layer_cell_var.Not()).OnlyEnforceIf(
                        current_layer_cell_var.Not())

            # if the cell and adjacent in the previous layer are all zero, then the cell in the current layer must
            # be zero also
            model.AddBoolOr(*cells3_vars, current_layer_cell_var.Not())

        current_layer_cells = expand2(adjacency_dict, current_layer_cells)

    # wrapping up
    columns: dict[tuple[int, int], set[IntVar]] = dict()
    for (r, c, _l), var in volume_vars_dict.items():
        curr_set = columns.setdefault((r, c), {var})
        curr_set.add(var)
    for (r, c), variables in columns.items():
        if exact:
            # at most 1 per column
            model.Add(sum(variables) <= 1)

        summary_var = region_vars_dict[(r, c)]
        # at least 1 in column <= summary_var
        model.AddBoolOr(variables).OnlyEnforceIf(summary_var)
        # !summary_var => none in the column (all zero)
        model.AddBoolAnd([var.Not() for var in variables]
                         ).OnlyEnforceIf(summary_var.Not())

    # dead columns (happens if the grid is not fully connected, because the cells cannot expand to the part of
    # the grid that's not connected)
    flat_volume = set((r, c) for r, c, _ in volume_vars_dict.keys())
    dead = base - flat_volume
    for x in dead:
        summary_var = region_vars_dict[x]
        model.Add(summary_var == 0)

# endregion Orthogonally Connected Regions --------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #
