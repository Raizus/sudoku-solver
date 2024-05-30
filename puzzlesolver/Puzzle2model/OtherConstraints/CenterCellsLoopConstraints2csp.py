
from puzzlesolver.Puzzle.ConstraintEnums import GlobalRegionConstraintsE
from puzzlesolver.Puzzle.Grid import Grid
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.OtherConstraints.UnknownRegionsConstraints2csp import get_or_set_unknown_regions_grid
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import are_all_equal_csp, are_all_true_csp, count_vars
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cell2var, edge_from_cells, orthogonally_connected_region_adjacency_vars_csp
from puzzlesolver.Puzzle2model.puzzle_model_types import AdjacencyVarsDict
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar


def build_cell_center_loop_adj_vars_dict(model: cp_model.CpModel, grid: Grid):
    # build the adjacency dictionary with corresponding edge IntVars, indicating if there is an edge between two cells centers' (nodes)
    # This assumes the edges are not directed n1 <-> n2

    prefix = f"cell_center_loop"
    loop_edges_dict: AdjacencyVarsDict = dict()
    all_cells = grid.getAllCells()
    for cell1 in all_cells:
        adjacent_cells = grid.getOrthogonallyAdjacentCells(cell1)
        edges_of_cell1 = loop_edges_dict.setdefault(
            (cell1.row, cell1.col), dict())
        for cell2 in adjacent_cells:
            edges_of_cell2 = loop_edges_dict.get((cell2.row, cell2.col))
            if edges_of_cell2:
                edge_var = edges_of_cell2.get((cell1.row, cell1.col))
                if edge_var is not None:
                    edges_of_cell1[(cell2.row, cell2.col)] = edge_var
                    continue

            edge_var = model.NewBoolVar(
                f"{prefix} - edge_{cell1.format_cell()}_{cell2.format_cell()}")
            edges_of_cell1[(cell2.row, cell2.col)] = edge_var

    return loop_edges_dict


def set_cell_center_loop_enters_and_exits_every_region_once(model: PuzzleModel, puzzle: Puzzle):
    key = GlobalRegionConstraintsE.LOOP_ENTER_AND_EXITS_EVERY_REGION_EXACTLY_ONCE
    enter_and_exit_once_per_region = puzzle.bool_constraints.get(key, False)
    enter_and_exit_once_per_region = True
    if not enter_and_exit_once_per_region:
        return

    unknown_regions1 = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.UNKNOWN_REGIONS, False)
    unknown_regions2 = puzzle.bool_constraints.get(
        GlobalRegionConstraintsE.UNKNOWN_NUMBERED_REGIONS, False)
    if not (unknown_regions1 or unknown_regions2):
        return

    grid = puzzle.grid
    loop_edges_dict = model.adjacency_vars_dicts["loop_edges_dict"]
    regions_grid = get_or_set_unknown_regions_grid(model, puzzle)

    prefix = f"Cells Center Loop - {key.value}"

    num_regions = 9
    all_transition_vars: list[IntVar] = []
    for cell1, cell2 in grid.genAllAdjacentPairs():
        prefix2 = f"{prefix} - {cell1.format_cell()}, {cell2.format_cell()}"
        cell1_region_var = cell2var(regions_grid, cell1)
        cell2_region_var = cell2var(regions_grid, cell2)

        edge_var = edge_from_cells(loop_edges_dict, cell1, cell2)
        if edge_var is None:
            continue

        name = f"{prefix2} - same_region_bool"
        same_region_bool = are_all_equal_csp(
            model, [cell1_region_var, cell2_region_var], name)
        name = f"{prefix2} - is_transition"
        is_transition = are_all_true_csp(model, [edge_var, same_region_bool.Not()],  # type: ignore
                                         name)

        transition_var_1 = model.NewIntVar(-1, num_regions-1,
                                           f"{prefix2} - transition_var_1")
        transition_var_2 = model.NewIntVar(-1, num_regions-1,
                                           f"{prefix2} - transition_var_2")
        model.Add(transition_var_1 == cell1_region_var).OnlyEnforceIf(
            is_transition)
        model.Add(transition_var_1 == -1).OnlyEnforceIf(
            is_transition.Not())

        model.Add(transition_var_2 == cell2_region_var).OnlyEnforceIf(
            is_transition)
        model.Add(transition_var_2 == -1).OnlyEnforceIf(
            is_transition.Not())

        all_transition_vars.append(transition_var_1)
        all_transition_vars.append(transition_var_2)

    for region in range(num_regions):
        count_var = count_vars(model, all_transition_vars, region,
                               f"{prefix} - region_{region} - count_transitions")
        model.Add(count_var == 2)


def _set_cell_center_loop_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    n_rows = grid.nRows
    n_cols = grid.nCols
    cells_grid_vars = model.grid_vars_dict['cells_grid_vars']
    grid_vars_dict = model.grid_vars_dict
    adjacency_vars_dicts = model.adjacency_vars_dicts
    all_cells = grid.getAllCells()

    # prefix = f"cell_center_loop"

    # var indicates if a cell is part of the loop
    loop_bools_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, "cell_center_loop")

    loop_edges_dict = build_cell_center_loop_adj_vars_dict(model, grid)

    grid_vars_dict["loop_bools_grid"] = loop_bools_grid
    adjacency_vars_dicts["loop_edges_dict"] = loop_edges_dict

    # if a cell is part of the loop then there are two edges attached to it,
    # if not there are zero edges attached to it
    for cell in all_cells:
        loop_var = cell2var(loop_bools_grid, cell)
        edges_vars = list(loop_edges_dict[(cell.row, cell.col)].values())
        model.Add(sum(edges_vars) == 2).OnlyEnforceIf(loop_var)
        model.Add(sum(edges_vars) == 0).OnlyEnforceIf(loop_var.Not())

    # loop must be orthogonally connected
    orthogonally_connected_region_adjacency_vars_csp(
        model, loop_edges_dict, loop_bools_grid, n_rows * n_cols)

    # loop must visit every region
    set_cell_center_loop_enters_and_exits_every_region_once(model, puzzle)

    # loop passes through every cell except cells that have the digit 1
    key = GlobalRegionConstraintsE.CENTER_CELLS_LOOP_PASSES_THROUGH_EVERY_CELL_EXCEPT_DIGIT_1
    loop_every_cell_except_1 = puzzle.bool_constraints.get(key, False)
    if loop_every_cell_except_1:
        for cell in all_cells:
            cell_var = cell2var(cells_grid_vars, cell)
            loop_var = cell2var(loop_bools_grid, cell)
            model.Add(cell_var == 1).OnlyEnforceIf(loop_var.Not())
            model.Add(cell_var != 1).OnlyEnforceIf(loop_var)

    return loop_bools_grid, loop_edges_dict


def get_or_set_cell_center_loop_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    adjacency_vars_dicts = model.adjacency_vars_dicts
    if "loop_bools_grid" in grid_vars_dict:
        return grid_vars_dict["loop_bools_grid"], adjacency_vars_dicts["loop_edges_dict"]

    loop_bools_grid, loop_edges_dict = _set_cell_center_loop_constraint(
        model, puzzle)
    return loop_bools_grid, loop_edges_dict
