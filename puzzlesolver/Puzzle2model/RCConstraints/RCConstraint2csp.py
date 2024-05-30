from itertools import combinations
from typing import List
from ortools.sat.python.cp_model import IntVar
from ortools.sat.python import cp_model

from puzzlesolver.Puzzle.ConstraintEnums import LocalConstraintsModifiersE, RCConstraintsE

from puzzlesolver.Puzzle.Directions import RCToDirectionDict, get_opposite_direction, DIRECTIONS, getCardinalDirections
from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OtherConstraints.BattlestarConstraints2csp import get_or_set_battlestar_constraint
from puzzlesolver.Puzzle2model.OtherConstraints.CenterCellsLoopConstraints2csp import get_or_set_cell_center_loop_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.RCConstraints.utils import genRCConstraintProperties
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars, edge_from_cells, int_vars_grid_dict_from_puzzle_grid, orthogonally_connected_region_csp
from puzzlesolver.Puzzle2model.puzzle_model_types import AdjacencyDict, AdjacencyVarsDict, GridVars
from puzzlesolver.Puzzle2model.custom_constraints import are_all_equal_csp, are_all_true_csp, masked_count_vars, masked_sum_csp


def set_digits_do_not_repeat_in_galaxy(model: PuzzleModel, puzzle: Puzzle):
    # cells in the same galaxy have different values
    digits_do_not_repeat_galaxy = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.DIGITS_DO_NOT_REPEAT_WITHIN_A_GALAXY, False)
    if not digits_do_not_repeat_galaxy:
        return

    key = RCConstraintsE.ROTATIONALLY_SYMMETRIC_GALAXY
    prefix = f"{key.value}"

    grid_vars_dict = model.grid_vars_dict
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    galaxies_grid = grid_vars_dict["galaxies_grid"]
    all_cells = puzzle.grid.getAllCells()

    same_region_dict: dict[tuple[tuple[int, int],
                                 tuple[int, int]], IntVar] = dict()
    for cell1, cell2 in combinations(all_cells, 2):
        cell1_var = cell2var(cells_grid_vars, cell1)
        cell2_var = cell2var(cells_grid_vars, cell2)
        cell1_galaxy_var = cell2var(galaxies_grid, cell1)
        cell2_galaxy_var = cell2var(galaxies_grid, cell2)

        name = f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()}, is_same_galaxy_bool"
        same_region_bool = are_all_equal_csp(
            model, [cell1_galaxy_var, cell2_galaxy_var], name)

        model.Add(cell1_var != cell2_var).OnlyEnforceIf(same_region_bool)
        same_region_dict[((cell1.row, cell1.col),
                          (cell2.row, cell2.col))] = same_region_bool
        same_region_dict[((cell2.row, cell2.col),
                          (cell1.row, cell1.col))] = same_region_bool


def set_every_galaxy_contains_one_star(model: PuzzleModel, puzzle: Puzzle):
    # one star per galaxy
    key2 = LocalConstraintsModifiersE.EVERY_GALAXY_CONTAINS_ONE_STAR
    one_star_per_galaxy = puzzle.bool_constraints.get(key2, False)
    if not one_star_per_galaxy:
        return

    key = RCConstraintsE.ROTATIONALLY_SYMMETRIC_GALAXY
    constraints_list = puzzle.tool_constraints.get(key)
    num_galaxies = len(constraints_list)

    grid_vars_dict = model.grid_vars_dict
    all_cells = puzzle.grid.getAllCells()

    stars_bools_grid = get_or_set_battlestar_constraint(model, puzzle)
    all_star_vars = cells2vars(stars_bools_grid, all_cells)

    for galaxy in range(num_galaxies):
        galaxy_i_bools_grid = grid_vars_dict[f"galaxy_{galaxy}_bools_grid"]
        all_galaxy_bools = cells2vars(galaxy_i_bools_grid, all_cells)
        name = f"{key2.value} - galaxy_{galaxy} - star_count"
        star_count = masked_count_vars(model, all_star_vars,
                                       all_galaxy_bools, 1, name)
        model.Add(star_count == 1)


def set_rotationally_symmetric_galaxy_constraints(model: PuzzleModel, puzzle: Puzzle):
    key = RCConstraintsE.ROTATIONALLY_SYMMETRIC_GALAXY
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    grid_vars_dict = model.grid_vars_dict
    all_cells = grid.getAllCells()

    num_galaxies = len(constraints_list)
    galaxies_grid = int_vars_grid_dict_from_puzzle_grid(
        model, grid, -1, num_galaxies - 1, prefix)
    grid_vars_dict["galaxies_grid"] = galaxies_grid

    for i, (coords, _) in enumerate(genRCConstraintProperties(puzzle, key)):
        r, c = coords.r, coords.c
        cells: list[Cell] = []
        mapped_cells: list[Cell] = []
        cells_not_in_galaxy: list[Cell] = []
        for cell in all_cells:
            mapped_cell = grid.getCell180RotSymmetry(cell, r, c)
            if mapped_cell and mapped_cell not in cells:
                cells.append(cell)
                mapped_cells.append(mapped_cell)
            elif cell not in mapped_cells:
                cells_not_in_galaxy.append(cell)

        cells_maybe_in_galaxy = list(set(cells) | set(mapped_cells))
        galaxy_i_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
            model, grid, f"galaxy_{i}_bools_grid")
        # galaxy_i_bools_grid = bool_vars_grid_dict_from_cells(model, cells_maybe_in_galaxy, f"galaxy_{i}_bools_grid")
        grid_vars_dict[f"galaxy_{i}_bools_grid"] = galaxy_i_bools_grid

        # symmetry implies that if a cell belongs to a galaxy, then the mapped cell also belongs to the same galaxy
        # equally if a cell does not belong to a galaxy, then the mapped cell also does NOT belong to the same galaxy
        bools: list[IntVar] = []
        for cell1, cell2 in zip(cells, mapped_cells):
            cell1_galaxy_bool_var = cell2var(galaxy_i_bools_grid, cell1)
            cell2_galaxy_bool_var = cell2var(galaxy_i_bools_grid, cell2)
            bools.extend([cell1_galaxy_bool_var, cell2_galaxy_bool_var])
            cell1_galaxy_var = cell2var(galaxies_grid, cell1)
            cell2_galaxy_var = cell2var(galaxies_grid, cell2)
            model.Add(cell1_galaxy_bool_var == cell2_galaxy_bool_var)

            model.Add(cell1_galaxy_var == i).OnlyEnforceIf(
                cell1_galaxy_bool_var)
            model.Add(cell2_galaxy_var == i).OnlyEnforceIf(
                cell2_galaxy_bool_var)
            model.Add(cell1_galaxy_var != i).OnlyEnforceIf(
                cell1_galaxy_bool_var.Not())
            model.Add(cell2_galaxy_var != i).OnlyEnforceIf(
                cell2_galaxy_bool_var.Not())
        model.Add(sum(bools) > 0)

        for cell in cells_not_in_galaxy:
            cell_galaxy_var = cell2var(galaxies_grid, cell)
            cell_galaxy_bool_var = cell2var(galaxy_i_bools_grid, cell)
            model.Add(cell_galaxy_bool_var == 0)
            model.Add(cell_galaxy_var != i)

        # galaxies must be orthogonally connected
        seed: list[tuple[int, int]] = [(cell.row, cell.col) for cell in cells]
        adjacency_dict: AdjacencyDict = dict()
        for cell in cells_maybe_in_galaxy:
            adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
            adjacent_cells = [
                _cell for _cell in adjacent_cells if _cell in cells_maybe_in_galaxy]
            adjacency_coords = [(_cell.row, _cell.col)
                                for _cell in adjacent_cells]
            adjacency_dict[(cell.row, cell.col)] = set(adjacency_coords)

        orthogonally_connected_region_csp(
            model, adjacency_dict, galaxy_i_bools_grid, len(cells_maybe_in_galaxy), seed)

    # all cells must belong to a galaxy
    each_cell_belongs_to_a_galaxy = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.EACH_CELL_BELONGS_TO_A_GALAXY, False)
    if each_cell_belongs_to_a_galaxy:
        for cell in all_cells:
            cell_galaxy_var = cell2var(galaxies_grid, cell)
            model.Add(cell_galaxy_var != -1)

    # cells in the same galaxy have different values
    set_digits_do_not_repeat_in_galaxy(model, puzzle)

    # one star per galaxy
    set_every_galaxy_contains_one_star(model, puzzle)


def connect_nodes_bools(model: cp_model.CpModel, cells: list[Cell], bools_grid_dict: GridVars,
                        edges_dict: AdjacencyVarsDict, prefix: str) -> List[IntVar]:
    bools: list[IntVar] = []
    if len(cells) == 0:
        return bools

    prefix = f"{prefix} - connect_nodes_bools"
    bool_var = cell2var(bools_grid_dict, cells[0])
    bools.append(bool_var)

    for i, (cell1, cell2) in enumerate(zip(cells, cells[1:]), 1):
        edge_var = edge_from_cells(edges_dict, cell1, cell2)
        prev_bool_var = bools[i-1]
        bool_var = model.NewBoolVar(
            f"{prefix} - {cell1.format_cell()} connects to {cell2.format_cell()}")
        if edge_var is not None:
            model.AddBoolAnd(prev_bool_var, edge_var).OnlyEnforceIf(bool_var)
            model.AddBoolOr(prev_bool_var.Not(), edge_var.Not()
                            ).OnlyEnforceIf(bool_var.Not())
        else:
            model.Add(bool_var == 0)
        bools.append(bool_var)
    return bools


def loop_cell_uninterrupted_sum(model: PuzzleModel, puzzle: Puzzle, cells: list[Cell], prefix: str):
    loop_bools_grid, loop_edges_dict = get_or_set_cell_center_loop_constraint(
        model, puzzle)
    cells_grid_vars = model.grid_vars_dict['cells_grid_vars']

    bools = connect_nodes_bools(model, cells, loop_bools_grid, loop_edges_dict,
                                f"{prefix}")
    cells1_vars = cells2vars(cells_grid_vars, cells)

    max_digit = max(puzzle.valid_digits)
    lb = 0
    ub = max_digit*len(cells)

    sum_var = model.NewIntVar(lb, ub, f"{prefix} - sum_var")
    masked_sum = masked_sum_csp(
        model, cells1_vars, bools, f"{prefix} - sum_var")
    model.Add(sum_var == masked_sum)

    return sum_var


def all_balanced_loop_cell_or_border_given(model: PuzzleModel, puzzle: Puzzle):
    key = RCConstraintsE.BALANCED_LOOP_CELL_OR_BORDER
    key2 = LocalConstraintsModifiersE.ALL_BALANCED_LOOP_CELL_OR_BORDER_GIVEN
    all_dots_given = puzzle.bool_constraints.get(key2, False)
    prefix = f"{key.value} - all_dots_given"

    all_dots_given = True
    if not all_dots_given:
        return

    given_dots = [(coords.r, coords.c) for (
        coords, _) in genRCConstraintProperties(puzzle, key)]

    _, loop_edges_dict = get_or_set_cell_center_loop_constraint(
        model, puzzle)

    grid = puzzle.grid
    directions = getCardinalDirections()
    all_cells = grid.getAllCells()

    # cell centers
    for cell in all_cells:
        node = (cell.row + 0.5, cell.col + 0.5)
        if node in given_dots:
            continue

        sum_vars: List[IntVar] = []
        consider_sums: List[IntVar] = []
        considered_directions: List[DIRECTIONS] = []

        for direction in directions:
            cells_in_direction = grid.getCellsInDirection(cell, direction)
            cells1 = [cell] + cells_in_direction

            if not len(cells_in_direction):
                continue

            edge_var = edge_from_cells(
                loop_edges_dict, cell, cells_in_direction[0])
            if edge_var is None:
                continue

            sum_var_i = loop_cell_uninterrupted_sum(
                model, puzzle, cells1, f"{prefix} - {cell.format_cell()} {direction.value}")

            sum_vars.append(sum_var_i)
            consider_sums.append(edge_var)
            considered_directions.append(direction)

        for group in combinations(zip(considered_directions, sum_vars, consider_sums), 2):
            dir1, sum1, consider1 = group[0]
            dir2, sum2, consider2 = group[1]
            name = f"{prefix} - consider_both, {cell.format_cell()} {dir1.value}, {dir2.value}"
            consider_both = are_all_true_csp(
                model, [consider1, consider2], name)

            # TODO some very weird bug below
            model.Add(sum1 != sum2).OnlyEnforceIf(consider_both)

    # TODO finish this for cell edges


def set_balanced_loop_cell_or_border_constraints(model: PuzzleModel, puzzle: Puzzle):

    key = RCConstraintsE.BALANCED_LOOP_CELL_OR_BORDER
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid = puzzle.grid

    max_digit = max(puzzle.valid_digits)
    max_n_rows_n_cols = max(grid.nRows, grid.nCols)

    loop_bools_grid, loop_edges_dict = get_or_set_cell_center_loop_constraint(
        model, puzzle)

    for i, (coords, _) in enumerate(genRCConstraintProperties(puzzle, key)):
        r, c = coords.r, coords.c

        cells = grid.getAdjacentToRC(r, c)
        loop_cells_vars = cells2vars(loop_bools_grid, cells)
        if len(cells) not in [1, 2]:
            continue

        for var in loop_cells_vars:
            model.Add(var == 1)

        # dot is on a cell border: both cells on the border belong to the loop
        if len(cells) == 2:
            cell1 = cells[0]
            cell2 = cells[1]
            edge_var_12 = edge_from_cells(loop_edges_dict, cell1, cell2)
            edge_var_21 = edge_from_cells(loop_edges_dict, cell2, cell1)
            if edge_var_12 is not None:
                model.Add(edge_var_12 == 1)
            if edge_var_21 is not None:
                model.Add(edge_var_21 == 1)

            # sum of segments on both sides untill the loop turns is the same
            # cell1 -> cell2
            dr = cell2.row - cell1.row
            dc = cell2.col - cell1.col

            prefix2 = f"{prefix} {i} - ({r}, {c})"

            direction = RCToDirectionDict[(dr, dc)]
            cells1 = grid.getCellsInDirection(cell1, direction)

            sum_var1 = loop_cell_uninterrupted_sum(
                model, puzzle, cells1, f"{prefix2}, {direction.value}")

            opposite_dir = get_opposite_direction(direction)
            cells2 = grid.getCellsInDirection(cell2, opposite_dir)

            sum_var2 = loop_cell_uninterrupted_sum(
                model, puzzle, cells2, f"{prefix2}, {opposite_dir.value}")

            model.Add(sum_var1 == sum_var2)

        # dot is on a cell center
        if len(cells) == 1:
            cell = cells[0]
            directions = getCardinalDirections()
            sum_var = model.NewIntVar(0, max_digit * (max_n_rows_n_cols - 1),
                                      f"{prefix} {i} - {cell.format_cell()} sum_var")
            for direction in directions:
                prefix2 = f"{prefix} {i} - ({r}, {c}) {direction.value}"
                cells_in_direction = grid.getCellsInDirection(cell, direction)
                cells1 = [cell] + cells_in_direction

                if not len(cells_in_direction):
                    continue

                edge_var = edge_from_cells(
                    loop_edges_dict, cell, cells_in_direction[0])
                if edge_var is None:
                    continue

                sum_var_i = loop_cell_uninterrupted_sum(
                    model, puzzle, cells1, f"{prefix2}")

                model.Add(sum_var == sum_var_i).OnlyEnforceIf(edge_var)

    # all_dots_given = puzzle.bool_constraints.get(
    #     BoolConstraints.ALL_BALANCED_LOOP_CELL_OR_BORDER_GIVEN, False)

    all_dots_given = True
    if not all_dots_given:
        return

    given_dots = [(coords.r, coords.c) for (
        coords, _) in genRCConstraintProperties(puzzle, key)]

    # cell centers
    directions = getCardinalDirections()
    all_cells = grid.getAllCells()

    prefix2 = f"{prefix} - all_dots_given"
    for cell in all_cells:
        node = (cell.row + 0.5, cell.col + 0.5)
        if node in given_dots:
            continue

        sum_vars: List[IntVar] = []
        consider_sums: List[IntVar] = []
        considered_directions: List[DIRECTIONS] = []

        for direction in directions:
            cells_in_direction = grid.getCellsInDirection(cell, direction)
            cells1 = [cell] + cells_in_direction

            if not len(cells_in_direction):
                continue

            edge_var = edge_from_cells(
                loop_edges_dict, cell, cells_in_direction[0])
            if edge_var is None:
                continue

            sum_var_i = loop_cell_uninterrupted_sum(
                model, puzzle, cells1, f"{prefix2} - {cell.format_cell()} {direction.value}")

            sum_vars.append(sum_var_i)
            consider_sums.append(edge_var)
            considered_directions.append(direction)

        for group in combinations(zip(considered_directions, sum_vars, consider_sums), 2):
            dir1, sum1, consider1 = group[0]
            dir2, sum2, consider2 = group[1]
            name = f"{prefix2} - consider_both, {cell.format_cell()} {dir1.value}, {dir2.value}"
            consider_both = are_all_true_csp(
                model, [consider1, consider2], name)

            # TODO some very weird bug below
            model.Add(sum1 != sum2).OnlyEnforceIf(consider_both)


def set_rc_constraints(model: PuzzleModel, puzzle: Puzzle):
    set_balanced_loop_cell_or_border_constraints(model, puzzle)
    set_rotationally_symmetric_galaxy_constraints(model, puzzle)
