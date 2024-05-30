from typing import Any
from puzzlesolver.Puzzle.ConstraintEnums import BoolToolEnum, globalToolConstraintGen


def set_bool_constraints() -> dict[BoolToolEnum, bool]:
    bool_constraints: dict[BoolToolEnum, bool] = dict()

    for tool_key in globalToolConstraintGen():
        bool_constraints[tool_key] = False

    return bool_constraints


def load_bool_constraints(data: dict[str, Any]) -> dict[BoolToolEnum, bool]:
    bool_constraints: dict[BoolToolEnum, bool] = dict()

    for tool_key in globalToolConstraintGen():
        _id = str(tool_key.value)
        if _id not in data:
            continue

        value = data.get(_id, False)
        if value:
            bool_constraints[tool_key] = value

    # diff = set(data.keys()).difference(bool_constraints.keys())
    # if len(diff):
    #     raise Exception(f'Some constraints were not processed: {diff}')

    return bool_constraints


def bool_constraints_to_json(bool_constraints: dict[BoolToolEnum, bool]):
    data: dict[str, Any] = dict()

    for key, value in bool_constraints.items():
        if value:
            data[key.value] = value
    return data
