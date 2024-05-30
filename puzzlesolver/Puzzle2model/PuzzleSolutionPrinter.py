import time
from ortools.sat.python import cp_model

from puzzlesolver.Puzzle.Puzzle import Puzzle
from puzzlesolver.Puzzle2model.PuzzleModel import PuzzleModel
from puzzlesolver.Puzzle2model.puzzle_model_types import AdjacencyDict, AdjacencyVarsDict, GridVars, build_adjacency_dict

MAX_SOLS = 20


def is_fully_orthogonally_connected_group(node_dict: dict[tuple[int, int], int],
                                          adjacency_dict: AdjacencyDict, target_val: int) -> bool:
    visited_dict: dict[tuple[int, int], bool] = dict()
    for node in adjacency_dict.keys():
        visited_dict[node] = False

    islands: list[set[tuple[int, int]]] = []

    def dfs(curr_node: tuple[int, int], _island: set[tuple[int, int]]):
        visited_dict[curr_node] = True
        _island.add(curr_node)

        adjacent_nodes = adjacency_dict.get(curr_node)

        if adjacent_nodes is None:
            return

        for adjacent_node in adjacent_nodes:
            visited = visited_dict.get(adjacent_node)
            _value = node_dict.get(adjacent_node)
            if visited or _value != target_val:
                continue
            dfs(adjacent_node, _island)

    for node, value in node_dict.items():
        if value == target_val and not visited_dict.get(node):
            island: set[tuple[int, int]] = set()
            islands.append(island)
            dfs(node, island)

    return len(islands) == 1


def get_grid_str(grid_value_dict: dict[tuple[int, int], int]) -> str:
    grid_str = ""
    max_val = max(grid_value_dict.values())
    min_val = min(grid_value_dict.values())
    max_length = max(len(f"{max_val}"), len(f"{min_val}"))

    rows_min = min([i for (i, _) in grid_value_dict.keys()])
    cols_min = min([j for (_, j) in grid_value_dict.keys()])
    rows_max = max([i for (i, _) in grid_value_dict.keys()])
    cols_max = max([j for (_, j) in grid_value_dict.keys()])

    for i in range(rows_min, rows_max + 1):
        line_str = '[ '
        line_divider = "+"
        for j in range(cols_min, cols_max + 1):
            value = grid_value_dict.get((i, j))
            value_str = "{:{field_size}d}".format(value,
                                                  field_size=max_length) if value is not None else ' ' * max_length
            line_str += value_str
            line_divider += '-' * (max_length + 2) + '+'
            if j != cols_max:
                line_str += ' | '
        line_str += ' ]\n'
        line_divider += "\n"
        grid_str += line_str
    return grid_str


def get_adjacencies_grid_str(adjacency_dict: dict[tuple[int, int], dict[tuple[int, int], int]]) -> str:
    grid_str = ""

    n_rows = max([i for (i, _) in adjacency_dict.keys()])
    n_cols = max([j for (_, j) in adjacency_dict.keys()])

    for i in range(0, n_rows + 1):
        line_str = '[ '
        line2_str = '[ '
        for j in range(0, n_cols + 1):
            edges_dict = adjacency_dict.get((i, j))
            is_node = any(edges_dict.values()
                          ) if edges_dict is not None else False
            value_str = '+' if is_node else '·'
            line_str += value_str
            if j != n_cols:
                horizontal_edge = edges_dict.get(
                    (i, j + 1), 0) if edges_dict else 0
                sep = ' - ' if horizontal_edge else '   '
                line_str += sep
            if i != n_rows:
                vertical_edge = edges_dict.get(
                    (i + 1, j), 0) if edges_dict else 0
                value_str = '|' if vertical_edge else ' '
                line2_str += value_str
                if j != n_cols:
                    sep = '   '
                    line2_str += sep
        line_str += ' ]\n'
        line2_str += ' ]\n'
        grid_str += line_str
        if i != n_rows:
            grid_str += line2_str
    return grid_str


def are_solutions_equal(solution1: dict[tuple[int, int], int], solution2: dict[tuple[int, int], int]) -> bool:
    for key, val in solution1.items():
        val2 = solution2.get(key)
        if val2 is None:
            return False
        if val != val2:
            return False
    return True


class SolutionPrinterOptions:
    solution_filename: str = ""
    log_solutions: bool = True
    max_sols: int = MAX_SOLS

    def __init__(self, max_sols: int = MAX_SOLS, log_solutions: bool = True,
                 solution_filename: str = "") -> None:
        self.max_sols = max_sols
        self.log_solutions = log_solutions
        self.solution_filename = solution_filename


DEFAULT_OPTIONS = SolutionPrinterOptions()


class PuzzleSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""
    _start_time: float
    _grid_vars_dict: dict[str, GridVars]
    _adjacency_vars_dicts: dict[str, AdjacencyVarsDict]
    _puzzle: Puzzle
    _max_sols: int
    _solution_count: int
    _unique_solution_count: int
    _log_solutions: bool
    _solution_filename: str

    def __init__(self, puzzle_model: PuzzleModel, puzzle: Puzzle,
                 options: SolutionPrinterOptions = DEFAULT_OPTIONS):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._grid_vars_dict = puzzle_model.grid_vars_dict
        self._adjacency_vars_dicts = puzzle_model.adjacency_vars_dicts
        self._start_time = time.time()
        self._puzzle = puzzle
        self.__adjacency_dict = build_adjacency_dict(puzzle.grid)
        self.__solution_store: list[dict[tuple[int, int], int]] = []
        self.__variables_record = puzzle_model.get_variable_record()
        self._max_sols = options.max_sols
        self._solution_count = 0
        self._unique_solution_count = 0
        self._solution_filename = options.solution_filename
        self._log_solutions = options.log_solutions

    def var_grid_dict_to_value_grid_dict(self, grid_var_dict: GridVars) -> dict[tuple[int, int], int]:
        value_grid_dict: dict[tuple[int, int], int] = dict()
        for key, var in grid_var_dict.items():
            value_grid_dict[key] = self.Value(var)
        return value_grid_dict

    def evaluate_adjacency_vars_dict(self, adjacency_vars_dict: AdjacencyVarsDict) \
            -> dict[tuple[int, int], dict[tuple[int, int], int]]:
        adjacency_values_dict: dict[tuple[int, int],
                                    dict[tuple[int, int], int]] = dict()
        for node1, edges_dict in adjacency_vars_dict.items():
            adjacency_values_dict[node1] = dict()
            edges_values_dict = adjacency_values_dict[node1]
            for node2, var in edges_dict.items():
                edges_values_dict[node2] = self.Value(var)

        return adjacency_values_dict

    def verify_orthogonally_connected_constraints(self) -> bool:
        # binary connected grids
        dict_ids = ["yin_yang_grid", "two_contiguous_regions_grid"]
        for dict_id in dict_ids:
            if dict_id not in self._grid_vars_dict:
                continue

            grid_dict = self._grid_vars_dict[dict_id]
            values_dict = self.var_grid_dict_to_value_grid_dict(grid_dict)
            orthogonally_connected_1s = is_fully_orthogonally_connected_group(
                values_dict, self.__adjacency_dict, 1)
            orthogonally_connected_0s = is_fully_orthogonally_connected_group(
                values_dict, self.__adjacency_dict, 0)

            if not orthogonally_connected_1s or not orthogonally_connected_0s:
                return False

        if "inside_outside_edge_loop_dict" in self._grid_vars_dict:
            inside_outside_edge_loop_dict = self._grid_vars_dict['inside_outside_edge_loop_dict']
            values_dict = self.var_grid_dict_to_value_grid_dict(
                inside_outside_edge_loop_dict)
            orthogonally_connected_1s = is_fully_orthogonally_connected_group(
                values_dict, self.__adjacency_dict, 1)

            if not orthogonally_connected_1s:
                return False

        if "snake_grid" in self._grid_vars_dict:
            snake_dict = self._grid_vars_dict['snake_grid']
            values_dict = self.var_grid_dict_to_value_grid_dict(snake_dict)
            orthogonally_connected_1s = is_fully_orthogonally_connected_group(
                values_dict, self.__adjacency_dict, 1)

            if not orthogonally_connected_1s:
                return False

        if "regions_grid" in self._grid_vars_dict:
            regions_dict = self._grid_vars_dict['regions_grid']
            values_dict = self.var_grid_dict_to_value_grid_dict(regions_dict)

            orthogonally_connected_vals: list[bool] = []
            for region_val in range(9):
                orthogonally_connected = is_fully_orthogonally_connected_group(values_dict, self.__adjacency_dict,
                                                                               region_val)
                orthogonally_connected_vals.append(orthogonally_connected)

            if not all(orthogonally_connected_vals):
                return False

        return True

    def log_solution(self):
        if not self._log_solutions:
            return

        filepath = f"./Logs/{self._solution_filename}_{self.solution_count()}.sol" if len(
            self._solution_filename) else f"./Logs/solution_{self.solution_count()}.sol"

        with open(filepath, 'w') as file:
            current_time = time.time()
            file.write(
                f'Solution {self._solution_count}, time = {current_time - self._start_time} s\n')

            cells_grid_vars = self._grid_vars_dict['cells_grid_vars']
            grid_value_dict = self.var_grid_dict_to_value_grid_dict(
                cells_grid_vars)
            grid_str = get_grid_str(grid_value_dict)
            file.write(grid_str)
            file.write('\n')
            for grid_name, grid_var_dict in self._grid_vars_dict.items():
                if grid_name == 'cells_grid_vars':
                    continue
                file.write(grid_name + '\n')
                grid_value_dict = self.var_grid_dict_to_value_grid_dict(
                    grid_var_dict)
                grid_str = get_grid_str(grid_value_dict)
                file.write(grid_str)
                file.write('\n')

            for dict_name, adjacency_dict in self._adjacency_vars_dicts.items():
                _adjacency_values_dict = self.evaluate_adjacency_vars_dict(
                    adjacency_dict)
                adjacencies_str = get_adjacencies_grid_str(
                    _adjacency_values_dict)
                file.write(dict_name + '\n')
                file.write(adjacencies_str)
                file.write('\n')

            for key, var in self.__variables_record.items():
                file.write(f"{key} = {self.Value(var)}\n")

            file.write(
                '+--------------------------------------------------------------+\n\n')

    def print_vars(self):
        for key, _grid in self._grid_vars_dict.items():
            if key == 'cells_grid_vars':
                continue

            print(key)
            print(get_grid_str(self.var_grid_dict_to_value_grid_dict(_grid)))
            print()

        edges_dict_names = ["loop_edges_dict"]
        for adjacencies_name in edges_dict_names:
            if adjacencies_name not in self._adjacency_vars_dicts:
                continue
            _adjacency_dict = self._adjacency_vars_dicts[adjacencies_name]
            _adjacency_values_dict = self.evaluate_adjacency_vars_dict(
                _adjacency_dict)
            adjacencies_str = get_adjacencies_grid_str(_adjacency_values_dict)
            print(adjacencies_name)
            print(adjacencies_str)
            print()

    def OnSolutionCallback(self):
        # satisfied = self.verify_orthogonally_connected_constraints()
        # if not satisfied:
        #     return

        self._solution_count += 1
        current_time = time.time()
        print(
            f'Solution {self._solution_count}, time = {current_time - self._start_time} s')

        cells_grid_vars = self._grid_vars_dict['cells_grid_vars']
        solution = self.var_grid_dict_to_value_grid_dict(cells_grid_vars)
        print(get_grid_str(solution))
        print()
        self.print_vars()

        self.log_solution()

        if self._solution_count > 1:
            already_in_store = any([are_solutions_equal(
                solution, solution2) for solution2 in self.__solution_store])
            if not already_in_store:
                self.__solution_store.append(solution)
                self._unique_solution_count += 1
        else:
            self.__solution_store.append(solution)
            self._unique_solution_count += 1

        if self._solution_count >= self._max_sols:
            self.StopSearch()

    def solution_count(self):
        return self._solution_count

    def unique_solution_count(self):
        return self._unique_solution_count

    def solution_store(self):
        return self.__solution_store


def puzzle_print_statistics(solver: cp_model.CpSolver, solution_printer: PuzzleSolutionPrinter):
    # Statistics.
    print('\nStatistics')
    print(f'  conflicts      : {solver.NumConflicts()}')
    print(f'  branches       : {solver.NumBranches()}')
    print(f'  wall time      : {solver.WallTime()} s')
    print(f'  solutions found: {solution_printer.solution_count()}')
    print(
        f'  unique solutions found: {solution_printer.unique_solution_count()}')
    print()
