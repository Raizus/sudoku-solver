

from puzzlesolver.Puzzle.ConstraintEnums import DoubleValuedGlobalConstraintsE, ValuedGlobalConstraintsE
from puzzlesolver.Puzzle.Constraints import DoubleValuedGlobalConstraint, ValuedGlobalConstraint
from puzzlesolver.Puzzle.Puzzle import Puzzle


def genValuedGlobalConstraint(puzzle: Puzzle, tool_key: ValuedGlobalConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    for constraint in constraints_list:
        if not isinstance(constraint, ValuedGlobalConstraint):
            continue
        yield constraint


def genDoubleValuedGlobalConstraint(puzzle: Puzzle, tool_key: DoubleValuedGlobalConstraintsE):
    tool_constraints = puzzle.tool_constraints
    constraints_list = tool_constraints.get(
        tool_key)
    if not constraints_list:
        return

    for constraint in constraints_list:
        if not isinstance(constraint, DoubleValuedGlobalConstraint):
            continue
        yield constraint
