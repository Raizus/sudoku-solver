from typing import Any, Optional
from puzzlesolver.Puzzle.Coords import GridCoords, areCoordsCage, areCoordsLine, areCornerCoords, areNeighbouringCoords, coordToCellString, sortCoords
from puzzlesolver.Puzzle.ConstraintEnums import LocalToolEnum
from puzzlesolver.Puzzle.Directions import DIRECTIONS, strToDirections


class LocalConstraint:
    type: LocalToolEnum
    constraint_props: dict[str, Any] | None

    def __init__(self, type: LocalToolEnum, constraint_props: dict[str, Any] | None = None) -> None:
        self.type = type
        self.constraint_props = constraint_props


class SingleCellConstraint(LocalConstraint):
    cell: GridCoords
    value: Optional[str]

    def __init__(self, type: LocalToolEnum, cell: GridCoords,
                 value: str | None = None, constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.cell = cell
        self.value = value

    def __repr__(self) -> str:
        _str = f"Cell = {self.cell}."
        if self.value is not None and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum):
        if 'cell' not in json_data:
            raise Exception("Single cell constraints must have cell field.")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        cell: GridCoords = GridCoords.fromString(json_data['cell'])
        value = json_data.get('value', None)

        constraint = SingleCellConstraint(type, cell, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cell'] = coordToCellString(self.cell)
        if self.value is not None:
            data['value'] = self.value
        return data


class SingleCellArrowConstraint(LocalConstraint):
    cell: GridCoords
    value: Optional[str]
    arrow: DIRECTIONS

    def __init__(self, type: LocalToolEnum, cell: GridCoords,
                 arrow: DIRECTIONS, value: str | None = None,
                 constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.cell = cell
        self.arrow = arrow
        self.value = value

    def __repr__(self) -> str:
        _str = f"Cell = {self.cell}."
        temp = f" Arrow = {self.arrow.value}"
        _str += temp

        if self.value is not None and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum):
        if 'cell' not in json_data:
            raise Exception("Single cell constraints must have cell field.")

        cell: GridCoords = GridCoords.fromString(json_data['cell'])
        value = json_data.get('value', None)

        if 'arrow' not in json_data:
            raise Exception(
                "Single cell constraints must have an arrow field.")

        arrow_str = json_data['arrow']
        arrow = strToDirections(arrow_str)
        if arrow is None:
            raise Exception(f"{arrow_str} is not a valid direction.")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = SingleCellArrowConstraint(
            type, cell, arrow, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cell'] = coordToCellString(self.cell)
        data['arrow'] = self.arrow.value
        if self.value is not None:
            data['value'] = self.value
        return data


class SingleCellMultiArrowConstraint(LocalConstraint):
    cell: GridCoords
    value: Optional[str]
    arrows: list[DIRECTIONS]

    def __init__(self, type: LocalToolEnum, cell: GridCoords,
                 arrows: list[DIRECTIONS], value: str | None = None,
                 constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.cell = cell
        self.arrows = arrows
        self.value = value

    def __repr__(self) -> str:
        _str = f"Cell = {self.cell}."
        if len(self.arrows):
            temp = f" Arrows = [" + \
                ', '.join(arrow.value for arrow in self.arrows) + ']'
            _str += temp
        if self.value is not None and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum):
        if 'cell' not in json_data:
            raise Exception("Single cell constraints must have cell field.")

        cell: GridCoords = GridCoords.fromString(json_data['cell'])
        value = json_data.get('value', None)

        if 'arrows' not in json_data:
            raise Exception(
                "Single Cell Multi Arrow constraints must have an arrows field.")

        arrows: list[DIRECTIONS] = []
        data_arrows = json_data['arrows']
        for dir1 in data_arrows:
            dir2 = strToDirections(dir1)
            if dir2 is None:
                raise Exception(f"{dir1} is not a valid direction.")
            arrows.append(dir2)

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = SingleCellMultiArrowConstraint(
            type, cell, arrows, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cell'] = coordToCellString(self.cell)
        if len(self.arrows):
            data['arrows'] = [arrow.value for arrow in self.arrows]
        if self.value is not None:
            data['value'] = self.value
        return data


class EdgeConstraint(LocalConstraint):
    cells: list[GridCoords]
    value: str

    def __init__(self, type: LocalToolEnum, cells: list[GridCoords],
                 value: str = "", constraint_props: dict[str, Any] | None = None) -> None:
        self.type = type
        self.value = value
        if not areNeighbouringCoords(cells):
            raise Exception(
                "EdgeConstraint must receive 2 cells that share an edge.")
        cells = sortCoords(cells)
        self.cells = cells

    def __repr__(self) -> str:
        _str = f"Cells = {self.cells}."
        if len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum):
        if 'cells' not in json_data:
            raise Exception("Edge constraint must have cells")

        cells: list[GridCoords] = [GridCoords.fromString(
            cell_data) for cell_data in json_data['cells']]
        value = json_data.get('value', "")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = EdgeConstraint(type, cells, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cells'] = [coordToCellString(cell) for cell in self.cells]
        data['value'] = self.value
        return data


class CornerConstraint(LocalConstraint):
    cells: list[GridCoords]
    value: Optional[str]

    def __init__(self, type: LocalToolEnum, cells: list[GridCoords],
                 value: str = "", constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.value = value
        cells = sortCoords(cells)
        if not areCornerCoords(cells):
            raise Exception(
                "CornerConstraint must receive 4 cells that share a corner.")
        self.cells = cells

    def __repr__(self) -> str:
        _str = f"Cells = {self.cells}."
        if self.value is not None and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum) -> "CornerConstraint":
        if 'cells' not in json_data:
            raise Exception("Corner constraint must have cells")

        cells: list[GridCoords] = [GridCoords.fromString(
            cell_data) for cell_data in json_data['cells']]
        value = json_data.get('value', "")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = CornerConstraint(type, cells, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cells'] = [coordToCellString(cell) for cell in self.cells]
        data['value'] = self.value
        return data


class LineConstraint(LocalConstraint):
    cells: list[GridCoords]
    value: Optional[str]

    def __init__(self, type: LocalToolEnum, cells: list[GridCoords],
                 value: str | None = None, constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.value = value
        if not areCoordsLine(cells, True):
            raise Exception("LineConstraint cells must form a valid line.")
        self.cells = cells

    def __repr__(self) -> str:
        _str = f"Cells = {self.cells}."
        if self.value is not None and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum) -> "LineConstraint":
        if 'cells' not in json_data:
            raise Exception("Line constraint must have cells")

        cells: list[GridCoords] = [GridCoords.fromString(
            cell_str) for cell_str in json_data['cells']]
        value = json_data.get('value', None)
        value = value if value is None else str(value)

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = LineConstraint(type, cells, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cells'] = [coordToCellString(cell) for cell in self.cells]
        if self.value is not None and len(self.value):
            data['value'] = self.value
        return data


class ArrowConstraint(LocalConstraint):
    cells: list[GridCoords]
    lines: list[list[GridCoords]]
    value: Optional[str]

    def __init__(self, type: LocalToolEnum, cells: list[GridCoords],
                 lines: list[list[GridCoords]], value: str | None = None,
                 constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.value = value
        if not areCoordsLine(cells, False):
            raise Exception("LineConstraint cells must form a valid line.")
        self.lines = []
        for line in lines:
            if not areCoordsLine(line, False):
                raise Exception("LineConstraint line must form a valid arrow.")
            if len(line) <= 1 or line[0] not in cells or any(coord in cells for coord in line[1:]):
                raise Exception("LineConstraint line must form a valid arrow.")
            self.lines.append(line)
        self.cells = cells

    def __repr__(self) -> str:
        _str = f"Cells = {self.cells}. "
        _str += f"Arrows = {self.lines}."
        if self.value is not None and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum) -> "ArrowConstraint":
        if 'cells' not in json_data:
            raise Exception("Arrow constraint must have cells.")
        cells: list[GridCoords] = [GridCoords.fromString(
            cell_data) for cell_data in json_data['cells']]

        if 'lines' not in json_data:
            raise Exception("Arrow constraint must have lines.")
        lines: list[list[GridCoords]] = [[GridCoords.fromString(
            cell_data) for cell_data in line] for line in json_data['lines']]

        value = json_data.get('value', "")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = ArrowConstraint(
            type, cells, lines, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cells'] = [coordToCellString(cell) for cell in self.cells]
        data['lines'] = [[coordToCellString(cell)
                          for cell in line] for line in self.lines]
        if self.value is not None:
            data['value'] = self.value
        return data


class CloneConstraint(LocalConstraint):
    cells: list[GridCoords]
    cells2: list[GridCoords]
    value: Optional[str]

    def __init__(self, type: LocalToolEnum, cells: list[GridCoords], cells2: list[GridCoords],
                 value: str | None = None, constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.cells = cells
        self.cells2 = cells2
        self.value = value

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum) -> "CloneConstraint":
        if 'cells' not in json_data:
            raise Exception("Clone constraint must have cells.")
        cells: list[GridCoords] = [GridCoords.fromString(
            cell_data) for cell_data in json_data['cells']]

        if 'cells2' not in json_data:
            raise Exception("Clone constraint must have cells2.")
        cells2: list[GridCoords] = [GridCoords.fromString(
            cell_data) for cell_data in json_data['cells2']]

        if len(cells) != len(cells2):
            raise Exception(
                "The two regions of clone constraints must have the same size")

        value = json_data.get('value', None)

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constrait = CloneConstraint(
            type, cells, cells2, value, constraint_props)
        return constrait

    def toJsonData(self) -> dict[str, Any]:
        data: dict[str, Any] = dict()
        data['cells'] = [coordToCellString(cell) for cell in self.cells]
        data['cells2'] = [coordToCellString(cell) for cell in self.cells2]

        if self.value is not None:
            data['value'] = self.value

        return data


class CageConstraint(LocalConstraint):
    cells: list[GridCoords]
    value: str

    def __init__(self, type: LocalToolEnum, cells: list[GridCoords],
                 value: str = "", constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.value = value
        if not areCoordsCage(cells):
            raise Exception("CageConstraint cells must form a valid cage.")
        self.cells = cells

    def __repr__(self) -> str:
        _str = f"Cells = {self.cells}."
        if len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum) -> "CageConstraint":
        if 'cells' not in json_data:
            raise Exception("Cage constraint must have cells")

        cells: list[GridCoords] = [GridCoords.fromString(
            cell_data) for cell_data in json_data['cells']]
        value = json_data.get('value', "")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = CageConstraint(type, cells, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cells'] = [coordToCellString(cell) for cell in self.cells]
        data['value'] = self.value
        return data


class OutsideEdgeConstraint(LocalConstraint):
    cell: GridCoords
    direction: DIRECTIONS
    value: Optional[str]

    def __init__(self, type: LocalToolEnum, cell: GridCoords, direction: DIRECTIONS,
                 value: str = "", constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.value = value
        self.cell = cell
        self.direction = direction

    def __repr__(self) -> str:
        _str = f"Cell = {self.cell}. Direction = {self.direction.value}."
        if self.value and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum) -> "OutsideEdgeConstraint":
        if 'cell' not in json_data:
            raise Exception("Outside Edge constraint must have a cell")

        cell: GridCoords = GridCoords.fromString(json_data['cell'])
        value = json_data.get('value', "")

        # direction: DIRECTIONS | None = None
        # if cell.r < cell.c and cell.r <= 1:
        #     direction = DIRECTIONS.S
        # if cell.r > cell.c and cell.r >= 9:
        #     direction = DIRECTIONS.N

        # if cell.c < cell.r and cell.c <= 1:
        #     direction = DIRECTIONS.E
        # if cell.c > cell.r and cell.c >= 9:
        #     direction = DIRECTIONS.W

        if 'direction' not in json_data:
            raise Exception(
                "Outside Corner constraints must have a direction field.")

        direction_str = json_data['direction']
        direction = strToDirections(direction_str)
        if direction is None:
            raise Exception(f"{direction_str} is not a valid direction.")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = OutsideEdgeConstraint(
            type, cell, direction, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cell'] = coordToCellString(self.cell)
        data['direction'] = self.direction.value
        if self.value is not None:
            data['value'] = self.value
        return data


class OutsideCornerConstraint(LocalConstraint):
    cell: GridCoords
    direction: DIRECTIONS
    value: Optional[str]

    def __init__(self, type: LocalToolEnum, cell: GridCoords, direction: DIRECTIONS,
                 value: str = "", constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.value = value
        self.cell = cell
        self.direction = direction

    def __repr__(self) -> str:
        _str = f"Cell = {self.cell}. Direction = {self.direction.value}."
        if self.value and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum) -> "OutsideCornerConstraint":
        if 'cell' not in json_data:
            raise Exception("Outside Edge constraint must have a cell")

        cell: GridCoords = GridCoords.fromString(json_data['cell'])
        value = json_data.get('value', "")

        if 'direction' not in json_data:
            raise Exception(
                "Outside Corner constraints must have a direction field.")

        direction_str = json_data['direction']
        direction = strToDirections(direction_str)
        if direction is None:
            raise Exception(f"{direction_str} is not a valid direction.")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = OutsideCornerConstraint(
            type, cell, direction, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['cell'] = coordToCellString(self.cell)
        data['direction'] = self.direction.value
        if self.value is not None:
            data['value'] = self.value
        return data


class ValuedGlobalConstraint(LocalConstraint):
    value: str

    def __init__(self, type: LocalToolEnum, value: str,
                 constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.value = value

    def __repr__(self) -> str:
        _str = f"Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum):
        value = json_data.get('value', None)

        if value is None:
            raise Exception("ValuedGlobalConstraint must contain a value")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = ValuedGlobalConstraint(type, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['value'] = self.value
        return data


class DoubleValuedGlobalConstraint(LocalConstraint):
    value1: str
    value2: str

    def __init__(self, type: LocalToolEnum, value1: str, value2: str,
                 constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.value1 = value1
        self.value2 = value2

    def __repr__(self) -> str:
        _str = f"Value1 = {self.value1}, Value2 = {self.value2}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum):
        value1 = json_data.get('value1', None)
        if value1 is None:
            raise Exception("ValuedGlobalConstraint must contain a value1")

        value2 = json_data.get('value2', None)
        if value2 is None:
            raise Exception("ValuedGlobalConstraint must contain a value2")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        constraint = DoubleValuedGlobalConstraint(
            type, value1, value2, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['value1'] = self.value1
        data['value2'] = self.value2
        return data


class RCConstraint(LocalConstraint):
    coords: GridCoords
    value: Optional[str]

    def __init__(self, type: LocalToolEnum, coords: GridCoords,
                 value: str | None = None, constraint_props: dict[str, Any] | None = None) -> None:
        super().__init__(type, constraint_props)
        self.coords = coords
        self.value = value

    def __repr__(self) -> str:
        _str = f"Coords = {self.coords}."
        if self.value is not None and len(self.value):
            _str += f" Value = {self.value}"
        return _str

    @classmethod
    def fromJsonData(cls, json_data: dict[Any, Any], type: LocalToolEnum):
        if 'r' not in json_data:
            raise Exception("Single cell constraints must have r field.")
        if 'c' not in json_data:
            raise Exception("Single cell constraints must have c field.")

        constraint_props: None | dict[str, Any] = json_data.get(
            'constraintProps', None)

        coords: GridCoords = GridCoords(json_data['r'], json_data['c'])
        value = json_data.get('value', None)

        constraint = RCConstraint(type, coords, value, constraint_props)
        return constraint

    def toJsonData(self):
        data: dict[str, Any] = dict()
        data['r'] = self.coords.r
        data['c'] = self.coords.c
        if self.value is not None:
            data['value'] = self.value
        return data


Constraint = SingleCellConstraint | SingleCellArrowConstraint | SingleCellMultiArrowConstraint | EdgeConstraint | CornerConstraint | LineConstraint | ArrowConstraint | CageConstraint | CloneConstraint | OutsideEdgeConstraint | OutsideCornerConstraint | ValuedGlobalConstraint | DoubleValuedGlobalConstraint | RCConstraint
