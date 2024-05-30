from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import count_vars, increasing_strict, is_member_of
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cell2var, cells2vars, int_vars_grid_dict_from_puzzle_grid


from ortools.sat.python.cp_model import IntVar


def _set_ambiguous_entropy_constraint(model: PuzzleModel, puzzle: Puzzle):
    """
    Every 2x2 square of cells must contain a digit from each of three sets (A,B,C)-(D,E,F)-(G,H,I) however, the digits in each entropy set must be deduced by the solver.

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 

    Returns:
        _type_: 
    """
    prefix = f"Ambiguous Entropy"
    grid = puzzle.grid
    all_cells = grid.getAllCells()
    grid_vars_dict = model.grid_vars_dict
    num_sets = 3

    # create multipliers bool grid, var == 1 if multiplier, else var == 0
    ambiguous_entropy_grid = int_vars_grid_dict_from_puzzle_grid(model, grid, 0, num_sets - 1,
                                                                 f"ambiguous_entropy_grid")
    grid_vars_dict["ambiguous_entropy_grid"] = ambiguous_entropy_grid
    cells_grid_vars = grid_vars_dict['cells_grid_vars']
    min_digit = min(puzzle.valid_digits)
    max_digit = max(puzzle.valid_digits)
    set_size = 3

    # group mappings
    all_set_vars: list[IntVar] = []
    first_members: list[IntVar] = []
    set_vars_dict: dict[int, list[IntVar]] = dict()
    for i in range(num_sets):
        set_vars = [model.NewIntVar(min_digit, max_digit,
                                    f"{prefix} - entropy_set_{i} - member_{j}") for j in range(set_size)]
        # order each set to ensure unique solution
        increasing_strict(model, set_vars)

        all_set_vars.extend(set_vars)
        first_members.append(set_vars[0])
        set_vars_dict[i] = set_vars

    # order each set by their first member to ensure unique solution
    model.AddAllDifferent(all_set_vars)
    increasing_strict(model, first_members)

    # each cell belongs to a single set
    for cell in all_cells:
        cell_entropy_var = cell2var(ambiguous_entropy_grid, cell)
        cell_var = cell2var(cells_grid_vars, cell)

        member_of_set_vars: list[IntVar] = []
        for i in range(num_sets):
            member_of_set = is_member_of(model, set_vars_dict[i], cell_var,
                                         f"{prefix} - {cell.format_cell()} is_member_of_set_{i}")
            model.Add(cell_entropy_var == i).OnlyEnforceIf(member_of_set)
            model.Add(cell_entropy_var != i).OnlyEnforceIf(member_of_set.Not())
            member_of_set_vars.append(member_of_set)

        model.AddExactlyOne(member_of_set_vars)

    # each 2x2 box must contain at least one digit from each of three sets (and at most 2)
    for cell in all_cells:
        two_by_two_box = [cell for line in grid.getXByYBox(
            cell, 2, 2) for cell in line]
        if len(two_by_two_box) != 4:
            continue

        box_vars = cells2vars(ambiguous_entropy_grid, two_by_two_box)
        for i in range(num_sets):
            count_entropy_group_i = count_vars(model, box_vars, i,
                                               f"{prefix} - {cell.format_cell()} 2x2 box, entropy group {i} count")
            model.Add(count_entropy_group_i >= 1)
            model.Add(count_entropy_group_i <= 2)

    return ambiguous_entropy_grid


def get_or_set_ambiguous_entropy_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "ambiguous_entropy_grid" in grid_vars_dict:
        return grid_vars_dict["ambiguous_entropy_grid"]

    ambiguous_entropy_grid = _set_ambiguous_entropy_constraint(model, puzzle)
    return ambiguous_entropy_grid
