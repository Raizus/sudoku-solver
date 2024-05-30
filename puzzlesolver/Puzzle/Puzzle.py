
from typing import Any
from puzzlesolver.Puzzle.GlobalConstraints import load_bool_constraints
from puzzlesolver.Puzzle.Grid import Grid
from puzzlesolver.Puzzle.ConstraintEnums import BoolToolEnum
from puzzlesolver.Puzzle.ToolConstraints import ToolConstraints

from puzzlesolver.utils.fileUtils import loadJSON


class PuzzleMeta:
    title: str
    authors: list[str]
    ruleset: str
    ctc_url: str
    youtube_url: str

    def __init__(self, title: str = "Sudoku", authors: list[str] = ["Anonymous"],
                 ruleset: str = "", ctc_url: str = "", youtube_url: str = "") -> None:
        self.title = title
        self.authors = authors
        self.ruleset = ruleset
        self.ctc_url = ctc_url
        self.youtube_url = youtube_url

    @classmethod
    def fromJson(cls, data: dict[str, Any]):
        title: str = data.get('title', 'Sudoku')
        authors: list[str] = data.get('authors', ["Anonymous"])
        ruleset: str = data.get('ruleset', "")
        ctc_url: str = data.get('ctcUrl', "")
        youtube_url: str = data.get('ctcYoutubeUrl', "")

        return PuzzleMeta(title, authors, ruleset, ctc_url, youtube_url)


class Puzzle:
    tool_constraints: ToolConstraints
    bool_constraints: dict[BoolToolEnum, bool]
    puzzle_meta: PuzzleMeta
    _nRows: int
    _nCols: int
    grid: Grid
    valid_digits: list[int]

    def __init__(self, nRows: int, nCols: int) -> None:
        self._nCols = nCols
        self._nRows = nRows
        self.grid = Grid(nRows, nCols)
        n = min(nRows, nCols, 9)
        self.valid_digits = list(range(1, n+1))
        self.bool_constraints = dict()
        self.puzzle_meta = PuzzleMeta()

    @classmethod
    def fromJSON(cls, pathToFile: str):
        data = loadJSON(pathToFile)
        nrows: int = data['nRows']
        ncols: int = data['nCols']
        puzzle_meta = PuzzleMeta.fromJson(data['puzzleInfo'])
        grid_data: list[list[dict[Any, Any]]] = data['grid']

        grid = Grid.fromJSON(nrows, ncols, grid_data)

        tool_constraints = ToolConstraints.load_tool_constraints(
            data['local_constraints'])  #
        bool_constraints = load_bool_constraints(data['bool_constraints'])  #

        puzzle = Puzzle(nrows, ncols)
        puzzle.grid = grid
        puzzle.tool_constraints = tool_constraints
        puzzle.bool_constraints = bool_constraints
        puzzle.puzzle_meta = puzzle_meta

        if 'valid_digits' in data:
            puzzle.valid_digits = data['valid_digits']

        return puzzle
