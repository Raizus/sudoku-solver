

from itertools import combinations
from puzzlesolver.Puzzle.Cell import Cell, are_cells_orthogonally_connected
from puzzlesolver.Puzzle.ConstraintEnums import CageConstraintsE, GlobalRegionConstraintsE, LineConstraintsE, LocalConstraintsModifiersE
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.CageConstraints.utils import genCageConstraintProperties, genConstraint
from puzzlesolver.Puzzle2model.LineConstraints.utils import genLineConstraintProperties
from puzzlesolver.Puzzle2model.OtherConstraints.NorinoriColouringConstraints2csp import get_or_set_norinori_colouring_constraint
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from ortools.sat.python.cp_model import IntVar
from ortools.sat.python import cp_model

from puzzlesolver.Puzzle2model.custom_constraints import all_equal, are_all_true_csp, masked_sum_csp, consecutive_csp, count_vars, distance_csp, is_even_csp, is_member_of, member_of, palindrome_csp, renban_csp
from puzzlesolver.Puzzle2model.puzzle_csp_utils import PRIME_LIST, GridVars, bool_vars_grid_dict_from_puzzle_grid, cell2var, cells2vars, int_vars_grid_dict_from_puzzle_grid
from puzzlesolver.utils.ParsingUtils import look_and_say_parse_string, parse_int


def are_cages_adjacent(cage1: list[Cell], cage2: list[Cell]) -> bool:
    # if they overlap, they're not adjacent
    if any(cell1 == cell2 for cell1 in cage1 for cell2 in cage2):
        return False

    if any(are_cells_orthogonally_connected(cell1, cell2) for cell1 in cage1 for cell2 in cage2):
        return True
    return False


def set_vaulted_cages(model: PuzzleModel, puzzle: Puzzle, key: CageConstraintsE):
    """
    Digits in a cage may not appear in any cell orthogonally adjacent to that cage.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
        key (CageConstraintsE): 
    """
    key2 = LocalConstraintsModifiersE.VAULTED_KILLER_CAGES
    prefix = f"{key2.value}"
    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    vaulted = puzzle.bool_constraints.get(key2, False)
    if vaulted:
        for i, (cells, cells_vars, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
            orth_cells: set[Cell] = set()
            for cell in cells:
                adj_cells = grid.getOrthogonallyAdjacentCells(cell)
                orth_cells.update(adj_cells)
            orth_cells_list = list(orth_cells.difference(cells))

            orth_cells_vars = cells2vars(grid_vars, orth_cells_list)

            for cell_var in orth_cells_vars:
                bool_var = is_member_of(
                    model, cells_vars, cell_var, f"{prefix} - cage_{i} {cells[0].format_cell()}")
                model.Add(bool_var == 0)


def adjacent_cages_have_consecutive_totals(model: PuzzleModel, puzzle: Puzzle,
                                           key: CageConstraintsE,
                                           cage_sums: dict[int, int | IntVar]):
    """
    The difference between the sums of the digits in any two orthogonally adjacent cages is exactly 1.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
        key (CageConstraintsE): 
        cage_sums (dict[int, int  |  IntVar]): dictionary mapping cage indexes to cage sums
    """

    key2 = LocalConstraintsModifiersE.ADJACENT_CAGES_HAVE_CONSECUTIVE_TOTALS
    adjacent_cages_have_consecutive_totals = puzzle.bool_constraints.get(
        key2, False)
    # prefix = f"{key2.value}"

    if not adjacent_cages_have_consecutive_totals:
        return

    considered_cages: set[tuple[int, int]] = set()
    for i, (cells, _, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        adjacent_cages = [(j, cells2_vars) for j, (cells2, cells2_vars, _) in enumerate(
            genCageConstraintProperties(model, puzzle, key)) if are_cages_adjacent(cells, cells2)]

        for j, _ in adjacent_cages:
            if (i, j) in considered_cages or (j, i) in considered_cages:
                continue

            cage_sum_1, cage_sum_2 = cage_sums[i], cage_sums[j]
            consecutive_csp(model, cage_sum_1, cage_sum_2)
            considered_cages.add((i, j))


def set_adjacent_cages_are_german_whispers(model: PuzzleModel, puzzle: Puzzle,
                                           key: CageConstraintsE,
                                           cage_sums: dict[int, int | IntVar]):
    """
    In cages, digits sum to the cage total where the cage totals of two cages that share an edge must differ by at least 5.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
        key (CageConstraintsE): 
        cage_sums (dict[int, int  |  IntVar]): dictionary mapping cage indexes to cage sums
    """
    key2 = LocalConstraintsModifiersE.ADJACENT_CAGES_ARE_GERMAN_WHISPERS
    adjacent_cages_are_german_whispers = puzzle.bool_constraints.get(
        key2, False)
    prefix = f"{key.value}"

    if not adjacent_cages_are_german_whispers:
        return

    considered_cages: set[tuple[int, int]] = set()

    for i, (cells, _, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        adjacent_cages = [(j, cells2_vars) for j, (cells2, cells2_vars, _) in enumerate(
            genCageConstraintProperties(model, puzzle, key)) if are_cages_adjacent(cells, cells2)]

        for j, _ in adjacent_cages:
            if (i, j) in considered_cages or (j, i) in considered_cages:
                continue
            cage_sum_1, cage_sum_2 = cage_sums[i], cage_sums[j]
            name = f"{prefix} - dist = |cage_{i} - cage_{j}|"
            dist = distance_csp(model, cage_sum_1, cage_sum_2, name)
            model.Add(dist >= 5)
            considered_cages.add((i, j))


def set_adjacent_cages_have_different_totals(model: PuzzleModel, puzzle: Puzzle, key: CageConstraintsE):
    """
    No two cages with the same total share an edge.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
        key (CageConstraintsE): 
    """

    key2 = LocalConstraintsModifiersE.ADJACENT_CAGES_HAVE_DIFFERENT_TOTALS
    adjacent_cages_have_different_totals = puzzle.bool_constraints.get(
        key2, False)

    if not adjacent_cages_have_different_totals:
        return

    considered_cages: set[tuple[int, int]] = set()
    for i, (cells, cells_vars, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        adjacent_cages = [(j, cells2_vars) for j, (cells2, cells2_vars, _) in enumerate(
            genCageConstraintProperties(model, puzzle, key)) if are_cages_adjacent(cells, cells2)]

        for j, cells2_vars in adjacent_cages:
            if (i, j) in considered_cages or (j, i) in considered_cages:
                continue

            model.Add(sum(cells_vars) != sum(cells2_vars))
            considered_cages.add((i, j))


def set_killer_cage_values_form_renban_line(model: PuzzleModel, puzzle: Puzzle,
                                            key: CageConstraintsE,
                                            cage_sums: dict[int, int | IntVar]):
    key2 = LineConstraintsE.KILLER_CAGE_VALUES_FORM_RENBAN_LINE
    constraints_list = puzzle.tool_constraints.get(key2)
    if not len(constraints_list):
        return

    prefix = f"{key.value} - {key2.value}"

    for i, (line, _, _) in enumerate(genLineConstraintProperties(model, puzzle, key2)):

        cage_idxs_in_line: list[int] = []
        for cell in line:
            found_cages = [(j, cells2_vars) for j, (cells2, cells2_vars, _) in enumerate(
                genCageConstraintProperties(model, puzzle, key)) if cell in cells2]

            if len(found_cages) and found_cages[0][0] not in cage_idxs_in_line:
                cage_idxs_in_line.append(found_cages[0][0])

        cage_sums_in_line = [cage_sums[j] for j in cage_idxs_in_line]

        # RENBAN CONSTRAINT
        renban_csp(model, cage_sums_in_line, f"{prefix} {i}")


def set_killer_cage_values_form_palindrome_line(model: PuzzleModel, puzzle: Puzzle,
                                                key: CageConstraintsE,
                                                cage_sums: dict[int, int | IntVar]):
    """
    Along each line, the cage totals form a palindrome, reading the same from each end. eg R1c1 + r1c2 + r2c1 = r6c1 + r7c1.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
        key (CageConstraintsE): 
        cage_sums (dict[int, int  |  IntVar]): dictionary mapping cage indexes to cage sums
    """
    key2 = LineConstraintsE.KILLER_CAGE_VALUES_FORM_PALINDROME_LINE
    constraints_list = puzzle.tool_constraints.get(key2)
    if not len(constraints_list):
        return

    # prefix = f"{key.value} - {key2.value}"

    for _, (line, _, _) in enumerate(genLineConstraintProperties(model, puzzle, key2)):

        cage_idxs_in_line: list[int] = []
        for cell in line:
            found_cages = [(j, cells2_vars) for j, (cells2, cells2_vars, _) in enumerate(
                genCageConstraintProperties(model, puzzle, key)) if cell in cells2]

            if len(found_cages) and found_cages[0][0] not in cage_idxs_in_line:
                cage_idxs_in_line.append(found_cages[0][0])

        cage_sums_in_line = [cage_sums[j] for j in cage_idxs_in_line]
        palindrome_csp(model, cage_sums_in_line)


def set_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Numbers must not repeat in a killer cage. The numbers in the cage must sum to the given total
    in the top left (if one exists).

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """

    key = CageConstraintsE.KILLER_CAGE
    prefix = f"{key.value}"
    cage_sum_vars: dict[int, IntVar] = dict()
    cage_sums: dict[int, int | IntVar] = dict()

    valid_digits = puzzle.valid_digits
    lb = 0

    for i, (cells, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        model.AddAllDifferent(cells_vars)
        n = len(cells)
        lb = sum(valid_digits[:n])
        ub = sum(valid_digits[-n:])

        sum_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix}_{i}: sum")

        cage_sums[i] = sum_var
        if isinstance(sum_var, IntVar):
            cage_sum_vars[i] = sum_var

        model.Add(sum(cells_vars) == sum_var)

    all_cage_totals_are_unique = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.ALL_CAGE_TOTALS_ARE_UNIQUE, False)
    if all_cage_totals_are_unique:
        model.AddAllDifferent(cage_sum_vars.values())

    adjacent_cages_have_consecutive_totals(model, puzzle, key, cage_sums)
    set_adjacent_cages_have_different_totals(model, puzzle, key)
    set_adjacent_cages_are_german_whispers(model, puzzle, key, cage_sums)

    set_killer_cage_values_form_renban_line(model, puzzle, key, cage_sums)
    set_killer_cage_values_form_palindrome_line(model, puzzle, key, cage_sums)

    set_vaulted_cages(model, puzzle, key)

    norinori_colouring = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.NORINORI_KILLER_CAGES, False)
    if norinori_colouring:
        norinori_grid = get_or_set_norinori_colouring_constraint(model, puzzle)
        for i, (cells, cells_vars, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
            norinori_cells_vars = cells2vars(norinori_grid, cells)
            model.Add(sum(norinori_cells_vars) == 2)


def set_sum_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The numbers in the cage must sum to the given total in the top left (if one exists).
    Numbers can repeat in a sum cage.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.SUM_CAGE
    prefix = f"{key.value}"

    lb = min(puzzle.valid_digits)
    ub = max(puzzle.valid_digits)

    for i, (_, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cells_vars)

        sum_var = model.get_or_set_shared_var(
            value, lb, n * ub, f"{prefix} {i} - sum")

        model.Add(sum(cells_vars) == sum_var)


def set_killer_cage_look_and_say_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    On a cage, given clues should be read as a 'look-and-say' numbers.
    Each number says which digits are in the respective cage.
    Eg if a cage clue is 1221, this means there is one 2 and two 1s in the cage.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.KILLER_CAGE_LOOK_AND_SAY
    prefix = f"{key.value}"

    for i, (_, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        if value:
            counts = look_and_say_parse_string(value)
            for digit, count in counts.items():
                digit_count = count_vars(
                    model, cells_vars, digit, f"{prefix}_{i} - val={value}, count={count}")
                model.Add(digit_count == count)


def set_spotlight_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits must not repeat in 'spotlight' cages, and each spotlight cage must contain the number in the clue.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.SPOTLIGHT_CAGE
    prefix = f"{key.value}"

    for i, (_, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        model.AddAllDifferent(cells_vars)

        if value:
            value2 = parse_int(value)
            if value2 is not None:
                digit_count = count_vars(
                    model, cells_vars, value2, f"{prefix} {i} - digit={value} count")
                model.Add(digit_count == 1)


def set_putteria_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Cages are 'putteria' cages. Each cage of size N has to have the number N contained in it.
    Putteria numbers (Ns) cannot repeat in a cage, and cannot orthogonally neighbour other putteria numbers.
    Other numbers may repeat in putteria cages.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.PUTTERIA_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    all_cells = puzzle.grid.getAllCells()

    # Keep track of the putteria numbers locations
    putteria_number_dict = bool_vars_grid_dict_from_puzzle_grid(
        model, puzzle.grid, f"{prefix} - putteria_number_bools")

    for i, (cells, cells_vars, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cells)

        # only 1 cell == n in the cage
        count_n = count_vars(model, cells_vars, n,
                             f"{prefix}_{i} - digit={n} count")
        model.Add(count_n == 1)

        for j, cell in enumerate(cells):
            cell_var = cells_vars[j]
            putteria_var = cell2var(putteria_number_dict, cell)
            model.Add(cell_var == n).OnlyEnforceIf(putteria_var)
            model.Add(cell_var != n).OnlyEnforceIf(putteria_var.Not())

    num_cages = len([constraint for constraint in genConstraint(puzzle, key)])
    all_putteria_vars = list(putteria_number_dict.values())
    model.Add(sum(all_putteria_vars) == num_cages)

    # Putteria numbers cannot be orthogonally adjacent
    for cell in all_cells:
        putteria_var = cell2var(putteria_number_dict, cell)
        adjacent = puzzle.grid.getOrthogonallyAdjacentCells(cell)
        bools = cells2vars(putteria_number_dict, adjacent)
        model.Add(sum(bools) == 0).OnlyEnforceIf(putteria_var)


def set_cage_as_a_number_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    The contents of each cage in the grid are either a single digit number or form a two-digit number,
    read left to right or downwards.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.CAGE_AS_A_NUMBER
    prefix = f"{key.value}"
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)

    for i, (_, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cells_vars)
        sum_var = model.get_or_set_shared_var(value, min_digit, int(n * f"{max_digit}"),
                                              f"{prefix}_{i}: value")
        multipliers = [10 ** i for i in range(len(cells_vars) - 1, -1, -1)]

        model.Add(sum_var == cp_model.LinearExpr.WeightedSum(
            cells_vars, multipliers))


def set_parity_balance_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    In cages the sum of the even digits equals the sum of the odd digits. Digits cannot repeat within a cage.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.PARITY_BALANCE_KILLER_CAGE
    prefix = f"{key.value}"

    lb = min(puzzle.valid_digits)
    ub = sum(puzzle.valid_digits)

    for i, (_, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        model.AddAllDifferent(cells_vars)

        sum_total_var = model.get_or_set_shared_var(
            value, lb, ub, f"{prefix} {i} - sum_total")

        even_bools = [is_even_csp(
            model, cell_var, f"{prefix} {i} - cell_{j}") for j, cell_var in enumerate(cells_vars)]
        sum_evens = model.NewIntVar(lb, ub//2, f"{prefix} {i} - sum_evens")
        masked_sum1 = masked_sum_csp(
            model, cells_vars, even_bools, f"{prefix} {i} - evens sum")
        model.Add(masked_sum1 == sum_evens)

        odd_bools = [is_even_csp(
            model, cell_var, f"{prefix}_{i} - cell_{j}") for j, cell_var in enumerate(cells_vars)]
        sum_odds = model.NewIntVar(lb, ub//2, f"{prefix} {i} - sum_odds")
        masked_sum2 = masked_sum_csp(
            model, cells_vars, odd_bools, f"{prefix}_{i} - odds sum")
        model.Add(masked_sum2 == sum_odds)

        model.Add(sum(cells_vars) == sum_total_var)
        model.Add(sum_odds == sum_evens)
        model.Add(sum_total_var == sum_odds + sum_evens)


def set_aquarium_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits cannot repeat within a cage. Cells within aquariums are either air cells or water cells, with cells outside
    of cages not being air or water. Water cells fill the bottoms of cages and must have digits greater than all the
    air cells in their cage. Rows in cages must be either all air cells or all water cells.

    Cages must have at least one row of air cells and one row of water cells.

    Additionally, the cages are “pressurized”: The air cells within any cage must have a higher average value than the
    number of rows above that cage in the grid. (Eg If a cage occupied only rows 7, 8 and 9 then any air cells in that
    cage must have an average value greater than 6.).

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.AQUARIUM_CAGE
    prefix = f"{key.value}"
    constraints_list = puzzle.tool_constraints.get(key)
    if not len(constraints_list):
        return

    grid = puzzle.grid
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    # 0 -> not water nor air (outside of cage), 1 -> air, 2 -> water
    aquarium_cage_grid = int_vars_grid_dict_from_puzzle_grid(
        model, grid, 0, 2, f"aquarium_cage_grid")
    model.grid_vars_dict["aquarium_cage_grid"] = aquarium_cage_grid
    all_cells = puzzle.grid.getAllCells()

    aquarium_cage_water_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"aquarium_cage_water_bools_grid")
    model.grid_vars_dict["aquarium_cage_water_bools_grid"] = aquarium_cage_water_bools_grid

    aquarium_cage_air_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"aquarium_cage_air_bools_grid")
    model.grid_vars_dict["aquarium_cage_air_bools_grid"] = aquarium_cage_air_bools_grid

    max_digit = max(puzzle.valid_digits)

    for i, (cage_cells, cells_vars, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        n = len(cage_cells)
        model.AddAllDifferent(cells_vars)

        # constraints for the bools grids
        for j, cell in enumerate(cage_cells):
            aquarium_grid_var = cell2var(aquarium_cage_grid, cell)
            aquarium_cage_water_bool_var = cell2var(
                aquarium_cage_water_bools_grid, cell)
            aquarium_cage_air_bool_var = cell2var(
                aquarium_cage_air_bools_grid, cell)

            model.AddAllowedAssignments([aquarium_grid_var], [(1,), (2,)])

            model.Add(aquarium_grid_var == 2).OnlyEnforceIf(
                aquarium_cage_water_bool_var)
            model.Add(aquarium_grid_var != 2).OnlyEnforceIf(
                aquarium_cage_water_bool_var.Not())

            model.Add(aquarium_grid_var == 1).OnlyEnforceIf(
                aquarium_cage_air_bool_var)
            model.Add(aquarium_grid_var != 1).OnlyEnforceIf(
                aquarium_cage_air_bool_var.Not())

        top_row = min([cell.row for cell in cage_cells])
        bottom_row = max([cell.row for cell in cage_cells])

        # top cells are air==1
        top_cells = [cell for cell in cage_cells if cell.row == top_row]
        top_cells_aquarium_vars = cells2vars(aquarium_cage_grid, top_cells)
        for top_cells_aquarium_var in top_cells_aquarium_vars:
            model.Add(top_cells_aquarium_var == 1)

        # bottom cells are water==2
        bottom_cells = [cell for cell in cage_cells if cell.row == bottom_row]
        bottom_cells_aquarium_vars = cells2vars(
            aquarium_cage_grid, bottom_cells)
        for bottom_cells_aquarium_var in bottom_cells_aquarium_vars:
            model.Add(bottom_cells_aquarium_var == 2)

        # cells with the same row are the same (all water or all air)
        for j in range(top_row + 1, bottom_row):
            middle_row_cells = [cell for cell in cage_cells if cell.row == j]
            middle_row_aquarium_vars = cells2vars(
                aquarium_cage_grid, middle_row_cells)
            all_equal(model, middle_row_aquarium_vars)

        # air cells must be above water cells
        # Or put it another way, the cells above an air cell must also be air cells
        for j in range(top_row + 1, bottom_row):
            middle_row_cells = [cell for cell in cage_cells if cell.row == j]
            above_rows_cells = [cell for cell in cage_cells if cell.row < j]

            middle_row_air_bool_vars = cells2vars(
                aquarium_cage_air_bools_grid, middle_row_cells)
            above_rows_aquarium_vars = cells2vars(
                aquarium_cage_grid, above_rows_cells)

            middle_row_air_bool_var = middle_row_air_bool_vars[0]

            for aquarium_var in above_rows_aquarium_vars:
                # if any middle_row_air_bool_var is air(==0) then all cells in the row above are also air
                # note that if one cell is air in a row then all cells in that row are also air
                model.Add(aquarium_var == 1).OnlyEnforceIf(
                    middle_row_air_bool_var)

        # water cells have higher value than all air cells
        for comb in combinations(cage_cells, 2):
            cage_var1 = cell2var(grid_vars, comb[0])
            cage_var2 = cell2var(grid_vars, comb[1])

            water_bool_var1 = cell2var(aquarium_cage_water_bools_grid, comb[0])
            water_bool_var2 = cell2var(aquarium_cage_water_bools_grid, comb[1])

            air_bool_var1 = cell2var(aquarium_cage_air_bools_grid, comb[0])
            air_bool_var2 = cell2var(aquarium_cage_air_bools_grid, comb[1])

            # if cell1 is air and cell2 is water => cell2 > cell1
            name = f"{prefix}_{i} - {comb[0].format_cell()}==air AND {comb[0].format_cell()}==water"
            c1_air_c2_water = are_all_true_csp(
                model, [air_bool_var1, water_bool_var2], name)

            model.Add(cage_var2 > cage_var1).OnlyEnforceIf(c1_air_c2_water)

            # if cell1 is water and cell2 is air => cell1 > cell2
            name = f"{prefix}_{i} - {comb[0].format_cell()}==water AND {comb[0].format_cell()}==air"
            c1_water_c2_air = are_all_true_csp(
                model, [water_bool_var1, air_bool_var2], name)

            model.Add(cage_var1 > cage_var2).OnlyEnforceIf(c1_water_c2_air)

        # pressurized air: the average value of the air cells must be greater than the number of rows above it
        num_rows_above = top_row

        cage_air_bools = cells2vars(aquarium_cage_air_bools_grid, cage_cells)
        air_cells_count = model.NewIntVar(
            0, n, f"{prefix}_{i} - cage_{cage_cells[0].format_cell()} air_cells_count")
        model.Add(air_cells_count == sum(cage_air_bools))

        name = f"{prefix}_{i} - cage_{cage_cells[0].format_cell()} air_cells_sum"
        air_sum = model.NewIntVar(0, n * max_digit, name)
        masked_sum = masked_sum_csp(model, cells_vars, cage_air_bools, name)
        model.Add(masked_sum == air_sum)
        model.Add(air_sum > num_rows_above * air_cells_count)

    # cells outside of cages are neither air or water
    all_cage_cells = list(set([cell for (cells, _, _) in genCageConstraintProperties(
        model, puzzle, key) for cell in cells]))
    non_cage_cells = [cell for cell in all_cells if cell not in all_cage_cells]

    for cell in non_cage_cells:
        aquarium_grid_var = cell2var(aquarium_cage_grid, cell)
        aquarium_cage_water_bool_var = cell2var(
            aquarium_cage_water_bools_grid, cell)
        aquarium_cage_air_bool_var = cell2var(
            aquarium_cage_air_bools_grid, cell)

        model.Add(aquarium_grid_var == 0)
        model.Add(aquarium_cage_water_bool_var == 0)
        model.Add(aquarium_cage_air_bool_var == 0)


def set_prime_dominos_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    In each green cage, any domino of digits must form a prime number reading left-to-right or downwards.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.PRIME_DOMINOES_CAGE
    prefix = f"{key.value}"
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    for i, (cells, _, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        for cell in cells:
            cell_var = cell2var(grid_vars, cell)

            adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
            adjacent_cells = [
                _cell for _cell in adjacent_cells if _cell.row >= cell.row and _cell.col >= cell.col]
            adjacent_cells_in_cage = [
                _cell for _cell in adjacent_cells if _cell in cells]
            for cell2 in adjacent_cells_in_cage:
                cell2_var = cell2var(grid_vars, cell2)

                name = f"{prefix}_{i} - prime_{cell.format_cell()}_{cell2.format_cell()}"
                prime_var = model.NewIntVar(0, 100, name)
                model.Add(prime_var == cell_var * 10 + cell2_var)
                member_of(model, PRIME_LIST, prime_var, name)


def set_no_prime_dominos_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    In each red cage, any domino of digits must NOT form a prime number reading left-to-right or downwards.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.NO_PRIME_DOMINOES_CAGE
    prefix = f"{key.value}"
    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    for i, (cells, _, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        for cell in cells:
            cell_var = cell2var(grid_vars, cell)

            adjacent_cells = grid.getOrthogonallyAdjacentCells(cell)
            adjacent_cells = [
                _cell for _cell in adjacent_cells if _cell.row >= cell.row and _cell.col >= cell.col]
            adjacent_cells_in_cage = [
                _cell for _cell in adjacent_cells if _cell in cells]
            for cell2 in adjacent_cells_in_cage:
                cell2_var = cell2var(grid_vars, cell2)

                name = f"{prefix}_{i} - prime_{cell.format_cell()}_{cell2.format_cell()}"
                not_prime_var = model.NewIntVar(0, 100, name)
                model.Add(not_prime_var == cell_var * 10 + cell2_var)
                is_prime_var = is_member_of(
                    model, PRIME_LIST, not_prime_var, name)
                model.Add(is_prime_var == 0)


def set_divisible_killer_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Digits within a cage must sum to a number divisible by the clue given in the top left of the cage.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.DIVISIBLE_KILLER_CAGE
    prefix = f"{key.value}"
    cage_sum_vars: dict[str, IntVar] = dict()

    lb = 0
    ub = sum(puzzle.valid_digits)

    for i, (_, cells_vars, value) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        model.AddAllDifferent(cells_vars)

        sum_var = model.get_or_set_shared_var(
            None, lb, ub, f"{prefix}_{i}: sum")
        divisor_var = model.get_or_set_shared_var(value, lb, sum(puzzle.valid_digits),
                                                  f"{prefix}_{i}: divisor")

        if isinstance(sum_var, IntVar):
            name = sum_var.name
            cage_sum_vars[name] = sum_var

        model.Add(sum(cells_vars) == sum_var)
        model.AddModuloEquality(0, sum_var, divisor_var)

    all_cage_sums_are_unique = puzzle.bool_constraints.get(
        LocalConstraintsModifiersE.DIVISIBLE_KILLER_CAGE_SUMS_ARE_UNIQUE, False)
    if all_cage_sums_are_unique:
        model.AddAllDifferent(cage_sum_vars.values())


def set_sujiken_cage_constraints(model: PuzzleModel, puzzle: Puzzle):
    """
    Green cells are Sujiken (no digit is repeated in any diagonal in any direction in this area).

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 
    """
    key = CageConstraintsE.SUJIKEN_REGION
    # prefix = f"{key.value}"

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']
    grid = puzzle.grid

    for _, (cells, _, _) in enumerate(genCageConstraintProperties(model, puzzle, key)):
        for cell in cells:
            # get the two diagonals with the cell
            pdiag = grid.getCellsInPDiagonalWithCell(cell)
            ndiag = grid.getCellsInNDiagonalWithCell(cell)

            # diagonal cells in region
            pdiag = [cell2 for cell2 in pdiag if cell2 in cells]
            ndiag = [cell2 for cell2 in ndiag if cell2 in cells]

            pdiag_vars = cells2vars(grid_vars, pdiag)
            ndiag_vars = cells2vars(grid_vars, ndiag)

            model.AddAllDifferent(pdiag_vars)
            model.AddAllDifferent(ndiag_vars)
