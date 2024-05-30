from puzzlesolver.Puzzle.Cell import Cell
from puzzlesolver.Puzzle.ConstraintEnums import ArrowConstraintsE
from puzzlesolver.Puzzle.Constraints import ArrowConstraint
from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_csp_utils import GridVars, cell2var, coord2var
# from Puzzle2cp_model.puzzle_csp_utils import GridVars, coord2var


def genConstraint(puzzle: Puzzle, tool_key: ArrowConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    for constraint in constraints_list:
        if not isinstance(constraint, ArrowConstraint):
            continue
        yield constraint


def genArrowConstraintProperties(model: PuzzleModel, puzzle: Puzzle, tool_key: ArrowConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    grid_vars: GridVars = model.grid_vars_dict['cells_grid_vars']

    for constraint in constraints_list:
        if not isinstance(constraint, ArrowConstraint):
            continue
        cell_coords = constraint.cells
        cells: list[Cell] = []
        for cell_coord in cell_coords:
            cell = puzzle.grid.getCellFromCoords(cell_coord)
            if cell is not None:
                cells.append(cell)

        lines: list[list[Cell]] = []
        for line_cell_coords in constraint.lines:
            line: list[Cell] = []
            for cell_coord in line_cell_coords:
                cell = puzzle.grid.getCellFromCoords(cell_coord)
                if cell is not None:
                    line.append(cell)
            if len(line):
                lines.append(line)

        cells_vars = [coord2var(grid_vars, cell_coord)
                      for cell_coord in cell_coords]
        lines_vars = [[cell2var(grid_vars, cell)
                      for cell in line] for line in lines]
        yield cells, lines, cells_vars, lines_vars, constraint.value
