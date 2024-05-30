

import json
from typing import Any
from puzzlesolver.Puzzle.GlobalConstraints import bool_constraints_to_json
from puzzlesolver.Puzzle.Puzzle import Puzzle
import os

from puzzlesolver.utils.fileUtils import loadJSON


def convert_to_new_format(origin_path: str, dest_path: str):

    old_json = loadJSON(origin_path)
    puzzle = Puzzle.fromJSON(origin_path)

    new_json: dict[str, Any] = dict()

    bool_constraints_data = bool_constraints_to_json(
        puzzle.bool_constraints)
    local_constraints_data = puzzle.tool_constraints.toJson()

    new_json['puzzleInfo'] = old_json['puzzleInfo']
    new_json['nRows'] = old_json['nRows']
    new_json['nCols'] = old_json['nCols']
    if 'valid_digits' in old_json:
        new_json['valid_digits'] = old_json['valid_digits']
    new_json['grid'] = old_json['grid']
    new_json['bool_constraints'] = bool_constraints_data
    new_json['local_constraints'] = local_constraints_data

    os.makedirs(dest_path, exist_ok=True)
    (_, tail) = os.path.split(origin_path)
    dest_filename = os.path.join(dest_path, tail)

    with open(dest_filename, 'w') as file:
        json.dump(new_json, file, indent=4)


def convert_json_folder(input_path: str, dest_path: str):
    obj = os.scandir(input_path)
    dir_list = [entry.name for entry in obj if entry.is_file()]

    for input_file in dir_list:
        filepath = input_path + input_file
        try:
            convert_to_new_format(filepath, dest_path)
        except Exception as exception:
            print(exception)
            print(f"Could not convert {input_file}")
            print()


def test_loading(path: str):
    obj = os.scandir(path)
    dir_list = [entry.name for entry in obj if entry.is_file()]
    for input_file in dir_list:
        filepath = path + input_file
        try:
            _ = Puzzle.fromJSON(filepath)
        except Exception as e:
            print(e)


def clear_old_format_folder(old_path: str, new_path: str):
    obj = os.scandir(old_path)
    old_list = [entry.name for entry in obj if entry.is_file()]

    obj = os.scandir(new_path)
    new_list = [entry.name for entry in obj if entry.is_file()]

    diff = set(old_list).difference(new_list)
    intersect = set(new_list).intersection(old_list)

    print(diff)
    print(len(diff))

    for f in intersect:
        os.remove(old_path + f)


if __name__ == "__main__":
    # path = "./jsonFiles/NewFormat/ContinuousSumSudoku_by_Syhill.json"
    # puzzle = Puzzle.fromJSON(path)

    origin_path = './jsonFiles/OldFormat/'
    dest_path = './jsonFiles/NewFormat/'

    test_loading(dest_path)

    # convert_json_folder(origin_path, dest_path)

    # convert_to_new_format(origin_path, dest_path)
