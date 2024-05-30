import os

from ortools.sat.python import cp_model
import argparse

from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleSolutionPrinter import PuzzleSolutionPrinter, SolutionPrinterOptions, puzzle_print_statistics
from puzzlesolver.Puzzle2model.puzzle2model import puzzle2model

MAX_TIME = 240
MAX_SOLS = 20
LOG_SOLUTIONS = False


class SolverOptions:
    max_time: int  # time in seconds
    max_sols: int
    log_solutions: bool

    def __init__(self, max_time: int = MAX_TIME, max_sols: int = MAX_SOLS,
                 log_solutions: bool = LOG_SOLUTIONS) -> None:
        """

        Args:
            max_time (int, optional): Defaults to MAX_TIME = 240.
            max_sols (int, optional): Defaults to MAX_SOLS = 20.
            log_solutions (bool, optional): Defaults to LOG_SOLUTIONS = False.
        """
        self.max_time = max_time
        self.max_sols = max_sols
        self.log_solutions = log_solutions


DEFAULT_OPTIONS = SolverOptions()


def load_puzzle(str_fp: str):
    try:
        puzzle = Puzzle.fromJSON(str_fp)
        return puzzle
    except FileNotFoundError as e:
        print(f"Error: File {str_fp} not found.")
        raise e
    except Exception as e:
        print(e)
        raise e


def solve_puzzle(str_fp: str, options: SolverOptions = DEFAULT_OPTIONS):
    puzzle = load_puzzle(str_fp)

    puzzle_meta = puzzle.puzzle_meta
    print(
        f"Building puzzle model for {puzzle_meta.title} by {', '.join(puzzle_meta.authors)}\n")
    puzzle_model = puzzle2model(puzzle)

    (_, tail) = os.path.split(str_fp)
    (filename, _) = os.path.splitext(tail)
    printer_options = SolutionPrinterOptions(
        options.max_sols, options.log_solutions, filename)

    solution_printer = PuzzleSolutionPrinter(
        puzzle_model, puzzle, printer_options)

    max_time = options.max_time
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.max_time_in_seconds = max_time
    print(f"Solving {puzzle_meta.title} by {', '.join(puzzle_meta.authors)}")
    solver.Solve(puzzle_model, solution_printer)

    puzzle_print_statistics(solver, solution_printer)

    return solver, solution_printer


def make_parser():
    description = """
    A CP-SAT solver for sudoku variants.
"""

    parser = argparse.ArgumentParser(
        description=description)
    parser.add_argument('filepath', type=str, nargs='+',
                        help='the path to the sudoku file, files, or folder')
    parser.add_argument('--max_time', dest='max_time', default=MAX_TIME, type=int,
                        help=f'the maximum time (in seconds) the solver will '
                             f'search for a solution. Default is {MAX_TIME} s.')
    parser.add_argument('--max_sols', dest='max_sols', default=MAX_SOLS, type=int,
                        help='the maximum number of solution the solver will search for. '
                             f'After the solver reaches the maximum, '
                             f'it will stop. Default is {MAX_SOLS}.')
    parser.add_argument('-l', '--log_solutions', dest='log_solutions', action="store_true",
                        help=f'flag indicating if solutions should be logged')
    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    fpath = args.filepath
    _max_time = args.max_time
    _max_sols = args.max_sols
    _log_solutions = args.log_solutions
    options = SolverOptions(_max_time, _max_sols, _log_solutions)

    if len(fpath) == 1 and os.path.isdir(fpath[0]):
        obj = os.scandir(fpath[0])
        fpath = [entry.path for entry in obj if entry.is_file(
        ) and os.path.splitext(entry.name)[1] == ".json"]

    for _fp in fpath:
        solve_puzzle(_fp, options)
