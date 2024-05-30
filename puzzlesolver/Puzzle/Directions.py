

from enum import Enum


class DIRECTIONS(Enum):
    N = "N"
    S = "S"
    E = "E"
    W = "W"
    NE = "NE"
    NW = "NW"
    SE = "SE"
    SW = "SW"


OppositeDirection = {
    DIRECTIONS.N: DIRECTIONS.S,
    DIRECTIONS.S: DIRECTIONS.N,
    DIRECTIONS.E: DIRECTIONS.W,
    DIRECTIONS.W: DIRECTIONS.E,
    DIRECTIONS.NE: DIRECTIONS.SW,
    DIRECTIONS.NW: DIRECTIONS.SE,
    DIRECTIONS.SE: DIRECTIONS.NW,
    DIRECTIONS.SW: DIRECTIONS.NE,
}

RCToDirectionDict: dict[tuple[int, int], DIRECTIONS] = {
    (-1, 0): DIRECTIONS.N,
    (1, 0): DIRECTIONS.S,
    (0, 1): DIRECTIONS.E,
    (0, -1): DIRECTIONS.W,
    (-1, 1): DIRECTIONS.NE,
    (-1, -1): DIRECTIONS.NW,
    (1, 1): DIRECTIONS.SE,
    (1, -1): DIRECTIONS.SW,
}

DirectionToRCDict: dict[DIRECTIONS, tuple[int, int]] = {
    DIRECTIONS.N: (-1, 0),
    DIRECTIONS.S: (1, 0),
    DIRECTIONS.E: (0, 1),
    DIRECTIONS.W: (0, -1),
    DIRECTIONS.NE: (-1, 1),
    DIRECTIONS.NW: (-1, -1),
    DIRECTIONS.SE: (1, 1),
    DIRECTIONS.SW: (1, -1),
}


def getCardinalDirections() -> list[DIRECTIONS]:
    return [DIRECTIONS.N, DIRECTIONS.S, DIRECTIONS.E, DIRECTIONS.W]


def getOrdinalDirections() -> list[DIRECTIONS]:
    return [DIRECTIONS.NW, DIRECTIONS.NE, DIRECTIONS.SW, DIRECTIONS.SE]


def getDirections() -> list[DIRECTIONS]:
    return getCardinalDirections() + getOrdinalDirections()


def strToDirections(string: str) -> DIRECTIONS | None:
    for item in DIRECTIONS:
        if string == item.value:
            return item
    return None


def rcToDirection(r: int, c: int) -> DIRECTIONS | None:
    direction = RCToDirectionDict.get((r, c), None)
    return direction


def directionToRC(direction: DIRECTIONS) -> tuple[int, int]:
    rc = DirectionToRCDict[direction]
    return rc


def get_opposite_direction(direction: DIRECTIONS) -> DIRECTIONS:
    return OppositeDirection[direction]
