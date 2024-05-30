from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_csp_utils import cells2vars
from puzzlesolver.Puzzle2model.puzzle_model_types import GridVars


def _set_edge_loop_constraints(model: PuzzleModel, puzzle: Puzzle):
    grid = puzzle.grid
    n_rows = grid.nRows
    n_cols = grid.nCols
    all_cells = grid.getAllCells()
    grid_vars_dict = model.grid_vars_dict
    prefix = f"edge_loop"

    inside_outside_edge_loop_dict: GridVars = {}
    for cell in all_cells:
        name = f"{prefix} - inside_outside_{cell.format_cell()}"
        var = model.NewBoolVar(name)
        inside_outside_edge_loop_dict[(cell.row, cell.col)] = var

    loop_nodes_dict: GridVars = {}
    for i in range(n_rows + 1):
        for j in range(n_cols + 1):
            loop_nodes_dict[(i, j)] = model.NewBoolVar(
                f"{prefix} - loop_node_({i}, {j})")

    horizontal_loop_edges: GridVars = {}
    for i in range(n_rows + 1):
        for j in range(n_cols):
            horizontal_loop_edges[(i, j)] = model.NewBoolVar(
                f"{prefix} - horizontal_loop_edges_({i}, {j})")

    vertical_loop_edges: GridVars = {}
    for j in range(n_cols + 1):
        for i in range(n_rows):
            vertical_loop_edges[(i, j)] = model.NewBoolVar(
                f"{prefix} - vertical_loop_edges_({i}, {j})")

    for (i, j), loop_node_var in loop_nodes_dict.items():
        horiz_connected_edges = [horizontal_loop_edges.get(
            (i, j - 1)), horizontal_loop_edges.get((i, j))]
        vert_connected_edges = [vertical_loop_edges.get(
            (i - 1, j)), vertical_loop_edges.get((i, j))]
        edges = horiz_connected_edges + vert_connected_edges
        edges = [x for x in edges if x is not None]

        model.Add(sum(edges) == 2).OnlyEnforceIf(loop_node_var)
        model.Add(sum(edges) == 0).OnlyEnforceIf(loop_node_var.Not())

    for (i, j), loop_node_var in horizontal_loop_edges.items():
        adjacent_cells = [grid.getCell(i - 1, j), grid.getCell(i, j)]
        adjacent_cells = [cell for cell in adjacent_cells if cell is not None]
        inside_outside_adjacent_vars = cells2vars(
            inside_outside_edge_loop_dict, adjacent_cells)
        # edge is on the edge of the grid
        if len(adjacent_cells) == 1:
            var = inside_outside_adjacent_vars[0]
            # cell is inside the loop if there's an edge that belongs to the group on the grid's edge
            model.Add(var == 1).OnlyEnforceIf(loop_node_var)
        else:
            var1 = inside_outside_adjacent_vars[0]
            var2 = inside_outside_adjacent_vars[1]
            model.Add(var1 != var2).OnlyEnforceIf(loop_node_var)
            model.Add(var1 == var2).OnlyEnforceIf(loop_node_var.Not())

    for (i, j), loop_node_var in vertical_loop_edges.items():
        adjacent_cells = [grid.getCell(i, j - 1), grid.getCell(i, j)]
        adjacent_cells = [cell for cell in adjacent_cells if cell is not None]
        inside_outside_adjacent_vars = cells2vars(
            inside_outside_edge_loop_dict, adjacent_cells)
        # edge is on the edge of the grid
        if len(adjacent_cells) == 1:
            var = inside_outside_adjacent_vars[0]
            # cell is inside the loop if there's an edge that belongs to the group on the grid's edge
            model.Add(var == 1).OnlyEnforceIf(loop_node_var)
        else:
            var1 = inside_outside_adjacent_vars[0]
            var2 = inside_outside_adjacent_vars[1]
            model.Add(var1 != var2).OnlyEnforceIf(loop_node_var)
            model.Add(var1 == var2).OnlyEnforceIf(loop_node_var.Not())

    grid_vars_dict["inside_outside_edge_loop_dict"] = inside_outside_edge_loop_dict
    grid_vars_dict["loop_nodes_dict"] = loop_nodes_dict
    grid_vars_dict["horizontal_loop_edges"] = horizontal_loop_edges
    grid_vars_dict["vertical_loop_edges"] = vertical_loop_edges

    return inside_outside_edge_loop_dict


def get_or_set_edge_loop_constraint(model: PuzzleModel,
                                    puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "inside_outside_edge_loop_dict" in grid_vars_dict:
        return grid_vars_dict["inside_outside_edge_loop_dict"]

    inside_outside_edge_loop_dict = _set_edge_loop_constraints(
        model, puzzle)
    return inside_outside_edge_loop_dict
