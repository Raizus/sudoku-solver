from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, bool_vars_grid_dict_from_puzzle_grid, \
    exactly_n_per_row_col_region, get_masked_vars_grid_dict, cells2vars, one_of_each_digit, cell2var, \
    int_vars_grid_dict_from_puzzle_grid
from puzzlesolver.Puzzle2model.custom_constraints import index_of_first_bools_csp

"""
    Includes function to create value modifier constraints, 
    like Doublers, Hot and Cold cells, Vampyre and Prey, etc
"""


def force_set_vampires_prey_constraint(model: PuzzleModel, puzzle: Puzzle):
    """
    There are 9 Vampire cells contained within the grid which are a set of the digits from 1-to-9.
    Each row, column and box contains exactly one Vampire cell.
    9 Prey cells in the grid follow the same rules as the Vampire cells. A cell may have only one of these roles.

    :param model:
    :param grid_vars_dict:
    :param puzzle:
    :return:
    """
    grid = puzzle.grid
    all_cells = grid.getAllCells()

    grid_vars_dict = model.grid_vars_dict
    cells_grid_vars = grid_vars_dict['cells_grid_vars']

    prefix = f"vampires_prey"
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    # create vampire and prey cells bool grid, var == 1 if marked cell, else var == 0
    vampire_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"vampire_bools_grid")
    prey_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"prey_bools_grid")

    # one vampire / prey cell per col, row and region
    exactly_n_per_row_col_region(model, grid, vampire_bools_grid, 1)
    exactly_n_per_row_col_region(model, grid, prey_bools_grid, 1)

    # grid with the marked digits: if digit is multiplied then var == digit, else var = min_digit - 1
    vampire_digits_grid: GridVars = \
        get_masked_vars_grid_dict(model, puzzle.valid_digits, grid, vampire_bools_grid, cells_grid_vars,
                                  f"vampire_digits_grid")
    prey_digits_grid: GridVars = \
        get_masked_vars_grid_dict(model, puzzle.valid_digits, grid, prey_bools_grid, cells_grid_vars,
                                  f"prey_digits_grid")

    # One of each digit is a vampire cell
    # One of each digit is a prey cell
    all_vampire_digits_vars = cells2vars(vampire_digits_grid, all_cells)
    one_of_each_digit(model, puzzle.valid_digits,
                      all_vampire_digits_vars, prefix)

    all_prey_digits_vars = cells2vars(prey_digits_grid, all_cells)
    one_of_each_digit(model, puzzle.valid_digits, all_prey_digits_vars, prefix)

    # cells cannot be both vampire and prey
    for cell in all_cells:
        vampire_bool = cell2var(vampire_bools_grid, cell)
        prey_bool = cell2var(prey_bools_grid, cell)
        model.Add(sum([vampire_bool, prey_bool]) <= 1)

    # values after vampires and preys (assuming regions are known)
    vampire_prey_values_grid = int_vars_grid_dict_from_puzzle_grid(model, grid, 0, 2 * max_digit,
                                                                   f"vampire_prey_values_grid")
    for region in grid.getUsedRegions():
        region_cells = grid.getRegionCells(region)
        cells_vars = cells2vars(cells_grid_vars, region_cells)
        prey_vars = cells2vars(prey_bools_grid, region_cells)
        prey_var = model.NewIntVar(
            min_digit, max_digit, f"{prefix} - region_{region} prey_var")
        prey_idx_var = index_of_first_bools_csp(model, prey_vars)
        model.AddElement(prey_idx_var, cells_vars, prey_var)

        for cell in region_cells:
            cell_var = cell2var(cells_grid_vars, cell)
            vampire_bool = cell2var(vampire_bools_grid, cell)
            prey_bool = cell2var(prey_bools_grid, cell)
            vampire_prey_value_var = cell2var(vampire_prey_values_grid, cell)

            not_prey_or_vampire = model.NewBoolVar(
                f"{prefix} - {cell.format_cell()} - not_prey_or_vampire")
            model.AddBoolAnd(vampire_bool.Not(), prey_bool.Not()
                             ).OnlyEnforceIf(not_prey_or_vampire)
            model.AddBoolOr(vampire_bool, prey_bool).OnlyEnforceIf(
                not_prey_or_vampire.Not())

            model.Add(vampire_prey_value_var == 0).OnlyEnforceIf(prey_bool)
            model.Add(vampire_prey_value_var == cell_var).OnlyEnforceIf(
                not_prey_or_vampire)
            model.Add(vampire_prey_value_var == cell_var +
                      prey_var).OnlyEnforceIf(vampire_bool)

    grid_vars_dict["vampire_digits_grid"] = vampire_digits_grid
    grid_vars_dict["prey_digits_grid"] = prey_digits_grid
    grid_vars_dict["vampire_bools_grid"] = vampire_bools_grid
    grid_vars_dict["prey_bools_grid"] = prey_bools_grid
    grid_vars_dict["vampire_prey_values_grid"] = vampire_prey_values_grid

    return vampire_bools_grid, prey_bools_grid, vampire_prey_values_grid


def get_or_set_vampires_prey_constraint(model: PuzzleModel,
                                        puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "vampire_bools_grid" in grid_vars_dict and \
            "prey_bools_grid" in grid_vars_dict and \
            "vampire_prey_values_grid" in grid_vars_dict:
        return grid_vars_dict["vampire_bools_grid"], grid_vars_dict["prey_bools_grid"], \
            grid_vars_dict["vampire_prey_values_grid"]

    vampire_bools_grid, prey_bools_grid, vampire_prey_values_grid = \
        force_set_vampires_prey_constraint(model, puzzle)
    return vampire_bools_grid, prey_bools_grid, vampire_prey_values_grid


def set_fixed_multipliers_constraint(model: PuzzleModel,
                                     puzzle: Puzzle, multiplier: int):
    grid_vars_dict = model.grid_vars_dict
    grid = puzzle.grid
    all_cells = grid.getAllCells()
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    prefix = f"multipliers_{multiplier}"

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    # create multipliers bool grid, var == 1 if multiplier, else var == 0
    bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix} - bools_grid")
    exactly_n_per_row_col_region(model, grid, bools_grid)

    # grid with the multiplied digits: if digit is multiplied then var == digit, else var = min_digit - 1
    multiplied_values_grid: GridVars = \
        get_masked_vars_grid_dict(model, puzzle.valid_digits, grid, bools_grid, cells_grid_vars,
                                  f"{prefix} - multiplied_digits_grid")

    # One of each digit is a multiplier
    all_doubled_value_vars = cells2vars(multiplied_values_grid, all_cells)
    one_of_each_digit(model, puzzle.valid_digits,
                      all_doubled_value_vars, prefix)

    lb = min(1, multiplier)
    ub = max(1, multiplier)
    # this way we can use these variables as weights for each cell variable for doubler constraints
    multipliers_grid: GridVars = {}
    for cell in all_cells:
        multipliers_grid[(cell.row, cell.col)] = model.NewIntVar(lb, ub,
                                                                 f"{prefix} - multipliers_grid-{cell.format_cell()}")

    # If is multiplier, then multiplier_var == multiplier, else multiplier_var == 1
    for cell in all_cells:
        bool_var = cell2var(bools_grid, cell)
        multiplier_var = cell2var(multipliers_grid, cell)
        model.Add(multiplier_var == multiplier).OnlyEnforceIf(bool_var)
        model.Add(multiplier_var == 1).OnlyEnforceIf(bool_var.Not())

    lb = min(min_digit, min_digit*multiplier, max_digit, max_digit*multiplier)
    ub = max(min_digit, min_digit*multiplier, max_digit, max_digit*multiplier)

    fixed_multipliers_values_grid = \
        int_vars_grid_dict_from_puzzle_grid(
            model, grid, lb, ub, f"{prefix} - fixed_multipliers_values_grid")

    for cell in all_cells:
        cell_var = cell2var(cells_grid_vars, cell)
        value_var = cell2var(fixed_multipliers_values_grid, cell)
        multiplier_bool_var = cell2var(bools_grid, cell)
        model.Add(value_var == cell_var).OnlyEnforceIf(
            multiplier_bool_var.Not())
        model.Add(value_var == multiplier *
                  cell_var).OnlyEnforceIf(multiplier_bool_var)

    return multipliers_grid, bools_grid, multiplied_values_grid, fixed_multipliers_values_grid


def force_set_doublers_constraint(model: PuzzleModel,
                                  puzzle: Puzzle):
    doublers_grid, doublers_bool_grid, doubled_digits_grid, doubled_values_grid = \
        set_fixed_multipliers_constraint(model, puzzle, 2)

    grid_vars_dict = model.grid_vars_dict
    grid_vars_dict["doubled_digits_grid"] = doubled_digits_grid
    grid_vars_dict["doublers_grid"] = doublers_grid
    grid_vars_dict["doublers_bools_grid"] = doublers_bool_grid
    grid_vars_dict["doubled_values_grid"] = doubled_values_grid

    return doublers_bool_grid, doublers_grid


def get_or_set_doublers_grid(model: PuzzleModel,
                             puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict

    if "doublers_grid" in grid_vars_dict:
        return grid_vars_dict["doublers_bools_grid"], grid_vars_dict["doublers_grid"]

    doublers_bool_grid, doublers_grid = force_set_doublers_constraint(
        model, puzzle)
    return doublers_bool_grid, doublers_grid


def force_set_negators_constraints(model: PuzzleModel,
                                   puzzle: Puzzle):

    negators_grid, negators_bool_grid, negated_digits_grid, negated_values_grid = \
        set_fixed_multipliers_constraint(model, puzzle, -1)

    grid_vars_dict = model.grid_vars_dict
    grid_vars_dict["negated_values_grid"] = negated_digits_grid
    grid_vars_dict["negators_grid"] = negators_grid
    grid_vars_dict["negators_bools_grid"] = negators_bool_grid
    grid_vars_dict["negated_values_grid"] = negated_values_grid

    return negators_bool_grid, negators_grid


def get_or_set_negators_grid(model: PuzzleModel,
                             puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "negators_grid" in grid_vars_dict:
        return grid_vars_dict["negators_bools_grid"], grid_vars_dict["negators_grid"]

    negators_bool_grid, negators_grid = force_set_negators_constraints(
        model, puzzle)
    return negators_bool_grid, negators_grid


def _set_multipliers_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    all_cells = grid.getAllCells()
    grid_vars_dict = model.grid_vars_dict
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    prefix = f"multipliers"

    # create multipliers bool grid, var == 1 if multiplier, else var == 0
    multipliers_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix} - bools_grid")

    exactly_n_per_row_col_region(model, grid, multipliers_bools_grid)

    # grid with the multiplied digits: if digit is multiplied then var == digit, else var = min_digit - 1
    multiplied_values_grid: GridVars = \
        get_masked_vars_grid_dict(model, puzzle.valid_digits, grid, multipliers_bools_grid, cells_grid_vars,
                                  f"{prefix} - multiplied_values_grid")

    # One of each digit is a multiplier
    all_multiplied_value_vars = cells2vars(multiplied_values_grid, all_cells)
    one_of_each_digit(model, puzzle.valid_digits,
                      all_multiplied_value_vars, prefix)

    grid_vars_dict["multiplied_values_grid"] = multiplied_values_grid
    grid_vars_dict["multipliers_bools_grid"] = multipliers_bools_grid

    return multipliers_bools_grid, multiplied_values_grid


def get_or_set_multipliers_constraint(model: PuzzleModel,
                                      puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "multipliers_grid" in grid_vars_dict:
        return grid_vars_dict["multipliers_grid"]

    multipliers_bools_grid, _ = _set_multipliers_constraint(
        model, puzzle)
    return multipliers_bools_grid


def force_set_decrement_fountain_constraint(model: PuzzleModel,
                                            puzzle: Puzzle):
    grid = puzzle.grid
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)
    all_cells = grid.getAllCells()
    grid_vars_dict = model.grid_vars_dict
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    prefix = f"decrement_fountain"

    # create multipliers bool grid, var == 1 if multiplier, else var == 0
    fountain_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix} - bools_grid")
    exactly_n_per_row_col_region(model, grid, fountain_bools_grid)

    # grid with the fountain digits: if digit is fountain then var == digit, else var = min_digit - 1
    decrement_fountain_digits: GridVars = \
        get_masked_vars_grid_dict(model, puzzle.valid_digits, grid, fountain_bools_grid, cells_grid_vars,
                                  f"{prefix} - digits_grid")

    # One of each digit is a decrement fountain
    all_decrement_fountain_value_vars = cells2vars(
        decrement_fountain_digits, all_cells)
    one_of_each_digit(model, puzzle.valid_digits,
                      all_decrement_fountain_value_vars, prefix)

    decrement_fountain_values_grid = \
        int_vars_grid_dict_from_puzzle_grid(
            model, grid, -9, 0, f"{prefix} - values_grid")

    for cell in all_cells:
        neighbour_cells = grid.getNeighbourCells(cell)
        fountain_bool_vars = cells2vars(fountain_bools_grid, neighbour_cells)
        value_var = cell2var(decrement_fountain_values_grid, cell)
        model.Add(-sum(fountain_bool_vars) == value_var)

    name = f"{prefix} - after_decrement_fountain_values_grid"
    after_decrement_fountain_values_grid = \
        int_vars_grid_dict_from_puzzle_grid(
            model, grid, min_digit - 9, max_digit, name)

    for cell in all_cells:
        cell_var = cell2var(cells_grid_vars, cell)
        value_after_fountain_var = cell2var(
            after_decrement_fountain_values_grid, cell)
        fountain_value_var = cell2var(decrement_fountain_values_grid, cell)
        model.Add(value_after_fountain_var == cell_var + fountain_value_var)

    grid_vars_dict['decrement_fountain_bools_grid'] = fountain_bools_grid
    grid_vars_dict['decrement_fountain_values_grid'] = decrement_fountain_values_grid
    grid_vars_dict['after_decrement_fountain_values_grid'] = after_decrement_fountain_values_grid

    return fountain_bools_grid, decrement_fountain_values_grid


def get_or_set_decrement_fountain_constraint(model: PuzzleModel,
                                             puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "decrement_fountain_bools_grid" in grid_vars_dict:
        return grid_vars_dict["decrement_fountain_bools_grid"]

    fountain_bools_grid, _ = \
        force_set_decrement_fountain_constraint(model, puzzle)
    return fountain_bools_grid


def set_fixed_adder_cells_constraint(model: PuzzleModel,
                                     puzzle: Puzzle,
                                     constant: int):
    """
    There are 9 Adder cells contained within the grid comprised of a set of the digits 1-to-9.
    Each row, column and box contains exactly one Adder cell.
    Adder cells increase the value of the contained digit by CONSTANT (can be negative too).
    """

    grid = puzzle.grid
    all_cells = grid.getAllCells()
    grid_vars_dict = model.grid_vars_dict
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    prefix = f"adders_{constant}"

    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    # create multipliers bool grid, var == 1 if adder, else var == 0
    bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"{prefix} - bools_grid")
    exactly_n_per_row_col_region(model, grid, bools_grid)

    # grid with the multiplied digits: if digit is multiplied then var == digit, else var = min_digit - 1
    adder_digits_grid: GridVars = \
        get_masked_vars_grid_dict(model, puzzle.valid_digits, grid, bools_grid, cells_grid_vars,
                                  f"{prefix} - adder_digits_grid")

    # One of each digit is a multiplier
    all_adder_digit_vars = cells2vars(adder_digits_grid, all_cells)
    one_of_each_digit(model, puzzle.valid_digits, all_adder_digit_vars, prefix)

    lb = min(0, constant)
    ub = max(0, constant)
    # this way we can use these variables as weights for each cell variable for doubler constraints
    adders_grid = int_vars_grid_dict_from_puzzle_grid(
        model, grid, lb, ub, f"{prefix} - adders_grid")

    # If is adder, then adder_var == constant, else adder_var == 0
    for cell in all_cells:
        bool_var = cell2var(bools_grid, cell)
        adder_var = cell2var(adders_grid, cell)
        model.Add(adder_var == constant).OnlyEnforceIf(bool_var)
        model.Add(adder_var == 0).OnlyEnforceIf(bool_var.Not())

    ub = max(min_digit, min_digit+constant, max_digit, max_digit+constant)
    lb = min(min_digit, min_digit+constant, max_digit, max_digit+constant)

    fixed_adders_values_grid = \
        int_vars_grid_dict_from_puzzle_grid(
            model, grid, lb, ub, f"{prefix} - fixed_adders_values_grid")

    for cell in all_cells:
        cell_var = cell2var(cells_grid_vars, cell)
        value_var = cell2var(fixed_adders_values_grid, cell)
        adder_bool_var = cell2var(bools_grid, cell)
        model.Add(value_var == cell_var).OnlyEnforceIf(adder_bool_var.Not())
        model.Add(value_var == cell_var +
                  constant).OnlyEnforceIf(adder_bool_var)

    return adders_grid, bools_grid, adder_digits_grid, fixed_adders_values_grid


def force_set_hot_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    hot_cells_grid, hot_cells_bool_grid, hot_cells_digits_grid, hot_cells_values_grid = \
        set_fixed_adder_cells_constraint(model, puzzle, 1)

    grid_vars_dict = model.grid_vars_dict
    grid_vars_dict["hot_cells_grid"] = hot_cells_grid
    grid_vars_dict["hot_cells_bool_grid"] = hot_cells_bool_grid
    grid_vars_dict["hot_cells_digits_grid"] = hot_cells_digits_grid
    grid_vars_dict["hot_cells_values_grid"] = hot_cells_values_grid

    return hot_cells_grid


def get_or_set_hot_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "hot_cells_grid" in grid_vars_dict:
        return grid_vars_dict["hot_cells_grid"]

    hot_cells_grid = force_set_hot_cells_constraint(model, puzzle)
    return hot_cells_grid


def force_set_cold_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    cold_cells_grid, cold_cells_bool_grid, cold_cells_digits_grid, cold_cells_values_grid = \
        set_fixed_adder_cells_constraint(model, puzzle, -1)

    grid_vars_dict = model.grid_vars_dict
    grid_vars_dict["cold_cells_grid"] = cold_cells_grid
    grid_vars_dict["cold_cells_bool_grid"] = cold_cells_bool_grid
    grid_vars_dict["cold_cells_digits_grid"] = cold_cells_digits_grid
    grid_vars_dict["cold_cells_values_grid"] = cold_cells_values_grid

    return cold_cells_grid


def get_or_set_cold_cells_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "cold_cells_grid" in grid_vars_dict:
        return grid_vars_dict["cold_cells_grid"]

    cold_cells_grid = force_set_cold_cells_constraint(model, puzzle)
    return cold_cells_grid
