

from typing import Any
from puzzlesolver.Puzzle.ConstraintEnums import LineConstraintsE, OutsideCornerConstraintsE, OutsideEdgeConstraintsE, isStrOfToolEnumType
from puzzlesolver.Puzzle.Coords import GridCoords
from puzzlesolver.Puzzle.Directions import DIRECTIONS, RCToDirectionDict
from puzzlesolver.utils.fileUtils import loadJSON
import os
import json


def update_line_constraints(data: dict[str, Any]) -> dict[str, Any]:
    new_json: dict[str, Any] = dict()
    for key, value in data.items():
        if isStrOfToolEnumType(key, LineConstraintsE):
            constraints = value
            for constraint in constraints:
                lines = constraint.pop('lines')
                new_line = lines[0]
                constraint['cells'] = new_line
            new_json[key] = constraints
        else:
            new_json[key] = value

    return new_json


def update_outside_corner_constraints(data: dict[str, Any]) -> dict[str, Any]:
    new_json: dict[str, Any] = dict()
    for key, value in data.items():
        if isStrOfToolEnumType(key, OutsideCornerConstraintsE):
            constraints = value
            for constraint in constraints:
                constraint.pop('cells')
            new_json[key] = constraints
        else:
            new_json[key] = value

    return new_json


def update_outside_edge_constraints(data: dict[str, Any]) -> dict[str, Any]:
    new_json: dict[str, Any] = dict()
    for key, value in data.items():
        if isStrOfToolEnumType(key, OutsideEdgeConstraintsE):
            constraints = value
            for constraint in constraints:
                cell: GridCoords = GridCoords.fromString(constraint['cell'])

                direction: DIRECTIONS | None = None
                if cell.r < cell.c and cell.r <= 1:
                    direction = DIRECTIONS.S
                elif cell.c < cell.r and cell.c <= 1:
                    direction = DIRECTIONS.E
                elif cell.r > cell.c:
                    direction = DIRECTIONS.N
                elif cell.c > cell.r:
                    direction = DIRECTIONS.W

                if direction is None:
                    raise Exception("No direction")
                constraint['direction'] = direction.value

            new_json[key] = constraints
        else:
            new_json[key] = value

    return new_json


def update_format(origin_path: str, dest_path: str):
    os.makedirs(dest_path, exist_ok=True)
    (_, tail) = os.path.split(origin_path)
    dest_filename = os.path.join(dest_path, tail)

    old_json = loadJSON(origin_path)
    new_json = update_outside_edge_constraints(old_json)

    with open(dest_filename, 'w') as file:
        json.dump(new_json, file, indent=4)


if __name__ == "__main__":
    origin_path = './jsonFiles/OldFormat/'
    dest_path = './jsonFiles/NewFormat/'

    obj = os.scandir(origin_path)
    dir_list = [entry.name for entry in obj if entry.is_file()]

    for input_file in dir_list:
        filepath = origin_path + input_file
        try:
            update_format(filepath, dest_path)
        except Exception as exception:
            print(exception)
            print(f"Could not convert {input_file}")
            print()
