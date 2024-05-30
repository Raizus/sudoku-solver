from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.custom_constraints import count_vars
from puzzlesolver.Puzzle2model.puzzle_csp_utils import bool_vars_grid_dict_from_puzzle_grid, cells2vars, orthogonally_connected_region_csp
from puzzlesolver.Puzzle2model.puzzle_model_types import build_adjacency_dict


def _set_nurimisaki_constraint(model: PuzzleModel, puzzle: Puzzle):
    """
    Shade some cells so that the remaining unshaded cells form one orthogonally connected area. No 2x2 region may be entirely shaded or unshaded.
        shaded <=> 0
        unshaded <=> 1

    Args:
        model (PuzzleModel): 
        puzzle (Puzzle): 

    Returns:
        _type_: 
    """
    grid = puzzle.grid
    n_rows = grid.nRows
    n_cols = grid.nCols
    all_cells = grid.getAllCells()
    prefix = f"nurimisaki"
    grid_vars_dict = model.grid_vars_dict

    # 1 <=> unshaded; 0 <=> shaded
    nurimisaki_grid = bool_vars_grid_dict_from_puzzle_grid(
        model, grid, f"nurimisaki")

    # 2x2 box cannot be all shaded or all unshaded
    for cell in all_cells:
        box = [cell for line in grid.getXByYBox(cell, 2, 2) for cell in line]
        if len(box) != 4:
            continue

        two_by_two = cells2vars(nurimisaki_grid, box)
        # 2x2 box cannot be all shaded or all unshaded, 0 < count < 4
        count0 = count_vars(model, two_by_two, 0,
                            f"{prefix} - count0_2by2_{cell.format_cell()}")
        model.Add(count0 >= 1)
        model.Add(count0 <= 3)

    seed = None
    # nurimisaki_unshaded_endpoints_list: List[NurimisakiUnshadedEndpoints] = \
    #     puzzle.tool_constraints.get(
    #         SingleCellConstraintsE.NURIMISAKI_UNSHADED_ENDPOINTS)
    # if nurimisaki_unshaded_endpoints_list:
    #     seed_cell = nurimisaki_unshaded_endpoints_list[0].cell
    #     seed = [(seed_cell.row, seed_cell.col)]

    # unshaded cells (1's) must be orthogonally connected
    adjacency_dict = build_adjacency_dict(grid)
    orthogonally_connected_region_csp(
        model, adjacency_dict, nurimisaki_grid, n_rows * n_cols, seed)

    grid_vars_dict["nurimisaki_grid"] = nurimisaki_grid

    return nurimisaki_grid


def get_or_set_nurimisaki_constraint(model: PuzzleModel, puzzle: Puzzle):
    grid_vars_dict = model.grid_vars_dict
    if "nurimisaki_grid" in grid_vars_dict:
        return grid_vars_dict["nurimisaki_grid"]

    nurimisaki_grid = _set_nurimisaki_constraint(model, puzzle)
    return nurimisaki_grid
