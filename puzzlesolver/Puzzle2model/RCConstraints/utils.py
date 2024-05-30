
from puzzlesolver.Puzzle.ConstraintEnums import RCConstraintsE
from puzzlesolver.Puzzle.Constraints import RCConstraint
from puzzlesolver.Puzzle.Puzzle import Puzzle


def genRCConstraintProperties(puzzle: Puzzle, tool_key: RCConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    for constraint in constraints_list:
        if not isinstance(constraint, RCConstraint):
            continue
        coords = constraint.coords

        value = constraint.value
        yield coords, value
