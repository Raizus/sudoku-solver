import time
from typing import Any

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar

from puzzlesolver.Puzzle2model.custom_constraints import member_of
from puzzlesolver.Puzzle2model.puzzle_model_types import AdjacencyVarsDict, GridVars
from puzzlesolver.utils.ParsingUtils import Interval, parse_value


class ModelWithRecord(cp_model.CpModel):
    _variable_counter: int
    _variable_record: dict[str, IntVar]

    def __init__(self):
        super().__init__()
        self._variable_counter = 0
        self._variable_record = {}

    def NewBoolVar(self, name: Any) -> IntVar:
        new_var = super().NewBoolVar(name)
        record_name = f"{self._variable_counter} - {str(name)}"
        self._variable_record[record_name] = new_var
        self._variable_counter += 1
        return new_var

    def NewIntVar(self, lb: int, ub: int, name: Any) -> IntVar:
        new_var = super().NewIntVar(lb, ub, name)
        record_name = f"{self._variable_counter} - {str(name)}"
        self._variable_record[record_name] = new_var
        self._variable_counter += 1
        return new_var

    def get_variable_record(self):
        return self._variable_record


class ModelWithRecordSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""
    __start_time: float
    __max_sols: int | None = None
    __solution_count: int
    __unique_solution_count: int

    def __init__(self, model: ModelWithRecord, max_sols: int | None = None):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__start_time = time.time()
        self.__variables_record = model.get_variable_record()
        self.__max_sols = max_sols
        self.__solution_count = 0

    def OnSolutionCallback(self):
        self.__solution_count += 1
        current_time = time.time()
        print('Solution %i, time = %f s' %
              (self.__solution_count, current_time - self.__start_time))

        for key, var in self.__variables_record.items():
            print(f"{key} = {self.Value(var)}")

        if self.__max_sols is not None and self.__solution_count >= self.__max_sols:
            self.StopSearch()

    def solution_count(self):
        return self.__solution_count


class PuzzleModel(ModelWithRecord):
    shared_vars_dict: dict[str, IntVar]
    grid_vars_dict: dict[str, GridVars]
    adjacency_vars_dicts: dict[str, AdjacencyVarsDict]

    def __init__(self):
        super().__init__()
        self.shared_vars_dict = dict()
        self.grid_vars_dict = dict()
        self.adjacency_vars_dicts = dict()

    def get_or_set_shared_var(self, value: str | int | None, min_val: int,
                              max_val: int, name: str) -> int | IntVar:
        shared_vars = self.shared_vars_dict

        parsed_value = parse_value(value)

        if isinstance(parsed_value, int):
            return parsed_value

        # integer interval
        if isinstance(parsed_value, Interval):
            var = self.NewIntVar(min_val, max_val, name)
            shared_vars[name] = var

            if parsed_value.lower_bound:
                lb_val = parsed_value.lower_bound[1]
                sign = parsed_value.lower_bound[0]
                if sign == '>':
                    self.Add(var > lb_val)
                elif sign == '>=':
                    self.Add(var >= lb_val)

            if parsed_value.upper_bound:
                ub_val = parsed_value.upper_bound[1]
                sign = parsed_value.upper_bound[0]
                if sign == '<':
                    self.Add(var < ub_val)
                elif sign == '<=':
                    self.Add(var <= ub_val)

            return var

        if isinstance(parsed_value, list):
            int_vals: list[int] = []
            vars: list[IntVar | int] = []
            for v in parsed_value:
                if isinstance(v, int):
                    subvar = v
                    int_vals.append(v)
                elif v in shared_vars:
                    subvar = shared_vars[v]
                else:
                    subvar = self.NewIntVar(min_val, max_val, v)
                    shared_vars[v] = subvar
                vars.append(subvar)

            var = self.NewIntVar(min_val, max_val, name)
            member_of(self, vars, var, f"{name}")

            # lb, ub = min(parsed_value), max(parsed_value)
            # allowed_vals = [(v,) for v in parsed_value]
            # self.AddAllowedAssignments([var], allowed_vals)
            return var

        if value in shared_vars:
            var = shared_vars[value]
            return var

        if name in shared_vars:
            var = shared_vars[name]
            return var

        if isinstance(value, str) and len(value) > 0:
            var = self.NewIntVar(min_val, max_val, value)
            shared_vars[value] = var
        else:
            var = self.NewIntVar(min_val, max_val, name)
            shared_vars[name] = var
        return var
