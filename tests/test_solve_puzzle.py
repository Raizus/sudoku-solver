import pytest
import random
import os

from puzzlesolver.SolvePuzzle import SolverOptions, solve_puzzle


class TestSolvePuzzle:

    @staticmethod
    def generate_all_fp():
        path = './data/Solved/'
        obj = os.scandir(path)
        filepaths = [os.path.join(path, entry.name)
                     for entry in obj if entry.is_file()]
        return filepaths

    @staticmethod
    def generate_random_fp():
        random.seed(42)
        path: str = './data/Solved/'
        n: int = 10
        obj = os.scandir(path)
        filepaths = [os.path.join(path, entry.name)
                     for entry in obj if entry.is_file()]
        n = min(n, len(filepaths))
        filepaths = random.sample(filepaths, n)
        return filepaths

    def run_test(self, filepath: str, max_time: int = 120):
        options = SolverOptions(max_time=max_time)

        try:
            solver_and_sol_printer = solve_puzzle(filepath, options)
        except:
            pytest.fail(f"Unable to solve puzzle at {filepath}")

        solver, solution_printer = solver_and_sol_printer

        wall_time = solver.WallTime()
        solution_count = solution_printer.solution_count()
        unique_solution_count = solution_printer.unique_solution_count()
        if wall_time >= max_time:
            pytest.fail(f"Could not solve {filepath}. Ran out of time.")
        elif solution_count == 1:
            assert solution_count == 1
            return
        elif unique_solution_count == 1:
            assert unique_solution_count == 1
            return
        else:
            pytest.fail(f"Solved {filepath} with multiple solutions.")

    @pytest.mark.parametrize("filepath", [('./data/Solved/400kSubscribers_by_PjotrV.json')])
    def test_one(self, filepath: str):
        self.run_test(filepath)

    @pytest.mark.parametrize("filepath", generate_random_fp())
    def test_random(self, filepath: str):
        self.run_test(filepath)

    @pytest.mark.parametrize("filepath", generate_all_fp())
    def test_all(self, filepath: str):
        self.run_test(filepath, 1200)
