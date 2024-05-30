from typing import TypeVar, Union, List

T = TypeVar("T")


def get_adjacent(line: list[T], target: T) -> list[T]:
    adjacent: list[T] = []
    if target not in line:
        return adjacent
    idx = line.index(target)
    if idx - 1 >= 0:
        adjacent.append(line[idx - 1])
    if idx + 1 < len(line):
        adjacent.append(line[idx + 1])
    return adjacent


def get_extremes(line: List[T]) -> List[T]:
    extremes: List[T] = []
    if len(line) >= 2:
        return [line[0], line[-1]]
    return extremes


def get_middle(line: List[T]) -> List[T]:
    middle: List[T] = []
    if len(line) > 2:
        return line[1:-1]
    return middle


def get_left_side(line: List[T], idx: int) -> List[T]:
    left_side: List[T] = []
    if 0 < idx < len(line):
        return line[0:idx]
    return left_side


def get_right_side(line: List[T], idx: int) -> List[T]:
    right_side: List[T] = []
    if 0 <= idx < len(line) - 1:
        return line[idx + 1:]
    return right_side


def get_opposite_value(line: List[T], value: T) -> Union[T, None]:
    if not len(line):
        return None

    if value in line:
        idx = line.index(value)
        opp_idx = len(line) - idx - 1
        return line[opp_idx]

    return None


def generate_list_kmers(line: list[T], k: int, closed: bool = False):
    l = len(line)

    for i in range(0, l-k+1):
        aux = line[i:i+k]
        yield aux

    if closed:
        for i in range(l-k+1, l):
            aux = line[i:] + line[:(i+k) % l]
            yield aux
