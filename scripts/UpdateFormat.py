
from puzzlesolver.utils.fileUtils import loadJSON
import os
import json


def update_format(origin_path: str, dest_path: str):
    os.makedirs(dest_path, exist_ok=True)
    (_, tail) = os.path.split(origin_path)
    dest_filename = os.path.join(dest_path, tail)

    old_json = loadJSON(origin_path)
    new_json = old_json
    # new_json = update_outside_edge_constraints(old_json)

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
