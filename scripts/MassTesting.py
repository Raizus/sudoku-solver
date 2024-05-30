# This is a sample Python script.
import json
from typing import Any, Iterable, Literal

from ortools.sat.python.cp_model import CpSolver

import os
import random
import shutil

from puzzlesolver.Puzzle2model.PuzzleSolutionPrinter import PuzzleSolutionPrinter, puzzle_print_statistics
from puzzlesolver.SolvePuzzle import SolverOptions, solve_puzzle

MAX_TIME = 120
MAX_SOLS = 20
LOG_SOLUTIONS = False

DEFAULT_OPTIONS = SolverOptions(MAX_TIME, MAX_SOLS, LOG_SOLUTIONS)


class TestResults:
    n: int = 0
    file_list: list[str] = []
    times: list[float] = []
    solved_single_solution: list[str] = []
    solved_single_unique_solution: list[str] = []
    multiple_solutions: list[str] = []
    unsolved_out_of_time: list[str] = []
    no_solutions: list[str] = []

    def update(self, file: str, solver: CpSolver, solution_printer: PuzzleSolutionPrinter):
        max_time = solver.parameters.max_time_in_seconds
        wall_time = solver.WallTime()
        unique_solutions = solution_printer.unique_solution_count()
        solution_count = solution_printer.solution_count()

        self.file_list.append(file)
        self.times.append(wall_time)
        self.n += 1

        if wall_time > MAX_TIME:
            self.unsolved_out_of_time.append(file)
        elif solution_count == 1 and wall_time < max_time:
            self.solved_single_solution.append(file)
        elif unique_solutions == 1 and wall_time < max_time:
            self.solved_single_unique_solution.append(file)
        elif solution_count == 0 and wall_time < max_time:
            self.no_solutions.append(file)
        elif solution_count > 1:
            self.multiple_solutions.append(file)
        else:
            self.no_solutions.append(file)

    def print(self):
        if len(self.solved_single_solution) == self.n:
            print(f'All puzzles ({len(self.solved_single_solution)}) solved!!')
            return

        if self.solved_single_solution:
            print(
                f'Puzzles solved with single solution: {len(self.solved_single_solution)}: ')
            for file in self.solved_single_solution:
                print(f'    {file}')
        if self.solved_single_unique_solution:
            print(f'Puzzles solved with single unique solution, but multiple solutions: '
                  f'{len(self.solved_single_unique_solution)}')
            for file in self.solved_single_unique_solution:
                print(f'    {file}')
            print()
        if self.no_solutions:
            print(f'Puzzles with no solutions.'
                  f'{len(self.no_solutions)}')
            for file in self.no_solutions:
                print(f'    {file}')
            print()
        if self.unsolved_out_of_time:
            print(
                f'Puzzles not solved, solver run out of time: {len(self.unsolved_out_of_time)}')
            for file in self.unsolved_out_of_time:
                print(f'    {file}')
            print()
        if self.multiple_solutions:
            print(
                f'Puzzles solved with multiple solutions: {len(self.multiple_solutions)}')
            for file in self.multiple_solutions:
                print(f'    {file}')

    def save_to_json(self):
        data: dict[str, Any] = dict()
        for key in dir(self):
            if not key.startswith('__') and not callable(getattr(self, key)):
                data[key] = getattr(self, key)

        output_file = './Logs/test_results.json'
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)


def mass_test_puzzles(filepaths: Iterable[str], options: SolverOptions = DEFAULT_OPTIONS):
    results = TestResults()

    # for file in filepaths:
    #     print(file)

    for filepath in filepaths:
        try:
            solver_and_sol_printer = solve_puzzle(filepath, options)
        except:
            continue

        solver, solution_printer = solver_and_sol_printer
        puzzle_print_statistics(solver, solution_printer)
        results.update(filepath, solver, solution_printer)

    return results


def test_in_path(path: str):
    obj = os.scandir(path)
    _filepaths = [path + entry.name for entry in obj if entry.is_file()]

    results = mass_test_puzzles(_filepaths)
    results.print()
    results.save_to_json()


def select_random_json_files(directory: str, n: int):
    json_files = [file for file in os.listdir(
        directory) if file.endswith('.json')]
    if len(json_files) < n:
        print(
            f"Warning: There are only {len(json_files)} JSON files in the directory.")

    selected_files = random.sample(json_files, n)
    selected_paths = [os.path.join(directory, file) for file in selected_files]
    return selected_paths


def solve_random_in_dir(directory: str, n: int):
    paths = select_random_json_files(directory, n)
    results = mass_test_puzzles(paths)
    results.print()
    results.save_to_json()


def test_and_move(origin_path: str, dest_path: str,
                  mode: Literal['Solved', 'No Solution'] = "Solved"):
    """
    Tests all files in the origin path folder and moves the ones that match mode into the destination folder

    Args:
        origin_path (str): _description_
        dest_path (str): _description_
        mode (Literal['Solved', 'No Solution'], optional): Defaults to "Solved".
    """
    results = TestResults()
    obj = os.scandir(origin_path)
    _filepaths = [origin_path + entry.name for entry in obj if entry.is_file()]

    # n = 10
    # selected = random.sample(_filepaths, min(n, len(_filepaths)))
    max_time = 120
    options = SolverOptions(max_time=max_time)

    for filepath in _filepaths:
        try:
            solver_and_sol_printer = solve_puzzle(filepath, options)
        except:
            continue

        solver, solution_printer = solver_and_sol_printer
        puzzle_print_statistics(solver, solution_printer)

        results.update(filepath, solver, solution_printer)

        wall_time = solver.WallTime()
        solution_count = solution_printer.solution_count()

        if mode == 'Solved':
            if solution_count == 1 and wall_time < max_time:
                print(f"Moving {filepath}")
                (_, tail) = os.path.split(filepath)
                # (filename, extension) = os.path.splitext(tail)
                filepath_dst = dest_path + tail
                shutil.move(filepath, filepath_dst)
        elif mode == 'No Solution':
            if solution_count == 0 and wall_time < max_time:
                print(f"Moving {filepath}")
                (_, tail) = os.path.split(filepath)
                # (filename, extension) = os.path.splitext(tail)
                filepath_dst = dest_path + tail
                shutil.move(filepath, filepath_dst)


if __name__ == '__main__':
    path = './jsonFiles/Solved/'
    test_in_path(path)

    # origin_path = './jsonFiles/NewFormat/'
    # dest_path = './jsonFiles/Solved/'
    # test_and_move(origin_path, dest_path)

    # obj = os.scandir(path)
    # _filepaths = [path + entry.name for entry in obj if entry.is_file()]
