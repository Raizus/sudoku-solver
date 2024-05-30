import re
from typing import Union, Tuple


def parse_variable(string: str) -> str | None:
    pattern = r'^[a-zA-z]\w*$'
    match = re.match(pattern, string)
    if match is not None:
        return string
    return None


def look_and_say_parse_string(string: str) -> dict[int, int]:
    counts: dict[int, int] = dict()
    matches = re.findall(r"([0-9]{2})", string)

    for match in matches:
        count = parse_int(match[0])
        value = parse_int(match[1])

        if count is not None and value is not None:
            counts[value] = count

    return counts


def parse_int(value: Union[str, int, None]) -> Union[int, None]:
    if value is not None:
        try:
            return int(value)
        except ValueError:
            return None
    return None


def parse_list_int(value: Union[str, None]) -> Union[list[int], None]:
    if value is None:
        return None

    int_list: list[int] = []
    values = value.split(',')
    values = [v.replace(" ", "") for v in values]

    for v in values:
        try:
            int_v = int(v)
            int_list.append(int_v)
        except ValueError:
            return None
    return int_list


def parse_list_int_or_var(value: Union[str, None]):
    if value is None:
        return None

    var_list: list[int] | list[str] | list[int | str] = []
    values = value.split(',')
    values = [v.replace(" ", "") for v in values]

    for v in values:
        try:
            int_v = int(v)
            var_list.append(int_v)
        except ValueError:
            var_v = parse_variable(v)
            if var_v is None:
                return None
            var_list.append(var_v)

    return var_list


class Interval:
    lower_bound: Tuple[str, int] | None = None
    upper_bound: Tuple[str, int] | None = None

    def __init__(self, lower_bound: Tuple[str, int] | None = None,
                 upper_bound: Tuple[str, int] | None = None):
        if lower_bound and lower_bound[0] in ['>', '>=']:
            self.lower_bound = (lower_bound[0], int(lower_bound[1]))
        if upper_bound and upper_bound[0] in ['<', '<=']:
            self.upper_bound = (upper_bound[0], int(upper_bound[1]))


def interval_from_str(value: str) -> Union[Interval, None]:
    g1 = r'(\<|\>|\<\=|\>\=)'
    g2 = r'(\d+|[a-zA-Z]\w*)'
    pattern1 = f'{g1}\\s*{g2}'
    match = re.search(pattern1, value)
    interval = None
    if match:
        sign = match.group(1)
        val = parse_int(match.group(2))
        if sign in ['>', '>='] and val is not None:
            interval = Interval(lower_bound=(sign, val))
        elif sign in ['<', '<='] and val is not None:
            interval = Interval(upper_bound=(sign, val))
    return interval


def parse_value(value: Union[str, int, None]) -> int | Interval | list[int] | list[int | str] | None:
    if isinstance(value, int):
        return value

    val = parse_int(value)
    if val is not None:
        return val

    val = parse_list_int(value)
    if val is not None and len(val):
        return val

    val = parse_list_int_or_var(value)
    if val is not None and len(val):
        return val

        # interval
    if isinstance(value, str):
        pattern = r'([\<\>])(\d+)'
        match = re.search(pattern, value)
        if match:
            return interval_from_str(value)

    return None
