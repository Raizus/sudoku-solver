from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.ArrowConstraints.ArrowConstraints2csp import set_arrow_constraints
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel

from puzzlesolver.Puzzle2model.OutsideCornerConstraints.OutsideCornerConstraints2csp import set_outside_corner_constraints
from puzzlesolver.Puzzle2model.OutsideEdgeConstraints.OutsideEdgeConstraints2csp import set_outside_edge_constraints
from puzzlesolver.Puzzle2model.RCConstraints.RCConstraint2csp import set_rc_constraints
from puzzlesolver.Puzzle2model.TwoRegionsConstraints.TwoRegionsConstraints2csp import set_two_regions_constraints
from puzzlesolver.Puzzle2model.ValuedGlobalConstraints.ValuedGlobalConstraints2csp import set_valued_global_constraints
from puzzlesolver.Puzzle2model.EdgeConstraints.BorderConstraints2csp import set_edge_constraints
from puzzlesolver.Puzzle2model.CageConstraints.CageConstraints2csp import set_cage_constraints
from puzzlesolver.Puzzle2model.CornerConstraints.CornerConstraints2csp import set_corner_constraints
from puzzlesolver.Puzzle2model.LineConstraints.LineTools2csp import set_line_constraints
from puzzlesolver.Puzzle2model.SingleCellConstraints.SingleCellConstraints2csp import set_single_cell_constraints


def set_tool_constraints(model: PuzzleModel, puzzle: Puzzle):

    set_outside_edge_constraints(model, puzzle)
    set_outside_corner_constraints(model, puzzle)

    set_rc_constraints(model, puzzle)

    set_edge_constraints(model, puzzle)
    set_corner_constraints(model, puzzle)
    set_line_constraints(model, puzzle)
    set_arrow_constraints(model, puzzle)

    set_single_cell_constraints(model, puzzle)
    set_two_regions_constraints(model, puzzle)
    set_cage_constraints(model, puzzle)

    set_valued_global_constraints(model, puzzle)
