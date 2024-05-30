from typing import Any

from puzzlesolver.Puzzle.ConstraintEnums import ArrowConstraintsE, CageConstraintsE, RCConstraintsE, TwoRegionsConstraintsE, CornerConstraintsE, CosmeticToolsE, DoubleValuedGlobalConstraintsE, EdgeConstraintsE, LineConstraintsE, OutsideCornerConstraintsE, OutsideEdgeConstraintsE, SingleCellArrowConstraintsE, SingleCellConstraintsE, SingleCellMultiArrowConstraintsE, ToolEnum, ValuedGlobalConstraintsE, isToolOfType, localToolConstraintGen

from puzzlesolver.Puzzle.Constraints import ArrowConstraint, CageConstraint, CloneConstraint, Constraint, CornerConstraint, DoubleValuedGlobalConstraint, EdgeConstraint, LineConstraint, LocalConstraint, OutsideCornerConstraint, OutsideEdgeConstraint, RCConstraint, SingleCellArrowConstraint, SingleCellConstraint, SingleCellMultiArrowConstraint, ValuedGlobalConstraint


class ToolConstraints:
    _dict: dict[ToolEnum, list[Constraint]]

    def __init__(self) -> None:
        self._dict = dict()

    def keys(self):
        return self._dict.keys()

    def addConstraint(self, key: ToolEnum, constraint: Constraint) -> None:
        constraintList = self._dict.get(key)
        if constraintList:
            constraintList.append(constraint)
            return
        # elif key in tool_constraint_key_gen():
        self._dict[key] = [constraint]

    def removeConstraint(self, key: ToolEnum, constraint: Constraint):
        if key in self._dict:
            constraint_list = self._dict.get(key)
            if constraint_list and constraint in constraint_list:
                constraint_list.remove(constraint)

    def get(self, key: ToolEnum):
        return self._dict.get(key, [])

    def items(self):
        return self._dict.items()

    @classmethod
    def load_tool_constraints(cls, data: dict[Any, Any]) -> 'ToolConstraints':
        tool_constraints: ToolConstraints = ToolConstraints()
        for tool_key in localToolConstraintGen():
            _id = str(tool_key.value)
            if _id not in data:
                continue

            constraint_list_data = data[_id]
            if not constraint_list_data:
                continue

            for constraint_data in constraint_list_data:
                constraint: None | LocalConstraint = None
                if isToolOfType(tool_key, SingleCellConstraintsE):
                    constraint = SingleCellConstraint.fromJsonData(
                        constraint_data, tool_key)

                if isToolOfType(tool_key, SingleCellArrowConstraintsE):
                    constraint = SingleCellArrowConstraint.fromJsonData(
                        constraint_data, tool_key)

                if isToolOfType(tool_key, SingleCellMultiArrowConstraintsE):
                    constraint = SingleCellMultiArrowConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, EdgeConstraintsE):
                    constraint = EdgeConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, CornerConstraintsE):
                    constraint = CornerConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, LineConstraintsE):
                    constraint = LineConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, ArrowConstraintsE):
                    constraint = ArrowConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, TwoRegionsConstraintsE):
                    constraint = CloneConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, CageConstraintsE) or tool_key == CosmeticToolsE.COSMETIC_CAGE:
                    constraint = CageConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, OutsideEdgeConstraintsE):
                    constraint = OutsideEdgeConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, OutsideCornerConstraintsE):
                    constraint = OutsideCornerConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, ValuedGlobalConstraintsE):
                    constraint = ValuedGlobalConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, DoubleValuedGlobalConstraintsE):
                    constraint = DoubleValuedGlobalConstraint.fromJsonData(
                        constraint_data, tool_key)

                elif isToolOfType(tool_key, RCConstraintsE):
                    constraint = RCConstraint.fromJsonData(
                        constraint_data, tool_key)

                if constraint is not None:
                    tool_constraints.addConstraint(tool_key, constraint)

        return tool_constraints

    def toJson(self):
        data: dict[str, Any] = dict()
        for key, c_list in self._dict.items():
            data_list: list[Any] = []
            for constraint in c_list:
                constraint_data = constraint.toJsonData()
                data_list.append(constraint_data)
            data[key.value] = data_list
        return data


if __name__ == "__main__":
    tool_constraints = ToolConstraints()
