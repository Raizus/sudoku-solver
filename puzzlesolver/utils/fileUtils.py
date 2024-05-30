
import json
import os
from typing import Any


def loadJSON(pathToFile: str) -> dict[str, Any]:
    """
    Loads a json and returns the corresponding dictionary object

    :param path_to_file:
    :return:
    """
    if os.path.isfile(pathToFile):
        split_tup = os.path.splitext(pathToFile)
        if split_tup[1] != '.json':
            raise Exception("File extension must be .json")
    try:
        with open(pathToFile) as f:
            data = json.load(f)
            if isinstance(data, str):
                data = json.loads(data)

        return data
    except FileNotFoundError as fnf_error:
        raise fnf_error
