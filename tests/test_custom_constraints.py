import pytest

from puzzlesolver.Puzzle2model.custom_constraints import are_all_diferent_csp, are_all_equal_csp, are_all_true_csp, are_any_true_csp, are_consecutive_csp, count_different_vars, count_in_set, count_transitions_csp, count_unique_values, count_vars, distance_csp, first_x_bools_csp, greater_than_all_csp, is_even_csp, is_increasing_strict_csp, is_inside_interval_2_csp, is_member_of, is_not_member_of, is_odd_csp, is_renban_csp, is_sandwiched_csp, is_whispers_csp, masked_count_vars, masked_sum_csp, modulo_count_csp, multiplication_csp, same_remainder_csp, sandwich_bools_csp, sandwich_sum_csp, scalar_product_csp, is_ratio_1_r_csp, shifted_first_x_bools_csp, x_sum_csp, xor_csp
from ortools.sat.python import cp_model
import random


def gen_random_binary_arrays(n: int, min_len: int, max_len: int):
    for _ in range(n):
        size = random.randint(min_len, max_len)
        inputs = [random.randint(0, 1) for _ in range(size)]
        yield inputs


def gen_random_int_arrays(n: int, min_len: int, max_len: int, vrange: tuple[int, int]):
    lb, ub = vrange
    for _ in range(n):
        size = random.randint(min_len, max_len)
        inputs = [random.randint(lb, ub) for _ in range(size)]
        yield inputs


class TestAreAllTrueCSP:

    @staticmethod
    def random_params():
        random.seed(42)
        num_examples = 10
        min_len = 2
        max_len = 10

        test_cases: list[tuple[list[int], int]] = []
        for inputs in gen_random_binary_arrays(num_examples, min_len, max_len):
            output = int(all(bool(v) for v in inputs))
            test_cases.append((inputs, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], int]]:
        return [([], 1),
                ([0], 0), ([1], 1),
                ([0, 0], 0), ([0, 1], 0), ([1, 1], 1),
                ([0, 1, 0], 0), ([1, 1, 1], 1)]

    def run_test(self, inputs: list[int], output: int):
        model = cp_model.CpModel()

        variables = [model.NewBoolVar(f"{i}") for i, _ in enumerate(inputs)]
        for var, val in zip(variables, inputs):
            model.Add(var == int(val))

        all_true_bool = are_all_true_csp(model, variables, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.value(all_true_bool) == int(output)

    @pytest.mark.parametrize("inputs, output", params())
    def test_manual(self, inputs: list[int], output: int):
        self.run_test(inputs, output)

    @pytest.mark.parametrize("inputs, output", random_params())
    def test_random(self, inputs: list[int], output: int):
        self.run_test(inputs, output)


class TestAreAnyTrueCSP:

    @staticmethod
    def random_params():
        random.seed(42)
        num = 10
        min_len = 2
        max_len = 10

        test_cases: list[tuple[list[int], int]] = []
        for inputs in gen_random_binary_arrays(num, min_len, max_len):
            output = int(any(bool(v) for v in inputs))
            test_cases.append((inputs, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], int]]:
        return [([], 0),
                ([0], 0), ([1], 1),
                ([0, 0], 0), ([0, 1], 1), ([1, 1], 1),
                ([0, 1, 0], 1), ([1, 1, 1], 1)]

    def run_test(self, inputs: list[int], output: int):
        model = cp_model.CpModel()

        variables = [model.NewBoolVar(f"{i}") for i, _ in enumerate(inputs)]
        for var, val in zip(variables, inputs):
            model.Add(var == int(val))

        any_true_bool = are_any_true_csp(model, variables, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.value(any_true_bool) == int(output)

    @pytest.mark.parametrize("inputs, output", params())
    def test_manual(self, inputs: list[int], output: int):
        self.run_test(inputs, output)

    @pytest.mark.parametrize("inputs, output", random_params())
    def test_random(self, inputs: list[int], output: int):
        self.run_test(inputs, output)


class TestCountVars:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 10
        min_len = 10
        max_len = 20
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], int, int]] = []
        for inputs in gen_random_int_arrays(num_examples, min_len, max_len, value_range):
            val = random.randint(*value_range)
            output = sum(1 for x in inputs if x == val)
            test_cases.append((inputs, val, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], int, int]]:
        return [
            ([], 3, 0), ([], 0, 0),
            ([0], 0, 1), ([1], 1, 1), ([2], 3, 0),
            ([0, 0], 0, 2), ([0, 1], 0, 1), ([1, 1], 1, 2),
            ([0, 1, 0], 0, 2), ([1, 2, 3, 4, 1], 1, 2), ([1, 2, 3, 4, 1], 2, 1),
            ([10, -10, 10], 10, 2), ([5, 5, 5, 5, 5], 5, 5),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 5, 3)
        ]

    def run_test(self, inputs: list[int], val: int, output: int):
        model = cp_model.CpModel()

        variables = [
            model.NewIntVar(-100, 100, f"var_{i}") for i, _ in enumerate(inputs)]
        for var, val_input in zip(variables, inputs):
            model.Add(var == val_input)

        count_bool = count_vars(model, variables, val, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.value(count_bool) == int(output)

    @pytest.mark.parametrize("inputs, val, output", params())
    def test_manual(self, inputs: list[int], val: int, output: int):
        self.run_test(inputs, val, output)

    @pytest.mark.parametrize("inputs, val, output", generate_random_params())
    def test_random(self, inputs: list[int], val: int, output: int):
        self.run_test(inputs, val, output)


class TestCountDifferentVars:

    @staticmethod
    def generate_random_params():
        num_examples = 10
        min_len = 10
        max_len = 50
        value_range = (-5, 5)

        test_cases: list[tuple[list[int], int, int]] = []
        for _ in range(num_examples):
            size = random.randint(min_len, max_len)
            val = random.randint(*value_range)
            inputs = [random.randint(*value_range) for _ in range(size)]
            output = sum(1 for x in inputs if x != val)
            test_cases.append((inputs, val, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], int, int]]:
        return [
            ([], 3, 0), ([], 0, 0),
            ([0], 0, 0), ([1], 1, 0), ([2], 1, 1),
            ([0, 0], 0, 0), ([0, 1], 0, 1), ([1, 1], 1, 0),
            ([0, 1, 0], 0, 1), ([1, 2, 3, 4, 1], 1, 3), ([1, 2, 3, 4, 1], 2, 4),
            ([10, -10, 10], 10, 1), ([5, 5, 5, 5, 5], 5, 0),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 5, 8)
        ]

    def run_test(self, inputs: list[int], val: int, output: int):
        model = cp_model.CpModel()

        variables = [
            model.NewIntVar(-100, 100, f"var_{i}") for i, _ in enumerate(inputs)]
        for var, val_input in zip(variables, inputs):
            model.Add(var == val_input)

        count_bool = count_different_vars(model, variables, val, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(count_bool) == int(output)

    @pytest.mark.parametrize("inputs, val, output", params())
    def test_manual(self, inputs: list[int], val: int, output: int):
        self.run_test(inputs, val, output)

    @pytest.mark.parametrize("inputs, val, output", generate_random_params())
    def test_random(self, inputs: list[int], val: int, output: int):
        self.run_test(inputs, val, output)


class TestMaskedCountVars:
    @staticmethod
    def generate_random_params():
        random.seed(42)  # Fixed seed for reproducibility
        num_examples = 10
        min_len = 10
        max_len = 100
        value_range = (-5, 5)

        test_cases: list[tuple[list[int], list[int], int, int]] = []
        for _ in range(num_examples):
            size = random.randint(min_len, max_len)
            val = random.randint(*value_range)
            inputs = [random.randint(*value_range) for _ in range(size)]
            masks = [random.randint(0, 1) for _ in range(size)]
            output = sum(1 for x, m in zip(inputs, masks)
                         if x == val and m == 1)
            test_cases.append((inputs, masks, val, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], list[int], int, int]]:
        return [
            ([], [], 0, 0), ([], [], 7, 0),
            ([0], [1], 0, 1), ([1], [1], 1, 1), ([2], [0], 2, 0),
            ([0, 0], [1, 0], 0, 1), ([0, 1], [0, 1], 0, 0), ([1, 1], [1, 1], 1, 2),
            ([0, 1, 0], [1, 1, 0], 0, 1), ([1, 2, 3, 4, 1], [1, 0, 1, 0, 1], 1, 2),
            ([1, 2, 3, 4, 1], [1, 1, 1, 1, 1], 2, 1),
            ([10, -10, 10], [1, 1, 0], 10, 1),
            ([5, 5, 5, 5, 5], [1, 0, 1, 0, 1], 5, 3),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], [
             1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], 5, 3),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], [
             1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1], 5, 2)
        ]

    def run_test(self, inputs: list[int], masks: list[int], val: int, output: int):
        model = cp_model.CpModel()

        variables = [
            model.NewIntVar(-100, 100, f"var_{i}") for i, _ in enumerate(inputs)]
        mask_bools = [model.NewBoolVar(f"mask_{i}")
                      for i, _ in enumerate(masks)]
        for var, val_input in zip(variables, inputs):
            model.Add(var == val_input)
        for mask_var, mask_val in zip(mask_bools, masks):
            model.Add(mask_var == mask_val)

        count_bool = masked_count_vars(model, variables, mask_bools, val, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(count_bool) == int(output)

    @pytest.mark.parametrize("inputs, masks, val, output", params())
    def test_manual(self, inputs: list[int], masks: list[int], val: int, output: int):
        self.run_test(inputs, masks, val, output)

    @pytest.mark.parametrize("inputs, masks, val, output", generate_random_params())
    def test_random(self, inputs: list[int], masks: list[int], val: int, output: int):
        self.run_test(inputs, masks, val, output)


class TestMaskedSumCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)  # Fixed seed for reproducibility
        num_examples = 10
        min_len = 10
        max_len = 50
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], list[int], int]] = []
        for _ in range(num_examples):
            size = random.randint(min_len, max_len)
            inputs = [random.randint(*value_range) for _ in range(size)]
            masks = [random.randint(0, 1) for _ in range(size)]
            output = sum(x * m for x, m in zip(inputs, masks))
            test_cases.append((inputs, masks, output))

        return test_cases

    @staticmethod
    def params():
        return [
            ([0], [1], 0), ([1], [1], 1), ([2], [0], 0),
            ([0, 0], [1, 0], 0), ([0, 1], [0, 1], 1), ([1, 1], [1, 1], 2),
            ([0, 1, 0], [1, 1, 0], 1), ([1, 2, 3, 4, 1], [
                1, 0, 1, 0, 1], 5), ([1, 2, 3, 4, 1], [1, 1, 1, 1, 1], 11),
            ([10, -10, 10], [1, 1, 0], 0), ([5, 5, 5, 5, 5], [1, 0, 1, 0, 1], 15),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], [
             1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], 24)
        ]

    def run_test(self, inputs: list[int], masks: list[int], output: int):
        model = cp_model.CpModel()

        variables = [
            model.NewIntVar(-100, 100, f"var_{i}") for i, _ in enumerate(inputs)]
        mask_bools = [model.NewBoolVar(f"mask_{i}")
                      for i, _ in enumerate(masks)]
        for var, val_input in zip(variables, inputs):
            model.Add(var == val_input)
        for mask_var, mask_val in zip(mask_bools, masks):
            model.Add(mask_var == mask_val)

        sum_var = masked_sum_csp(model, variables, mask_bools, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(sum_var) == int(output)

    @pytest.mark.parametrize("inputs, masks, output", [([], [], 0)])
    def test_empty(self, inputs: list[int], masks: list[int], output: int):
        self.run_test(inputs, masks, output)

    @pytest.mark.parametrize("inputs, masks, output", params())
    def test_manual(self, inputs: list[int], masks: list[int], output: int):
        self.run_test(inputs, masks, output)

    @pytest.mark.parametrize("inputs, masks, output", generate_random_params())
    def test_random(self, inputs: list[int], masks: list[int], output: int):
        self.run_test(inputs, masks, output)


class TestScalarProductCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)  # Fixed seed for reproducibility
        num_examples = 10
        min_len = 10
        max_len = 30
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], list[int], int]] = []
        for _ in range(num_examples):
            size = random.randint(min_len, max_len)
            inputs_x = [random.randint(*value_range) for _ in range(size)]
            inputs_y = [random.randint(*value_range) for _ in range(size)]
            output = sum(x * y for x, y in zip(inputs_x, inputs_y))
            test_cases.append((inputs_x, inputs_y, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], list[int], int]]:
        return [
            ([], [], 0),
            ([1], [1], 1), ([2], [3], 6), ([0], [5], 0),
            ([0, 1], [1, 0], 0), ([1, 2], [3, 4], 11), ([2, 2], [2, 2], 8),
            ([1, 2, 3], [4, 5, 6], 32),
            ([1, -1, 2], [-1, 2, -3], -9), ([3, 0, -3], [2, 4, -2], 12),
            ([1, 1, 1, 1], [1, 1, 1, 1], 4), ([2, 3, 4], [0, 0, 0], 0),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], [
             1, 0, -1, 0, 2, 0, -1, 0, 1, 0, -1], 7)
        ]

    def run_test(self, inputs_x: list[int], inputs_y: list[int], output: int):
        model = cp_model.CpModel()

        variables_x = [
            model.NewIntVar(-100, 100, f"x_{i}") for i, _ in enumerate(inputs_x)]
        variables_y = [
            model.NewIntVar(-100, 100, f"y_{i}") for i, _ in enumerate(inputs_y)]
        for var_x, val_x in zip(variables_x, inputs_x):
            model.Add(var_x == val_x)
        for var_y, val_y in zip(variables_y, inputs_y):
            model.Add(var_y == val_y)

        sum_var = scalar_product_csp(model, variables_x, variables_y, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(sum_var) == int(output)

    @pytest.mark.parametrize("inputs_x, inputs_y, output", params())
    def test_manual(self, inputs_x: list[int], inputs_y: list[int], output: int):
        self.run_test(inputs_x, inputs_y, output)

    @pytest.mark.parametrize("inputs_x, inputs_y, output", generate_random_params())
    def test_random(self, inputs_x: list[int], inputs_y: list[int], output: int):
        self.run_test(inputs_x, inputs_y, output)


class TestIsMemberOf:

    @staticmethod
    def generate_random_params():
        random.seed(42)  # Fixed seed for reproducibility
        num_examples = 20
        min_len = 10
        max_len = 20
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], int, bool]] = []
        for _ in range(num_examples):
            size = random.randint(min_len, max_len)
            inputs = [random.randint(*value_range) for _ in range(size)]
            val = random.randint(*value_range)
            output = val in inputs
            test_cases.append((inputs, val, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], int, bool]]:
        return [
            ([], 0, False), ([], 1, False),
            ([1, 2, 3], 2, True), ([4, 5, 6], 7, False), ([0, -1, -2], -1, True),
            ([0, 1, 2], 3, False), ([1, 2, 3], 3, True), ([1, 2, 3], 0, False),
            ([10, 20, 30], 20, True), ([1, 1, 1], 1, True),
            ([10, -10, 10], 10, True), ([5, 5, 5, 5, 5], 5, True),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 7, False)
        ]

    def run_test(self, inputs: list[int], val: int, output: bool):
        model = cp_model.CpModel()

        variables = [
            model.NewIntVar(-100, 100, f"{i}") for i, _ in enumerate(inputs)]
        for var, val_input in zip(variables, inputs):
            model.Add(var == val_input)

        is_member = is_member_of(model, variables, val, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(is_member) == int(output)

    @pytest.mark.parametrize("inputs, val, output", params())
    def test_manual(self, inputs: list[int], val: int, output: bool):
        self.run_test(inputs, val, output)

    @pytest.mark.parametrize("inputs, val, output", generate_random_params())
    def test_random(self, inputs: list[int], val: int, output: bool):
        self.run_test(inputs, val, output)


class TestIsNotMemberOf:

    @staticmethod
    def generate_random_params():
        random.seed(42)  # Fixed seed for reproducibility
        num_examples = 20
        min_len = 10
        max_len = 20
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], int, bool]] = []
        for _ in range(num_examples):
            size = random.randint(min_len, max_len)
            inputs = [random.randint(*value_range) for _ in range(size)]
            val = random.randint(*value_range)
            output = val not in inputs
            test_cases.append((inputs, val, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], int, bool]]:
        return [
            ([], 0, True), ([], 1, True),
            ([1, 2, 3], 2, False), ([4, 5, 6], 7, True), ([0, -1, -2], -1, False),
            ([0, 1, 2], 3, True), ([1, 2, 3], 3, False), ([1, 2, 3], 0, True),
            ([10, 20, 30], 20, False), ([1, 1, 1], 1, False),
            ([10, -10, 10], 10, False), ([5, 5, 5, 5, 5], 5, False),
            ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 7, True)
        ]

    def run_test(self, inputs: list[int], val: int, output: bool):
        model = cp_model.CpModel()

        variables = [
            model.NewIntVar(-100, 100, f"{i}") for i, _ in enumerate(inputs)]
        for var, val_input in zip(variables, inputs):
            model.Add(var == val_input)

        is_not_member = is_not_member_of(model, variables, val, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(is_not_member) == int(output)

    @pytest.mark.parametrize("inputs, val, output", params())
    def test_manual(self, inputs: list[int], val: int, output: bool):
        self.run_test(inputs, val, output)

    @pytest.mark.parametrize("inputs, val, output", generate_random_params())
    def test_random(self, inputs: list[int], val: int, output: bool):
        self.run_test(inputs, val, output)


class TestAreAllEqual:

    @staticmethod
    def params() -> list[tuple[list[int], int]]:
        return [
            ([], 1),                # No variables, should return true
            ([1], 1),               # Single variable, should return true
            ([1, 1], 1),            # All equal, should return true
            ([1, 0], 0),            # Not all equal, should return false
            ([2, 2, 2], 1),         # All equal, should return true
            ([2, 3, 2], 0),         # Not all equal, should return false
            ([4, 4, 4, 4], 1),      # All equal, should return true
            ([4, 4, 4, 5], 0)       # Not all equal, should return false
        ]

    def run_test(self, inputs: list[int], output: int):
        model = cp_model.CpModel()

        variables = [
            model.NewIntVar(-100, 100, f"{i}") for i, _ in enumerate(inputs)]
        for var, val_input in zip(variables, inputs):
            model.Add(var == val_input)

        all_equal = are_all_equal_csp(model, variables, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(all_equal) == int(output)

    @pytest.mark.parametrize("inputs, output", params())
    def test_manual(self, inputs: list[int], output: bool):
        self.run_test(inputs,  output)


class TestAreAllDiferentCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        min_len = 5
        max_len = 10
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], bool]] = []
        for _ in range(num_examples):
            length = random.randint(min_len, max_len)
            variables = [random.randint(*value_range) for _ in range(length)]
            output = len(set(variables)) == len(variables)
            test_cases.append((variables, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], bool]]:
        return [
            ([1, 2, 3], True), ([3, 3, 3], False), ([1, 1, 2], False),
            ([1, 2, 3, 4, 5], True), ([1, 2, 2, 3], False), ([10, 20, 30], True),
            ([5, 5, 5], False), ([7, 8, 9], True), ([0, 1, 2], True),
            ([], True), ([1], True), ([-1, -2, -3], True), ([-1, -1, -2], False),
            ([1, 2, 3, 2], False), ([3, 4, 5, 6], True)
        ]

    def run_test(self, variables: list[int], output: bool):
        model = cp_model.CpModel()

        var_list = [
            model.NewIntVar(-100, 100, f"var_{i}") for i in range(len(variables))]
        for var, val in zip(var_list, variables):
            model.Add(var == val)

        are_all_different = are_all_diferent_csp(model, var_list, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(are_all_different) == output

    @pytest.mark.parametrize("variables, output", params())
    def test_manual(self, variables: list[int], output: bool):
        self.run_test(variables, output)

    @pytest.mark.parametrize("variables, output", generate_random_params())
    def test_random(self, variables: list[int], output: bool):
        self.run_test(variables, output)


class TestMultiplicationCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 10
        min_len = 2
        max_len = 5
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], int]] = []
        for inputs in gen_random_int_arrays(num_examples, min_len, max_len, value_range):
            output = 1
            for x in inputs:
                output *= x
            test_cases.append((inputs, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], int]]:
        return [
            ([], 1),
            ([2, 3], 6), ([1, 1, 1], 1), ([1, -1], -1), ([0, 5], 0),
            ([5, 5, 5], 125), ([2, 2, 2, 2], 16), ([1, 2, 3, 4], 24),
            ([10, 0, 10], 0), ([-2, 3, -4], 24), ([10, 10], 100),
            ([3, 3, 3], 27), ([2, 3, -1], -6), ([2, -2, 2, -2], 16)
        ]

    def run_test(self, inputs: list[int], output: int):
        model = cp_model.CpModel()

        variables = [
            model.NewIntVar(-100, 100, f"var_{i}") for i, _ in enumerate(inputs)]
        for var, val_input in zip(variables, inputs):
            model.Add(var == val_input)

        product_var = multiplication_csp(model, variables, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(product_var) == int(output)

    @pytest.mark.parametrize("inputs, output", params())
    def test_manual(self, inputs: list[int], output: int):
        self.run_test(inputs, output)

    @pytest.mark.parametrize("inputs, output", generate_random_params())
    def test_random(self, inputs: list[int], output: int):
        self.run_test(inputs, output)


class TestDistanceCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 10
        value_range = (-100, 100)

        test_cases: list[tuple[int, int, int]] = []
        for _ in range(num_examples):
            var1 = random.randint(*value_range)
            var2 = random.randint(*value_range)
            output = abs(var2 - var1)
            test_cases.append((var1, var2, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[int, int, int]]:
        return [
            (0, 0, 0), (1, 1, 0), (0, 1, 1), (1, 0, 1),
            (5, 5, 0), (2, 8, 6), (10, 2, 8), (-5, 5, 10),
            (-3, -7, 4), (100, 50, 50), (-10, -10, 0), (7, -7, 14),
            (-20, 20, 40), (25, -25, 50)
        ]

    def run_test(self, var1: int, var2: int, output: int):
        model = cp_model.CpModel()

        var1_var = model.NewIntVar(-100, 100, "var1")
        var2_var = model.NewIntVar(-100, 100, "var2")
        model.Add(var1_var == var1)
        model.Add(var2_var == var2)

        dist_var = distance_csp(model, var1_var, var2_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(dist_var) == int(output)

    @pytest.mark.parametrize("var1, var2, output", params())
    def test_manual(self, var1: int, var2: int, output: int):
        self.run_test(var1, var2, output)

    @pytest.mark.parametrize("var1, var2, output", generate_random_params())
    def test_random(self, var1: int, var2: int, output: int):
        self.run_test(var1, var2, output)


class TestIsInsideInterval2CSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 10
        start_range = (-100, 0)
        end_range = (1, 100)
        value_range = (-200, 200)

        test_cases: list[tuple[int, int, int, bool]] = []
        for _ in range(num_examples):
            start = random.randint(*start_range)
            end = random.randint(*end_range)
            while end <= start:
                end = random.randint(*end_range)
            val = random.randint(*value_range)
            output = start <= val < end
            test_cases.append((start, end, val, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[int, int, int, bool]]:
        return [
            (0, 10, 5, True), (0, 10, 0, True),
            (0, 10, 10, False), (0, 10, -1, False), (0, 10, 11, False),
            (5, 15, 10, True), (-10, 10, 0, True),
            (-10, 10, -10, True), (-10, 10, 10, False), (-10, 10, -11, False),
            (-10, 10, 11, False), (-20, -10, -15, True),
            (100, 200, 150, True), (100, 200, 100, True), (100, 200, 200, False),
            (100, 200, 99, False), (100, 200, 201, False)
        ]

    def run_test(self, start: int, end: int, val: int, output: bool):
        model = cp_model.CpModel()

        start_var = model.NewIntVar(-1000, 1000, "start")
        end_var = model.NewIntVar(-1000, 1000, "end")
        size_var = model.NewIntVar(0, 2000, "size")
        model.Add(start_var == start)
        model.Add(end_var == end)

        interval_var = model.NewIntervalVar(
            start_var, size_var, end_var, "interval")

        val_var = model.NewIntVar(-1000, 1000, "val")
        model.Add(val_var == val)

        is_inside_bool = is_inside_interval_2_csp(
            model, interval_var, val_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(is_inside_bool) == output

    @pytest.mark.parametrize("start, end, val, output", params())
    def test_manual(self, start: int, end: int, val: int, output: bool):
        self.run_test(start, end, val, output)

    @pytest.mark.parametrize("start, end, val, output", generate_random_params())
    def test_random(self, start: int, end: int, val: int, output: bool):
        self.run_test(start, end, val, output)


class TestCountInSet:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        min_len = 2
        max_len = 5
        value_range = (-10, 10)
        set_size_range = (1, 5)

        test_cases: list[tuple[list[int], list[int], int]] = []
        for _ in range(num_examples):
            x = [random.randint(*value_range)
                 for _ in range(random.randint(min_len, max_len))]
            var_set = [random.randint(*value_range)
                       for _ in range(random.randint(*set_size_range))]
            output = sum(1 for var in x if var in var_set)
            test_cases.append((x, var_set, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], list[int], int]]:
        return [
            ([], [], 0), ([2, 3], [], 0), ([], [1, 4], 0),
            ([1, 2, 3], [1, 3, 5], 2), ([0, 0, 0], [0], 3), ([1, 2, 3], [], 0),
            ([], [1, 2, 3], 0), ([1, 2, 2, 3], [2], 2), ([5, 5, 5], [5], 3),
            ([1, 2, 3, 4, 5], [2, 4], 2), ([-1, -2, -3], [-1, -3, 1], 2),
            ([10, 20, 30], [10, 20, 30], 3), ([0, 1, 2], [2, 3, 4], 1)
        ]

    def run_test(self, x: list[int], var_set: list[int], output: int):
        model = cp_model.CpModel()

        x_vars = [model.NewIntVar(-100, 100, f"x_{i}") for i in range(len(x))]
        for var, val in zip(x_vars, x):
            model.Add(var == val)

        set_vars = [
            model.NewIntVar(-100, 100, f"set_{i}") for i in range(len(var_set))]
        for var, val in zip(set_vars, var_set):
            model.Add(var == val)

        count_var = count_in_set(model, x_vars, set_vars, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(count_var) == output

    @pytest.mark.parametrize("x, var_set, output", params())
    def test_manual(self, x: list[int], var_set: list[int], output: int):
        self.run_test(x, var_set, output)

    @pytest.mark.parametrize("x, var_set, output", generate_random_params())
    def test_random(self, x: list[int], var_set: list[int], output: int):
        self.run_test(x, var_set, output)


class TestIsIncreasingStrictCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        min_len = 2
        max_len = 10
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], bool]] = []
        for _ in range(num_examples):
            length = random.randint(min_len, max_len)
            x = [random.randint(*value_range) for _ in range(length)]
            output = all(x[i] < x[i+1] for i in range(len(x) - 1))
            test_cases.append((x, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], bool]]:
        return [
            ([], False), ([1], True),
            ([1, 2, 3], True), ([3, 2, 1], False),
            ([1, 1, 2], False), ([1, 2, 2], False),
            ([0, 1, 2, 3, 4], True), ([10, 20, 30, 40], True),
            ([5, 3, 2, 1], False), ([-3, -2, -1, 0], True), ([1, 2, 1], False),
            ([-5, -3, -1, 0], True), ([1, 3, 5, 7], True), ([1, 2, 3, 2], False),
            ([2, 3, 5, 7, 11], True)
        ]

    def run_test(self, x: list[int], output: bool):
        model = cp_model.CpModel()

        x_vars = [model.NewIntVar(-100, 100, f"x_{i}") for i in range(len(x))]
        for var, val in zip(x_vars, x):
            model.Add(var == val)

        is_increasing_strict = is_increasing_strict_csp(model, x_vars, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(is_increasing_strict) == output

    @pytest.mark.parametrize("x, output", params())
    def test_manual(self, x: list[int], output: bool):
        self.run_test(x, output)

    @pytest.mark.parametrize("x, output", generate_random_params())
    def test_random(self, x: list[int], output: bool):
        self.run_test(x, output)


class TestIsRenbanCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        min_len = 2
        max_len = 5
        value_range = (-10, 10)

        test_cases: list[tuple[list[int], bool]] = []
        for _ in range(num_examples):
            length = random.randint(min_len, max_len)
            start = random.randint(*value_range)
            renban_set = [start + i for i in range(length)]
            random.shuffle(renban_set)
            output = all(
                renban_set[i] != renban_set[j]
                for i in range(len(renban_set))
                for j in range(i+1, len(renban_set))
            ) and max(renban_set) == min(renban_set) + length - 1
            test_cases.append((renban_set, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], bool]]:
        return [
            ([2, 3, 4], True), ([7, 5, 6, 4], True), ([10, 9, 8], True),
            ([2, 3, 2], False), ([2, 5, 4], False), ([1, 2, 3, 4, 5], True),
            ([5, 3, 4], True), ([1, 3, 2, 4], True), ([10, 8, 9], True),
            ([0, 1, 2], True), ([3, 1, 2], True), ([3, 4, 6], False),
            ([1, 1, 2], False), ([4, 2, 3, 5], True), ([7, 8, 9, 6], True)
        ]

    def run_test(self, variables: list[int], output: bool):
        model = cp_model.CpModel()

        var_list = [
            model.NewIntVar(-100, 100, f"var_{i}") for i in range(len(variables))]
        for var, val in zip(var_list, variables):
            model.Add(var == val)

        is_renban = is_renban_csp(model, var_list, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(is_renban) == output

    @pytest.mark.parametrize("variables, output", params())
    def test_manual(self, variables: list[int], output: bool):
        self.run_test(variables, output)

    @pytest.mark.parametrize("variables, output", generate_random_params())
    def test_random(self, variables: list[int], output: bool):
        self.run_test(variables, output)


class TestIsWhispersCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        min_len = 2
        max_len = 6
        value_range = (-10, 10)
        min_dist_range = (1, 5)

        test_cases: list[tuple[list[int], int, bool]] = []
        for _ in range(num_examples):
            length = random.randint(min_len, max_len)
            min_dist = random.randint(*min_dist_range)
            variables = [random.randint(*value_range) for _ in range(length)]
            output = all(abs(x2-x1) >= min_dist for x1,
                         x2 in zip(variables, variables[1:]))
            test_cases.append((variables, min_dist, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[list[int], int, bool]]:
        return [
            ([2, 7, 1], 5, True), ([7, 1, 6, 1],
                                   5, True), ([10, 2, 8, 0, 5], 5, True),
            ([2, 6, 1], 5, False), ([2, 8, 4, 9],
                                    5, False), ([5, 10, 15], 5, True),
            ([5, 9, 14], 5, False), ([1, 7, 12],
                                     5, True), ([10, 14, 18], 4, True),
            ([], 5, True), ([1], 5, True), ([5, 15, 25], 10, True),
            ([1, 3, 5], 3, False), ([10, 20, 30],
                                    10, True), ([5, 10, 5, 10], 5, True)
        ]

    def run_test(self, variables: list[int], min_dist: int, output: bool):
        model = cp_model.CpModel()

        var_list = [
            model.NewIntVar(-100, 100, f"var_{i}") for i in range(len(variables))]
        for var, val in zip(var_list, variables):
            model.Add(var == val)

        is_whispers = is_whispers_csp(model, var_list, min_dist)
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(is_whispers) == output

    @pytest.mark.parametrize("variables, min_dist, output", params())
    def test_manual(self, variables: list[int], min_dist: int, output: bool):
        self.run_test(variables, min_dist, output)

    @pytest.mark.parametrize("variables, min_dist, output", generate_random_params())
    def test_random(self, variables: list[int], min_dist: int, output: bool):
        self.run_test(variables, min_dist, output)


class TestAreConsecutiveCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 10
        value_range = (-10, 10)

        test_cases: list[tuple[int, int, bool]] = []
        for _ in range(num_examples):
            var1 = random.randint(*value_range)
            var2 = random.randint(*value_range)
            output = abs(var2 - var1) == 1
            test_cases.append((var1, var2, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[int, int, bool]]:
        return [
            (2, 3, True), (7, 6, True), (1, 2, True),
            (3, 5, False), (2, 2, False), (10, 11, True),
            (-1, 0, True), (0, 1, True), (-5, -4, True),
            (5, 5, False), (6, 8, False), (-3, -2, True),
            (-1, 1, False), (3, 4, True), (4, 2, False)
        ]

    def run_test(self, var1: int, var2: int, output: bool):
        model = cp_model.CpModel()

        var1_var = model.NewIntVar(-100, 100, "var1")
        var2_var = model.NewIntVar(-100, 100, "var2")
        model.Add(var1_var == var1)
        model.Add(var2_var == var2)

        are_consecutive = are_consecutive_csp(model, var1_var, var2_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(are_consecutive) == output

    @pytest.mark.parametrize("var1, var2, output", params())
    def test_manual(self, var1: int, var2: int, output: bool):
        self.run_test(var1, var2, output)

    @pytest.mark.parametrize("var1, var2, output", generate_random_params())
    def test_random(self, var1: int, var2: int, output: bool):
        self.run_test(var1, var2, output)


class TestIsRatio1RCSP:

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        value_range = (1, 10)
        ratio_range = (1, 5)

        test_cases: list[tuple[int, int, int, bool]] = []
        for _ in range(num_examples):
            var1 = random.randint(*value_range)
            var2 = random.randint(*value_range)
            r = random.randint(*ratio_range)
            output = (var2 == r * var1) or (var1 == r * var2)
            test_cases.append((var1, var2, r, output))

        return test_cases

    @staticmethod
    def params() -> list[tuple[int, int, int, bool]]:
        return [
            (1, 2, 2, True), (4, 2, 2, True), (8, 4, 2, True), (8, 16, 2, True),
            (2, 6, 3, True), (12, 4, 3, True), (2, 3, 2, False), (5, 3, 2, False),
            (3, 9, 3, True), (6, 2, 3, True), (10, 2, 5, True), (20, 4, 5, True),
            (2, 8, 3, False), (5, 10, 2, True), (5, 10, 3, False)
        ]

    def run_test(self, var1: int, var2: int, r: int, output: bool):
        model = cp_model.CpModel()

        var1_var = model.NewIntVar(-100, 100, "var1")
        var2_var = model.NewIntVar(-100, 100, "var2")
        r_var = model.NewIntVar(-100, 100, "r")
        model.Add(var1_var == var1)
        model.Add(var2_var == var2)
        model.Add(r_var == r)

        is_ratio = is_ratio_1_r_csp(model, var1_var, var2_var, r_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(is_ratio) == output

    @pytest.mark.parametrize("var1, var2, r, output", params())
    def test_manual(self, var1: int, var2: int, r: int, output: bool):
        self.run_test(var1, var2, r, output)

    @pytest.mark.parametrize("var1, var2, r, output", generate_random_params())
    def test_random(self, var1: int, var2: int, r: int, output: bool):
        self.run_test(var1, var2, r, output)


class TestSameRemainderCSP:

    @staticmethod
    def params() -> list[tuple[int, int, int, bool]]:
        return [
            (10, 20, 5, True), (10, 25, 5, True), (14, 4, 5, True), (17, 3, 7, True),
            (12, 3, 2, False), (7, 3, 2, True), (21, 14, 7, True),
            (16, 2, 7, True), (9, 12, 3, True), (8, 5, 3, True),
            (11, 4, 3, False), (13, 7, 4, False)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        value_range = (0, 100)
        mod_range = (1, 10)

        test_cases: list[tuple[int, int, int, bool]] = []
        for _ in range(num_examples):
            var1 = random.randint(*value_range)
            var2 = random.randint(*value_range)
            mod = random.randint(*mod_range)
            output = (var1 % mod == var2 % mod)
            test_cases.append((var1, var2, mod, output))

        return test_cases

    def run_test(self, var1: int, var2: int, mod: int, output: bool):
        model = cp_model.CpModel()
        var1_var = model.NewIntVar(-100, 100, "var1")
        var2_var = model.NewIntVar(-100, 100, "var2")
        model.Add(var1_var == var1)
        model.Add(var2_var == var2)

        same_remainder = same_remainder_csp(model, var1_var, var2_var, mod, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(same_remainder) == output

    @pytest.mark.parametrize("var1, var2, mod, output", params())
    def test_manual(self, var1: int, var2: int, mod: int, output: bool):
        self.run_test(var1, var2, mod, output)

    @pytest.mark.parametrize("var1, var2, mod, output", generate_random_params())
    def test_random(self, var1: int, var2: int, mod: int, output: bool):
        self.run_test(var1, var2, mod, output)


class TestIsEvenCSP:

    @staticmethod
    def params() -> list[tuple[int, bool]]:
        return [
            (2, True), (4, True), (6, True), (8, True),
            (1, False), (3, False), (5, False), (7, False),
            (10, True), (11, False), (0, True), (-2, True),
            (-3, False), (-4, True), (100, True), (101, False)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        value_range = (-100, 100)

        test_cases: list[tuple[int, bool]] = []
        for _ in range(num_examples):
            var1 = random.randint(*value_range)
            output = (var1 % 2 == 0)
            test_cases.append((var1, output))

        return test_cases

    def run_test(self, var1: int, output: bool):
        model = cp_model.CpModel()
        var1_var = model.NewIntVar(-200, 200, "var1")
        model.Add(var1_var == var1)

        is_even = is_even_csp(model, var1_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(is_even) == output

    @pytest.mark.parametrize("var1, output", params())
    def test_manual(self, var1: int, output: bool):
        self.run_test(var1, output)

    @pytest.mark.parametrize("var1, output", generate_random_params())
    def test_random(self, var1: int, output: bool):
        self.run_test(var1, output)


class TestIsOddCSP:

    @staticmethod
    def params() -> list[tuple[int, bool]]:
        return [
            (2, False), (4, False), (6, False), (8, False),
            (1, True), (3, True), (5, True), (7, True),
            (10, False), (11, True), (0, False), (-2, False),
            (-3, True), (-4, False), (100, False), (101, True)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        value_range = (-100, 100)

        test_cases: list[tuple[int, bool]] = []
        for _ in range(num_examples):
            var1 = random.randint(*value_range)
            output = (var1 % 2 == 1)
            test_cases.append((var1, output))

        return test_cases

    def run_test(self, var1: int, output: bool):
        model = cp_model.CpModel()
        var1_var = model.NewIntVar(-200, 200, "var1")
        model.Add(var1_var == var1)

        is_odd = is_odd_csp(model, var1_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.BooleanValue(is_odd) == output

    @pytest.mark.parametrize("var1, output", params())
    def test_manual(self, var1: int, output: bool):
        self.run_test(var1, output)

    @pytest.mark.parametrize("var1, output", generate_random_params())
    def test_random(self, var1: int, output: bool):
        self.run_test(var1, output)


class TestModuloCountCSP:

    @staticmethod
    def params() -> list[tuple[list[int], int, int, int]]:
        return [
            ([], 2, 5, 0),
            ([10, 20, 30, 40], 0, 10, 4), ([10, 21, 32, 43], 1, 10, 1),
            ([14, 24, 34, 44], 4, 10, 4), ([17, 27, 37, 47], 7, 10, 4),
            ([12, 22, 32, 42], 2, 10, 4), ([7, 3, 8, 13], 3, 5, 3),
            ([21, 14, 7, 2], 1, 7, 0), ([16, 3, 10, 5], 3, 7, 2),
            ([9, 12, 15, 18], 3, 3, 0), ([8, 5, 2, 11], 1, 3, 0),
            ([11, 14, 17, 20], 2, 3, 4), ([13, 16, 19, 22], 1, 4, 1),
            # ([-2, -6, -7, 14, 4], 2, 4, 1),
            # ([-2, -6, -7, 14, 4], -2, 4, 2),
            # ([-2, -6, -7, 14, 4], -2, -4, 1),
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        value_range = (0, 100)
        mod_range = (1, 10)

        test_cases: list[tuple[list[int], int, int, int]] = []
        for _ in range(num_examples):
            variables = [random.randint(*value_range) for _ in range(20)]
            mod = random.randint(*mod_range)
            bound = abs(mod)
            target = random.randint(0, bound - 1)
            count = sum(var % mod == target for var in variables)
            test_cases.append((variables, target, mod, count))

        return test_cases

    def run_test(self, variables: list[int], target: int, mod: int, expected_count: int):
        model = cp_model.CpModel()
        variable_vars = [model.NewIntVar(
            -100, 100, f"var_{i}") for i in range(len(variables))]
        for var, val in zip(variable_vars, variables):
            model.Add(var == val)

        count_var = modulo_count_csp(model, target, mod, variable_vars, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(count_var) == expected_count

    @pytest.mark.parametrize("variables, target, mod, expected_count", params())
    def test_manual(self, variables: list[int], target: int, mod: int, expected_count: int):
        self.run_test(variables, target, mod, expected_count)

    @pytest.mark.parametrize("variables, target, mod, expected_count", generate_random_params())
    def test_random(self, variables: list[int], target: int, mod: int, expected_count: int):
        self.run_test(variables, target, mod, expected_count)


class TestGreaterThanAllCSP:

    @staticmethod
    def params() -> list[tuple[list[int], int, bool]]:
        return [
            ([1, 2, 3, 4], 5, True), ([10, 20, 30, 40], 35, False),
            ([3, 5, 7], 7, False), ([7, 7, 7], 8, True),
            ([7, 8, 9], 10, True), ([1, 2, 3], 2, False),
            ([4, 4, 4], 4, False), ([3, 6, 9], 6, False),
            ([0, 0, 0], 1, True), ([10, 11, 12], 15, True),
            ([15, 16, 17], 14, False), ([7, 8, 9, 10], 10, False)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 20
        value_range = (-100, 100)
        min_len = 3
        max_len = 10

        test_cases: list[tuple[list[int], int, bool]] = []
        for variables in gen_random_binary_arrays(num_examples, min_len, max_len):
            target = random.randint(*value_range)
            is_greater = all(target > var for var in variables)
            test_cases.append((variables, target, is_greater))

        return test_cases

    def run_test(self, variables: list[int], target: int, expected_result: bool):
        model = cp_model.CpModel()
        variable_vars = [model.NewIntVar(
            -100, 100, f"var_{i}") for i in range(len(variables))]
        for var, val in zip(variable_vars, variables):
            model.Add(var == val)

        target_var = model.NewIntVar(-100, 100, "target")
        model.Add(target_var == target)

        result_var = greater_than_all_csp(model, variable_vars, target_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(result_var) == expected_result

    @pytest.mark.parametrize("variables, target, expected_result", params())
    def test_manual(self, variables: list[int], target: int, expected_result: bool):
        self.run_test(variables, target, expected_result)

    @pytest.mark.parametrize("variables, target, expected_result", generate_random_params())
    def test_random(self, variables: list[int], target: int, expected_result: bool):
        self.run_test(variables, target, expected_result)


class TestXorCSP:

    def run_test(self, a: int, b: int, expected_result: int):
        model = cp_model.CpModel()
        a_var = model.NewBoolVar("a")
        b_var = model.NewBoolVar("b")
        model.Add(a_var == a)
        model.Add(b_var == b)

        xor_res = xor_csp(model, a_var, b_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(xor_res) == expected_result

    @pytest.mark.parametrize("a, b, expected_result",
                             [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)])
    def test_manual(self, a: int, b: int, expected_result: bool):
        self.run_test(a, b, expected_result)


class TestIsSandwichedCSP:

    @staticmethod
    def params() -> list[tuple[list[int], int, int, int, bool]]:
        return [
            ([2, 9, 4, 6, 3, 1, 1, 5], 3, 1, 4, True),
            ([2, 9, 4, 6, 3, 1, 1, 5], 4, 1, 4, True),
            ([2, 9, 4, 6, 3, 1, 1, 5], 5, 1, 4, True),
            ([2, 9, 4, 6, 3, 1, 1, 5], 2, 1, 4, False),
            ([7, 8, 9, 1, 3], 2, 7, 3, True),
            ([7, 8, 9, 1, 3], 0, 7, 3, False),
            ([1, 2, 3, 4, 5], 2, 1, 5, True),
            ([1, 2, 3, 4, 5], 1, 5, 4, False),
            ([10, 20, 30, 40], 2, 10, 40, True),
            ([10, 20, 30, 40], 3, 10, 20, False)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        value_range = (-100, 100)
        len_range = (5, 10)

        test_cases: list[tuple[list[int], int, int, int, bool]] = []
        for _ in range(num_examples):
            variables = [random.randint(*value_range)
                         for _ in range(random.randint(*len_range))]
            idx = random.randint(0, len(variables) - 1)
            a, b = random.sample(variables, 2)
            expected_result = (a in variables[:idx] and b in variables[idx+1:]) or (
                b in variables[:idx] and a in variables[idx+1:])
            test_cases.append((variables, idx, a, b, expected_result))

        return test_cases

    def run_test(self, variables: list[int], idx: int, a: int, b: int, expected_result: bool):
        model = cp_model.CpModel()
        value_range = (-100, 100)

        variable_vars = [model.NewIntVar(
            *value_range, f"var_{i}") for i in range(len(variables))]
        for var, val in zip(variable_vars, variables):
            model.Add(var == val)

        a_var = model.NewIntVar(*value_range, "a")
        b_var = model.NewIntVar(*value_range, "b")
        model.Add(a_var == a)
        model.Add(b_var == b)

        result_var = is_sandwiched_csp(
            model, variable_vars, idx, a_var, b_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(result_var) == expected_result

    @pytest.mark.parametrize("variables, idx, a, b, expected_result", params())
    def test_manual(self, variables: list[int], idx: int, a: int, b: int, expected_result: bool):
        self.run_test(variables, idx, a, b, expected_result)

    @pytest.mark.parametrize("variables, idx, a, b, expected_result", generate_random_params())
    def test_random(self, variables: list[int], idx: int, a: int, b: int, expected_result: bool):
        self.run_test(variables, idx, a, b, expected_result)


class TestSandwichBoolsCSP:

    @staticmethod
    def params() -> list[tuple[list[int], int, int, list[int]]]:
        return [
            ([2, 9, 4, 6, 3, 1, 1, 5], 1, 9, [0, 0, 1, 1, 1, 1, 0, 0]),
            ([5, 1, 3, 5, 4, 9, 6, 5], 1, 9, [0, 0, 1, 1, 1, 0, 0, 0]),
            ([5, 7, 3, 1, 9, 6, 5, 2], 1, 9, [0, 0, 0, 0, 0, 0, 0, 0]),
            ([4, 0, 1, 7, 3, 5, 6, 8], 1, 9, [0, 0, 0, 0, 0, 0, 0, 0])
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        value_range = (-100, 100)
        len_range = (10, 20)

        test_cases: list[tuple[list[int], int, int, list[int]]] = []
        for _ in range(num_examples):
            variables = [random.randint(*value_range)
                         for _ in range(random.randint(*len_range))]
            a, b = random.sample(variables, 2)
            expected_result = [
                int((a in variables[:i] and b in variables[i+1:]
                     ) or (b in variables[:i] and a in variables[i+1:]))
                for i in range(len(variables))
            ]
            test_cases.append((variables, a, b, expected_result))

        return test_cases

    def run_test(self, variables: list[int], a: int, b: int, expected_result: list[int]):
        model = cp_model.CpModel()
        value_range = (-100, 100)
        variable_vars = [model.NewIntVar(
            *value_range, f"var_{i}") for i in range(len(variables))]
        for var, val in zip(variable_vars, variables):
            model.Add(var == val)

        a_var = model.NewIntVar(*value_range, "a")
        b_var = model.NewIntVar(*value_range, "b")
        model.Add(a_var == a)
        model.Add(b_var == b)

        result_bools = sandwich_bools_csp(
            model, variable_vars, a_var, b_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        for result_bool, expected in zip(result_bools, expected_result):
            assert solver.Value(result_bool) == expected

    @pytest.mark.parametrize("variables, a, b, expected_result", params())
    def test_manual(self, variables: list[int], a: int, b: int, expected_result: list[int]):
        self.run_test(variables, a, b, expected_result)

    @pytest.mark.parametrize("variables, a, b, expected_result", generate_random_params())
    def test_random(self, variables: list[int], a: int, b: int, expected_result: list[int]):
        self.run_test(variables, a, b, expected_result)


class TestFirstXBoolsCSP:

    @staticmethod
    def params() -> list[tuple[int, int, list[int]]]:
        return [
            (10, 4, [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]),
            (5, 2, [1, 1, 0, 0, 0]),
            (8, 8, [1, 1, 1, 1, 1, 1, 1, 1]),
            (6, 0, [0, 0, 0, 0, 0, 0]),
            (7, 10, [1, 1, 1, 1, 1, 1, 1])
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        n_range = (1, 15)
        x_range = (-20, 20)

        test_cases: list[tuple[int, int, list[int]]] = []
        for _ in range(num_examples):
            n = random.randint(*n_range)
            x = random.randint(*x_range)
            expected_result = [int(i < x) for i in range(n)]
            test_cases.append((n, x, expected_result))

        return test_cases

    def run_test(self, n: int, x: int, expected_result: list[int]):
        model = cp_model.CpModel()
        x_var = model.NewIntVar(-20, 20, "x")
        model.Add(x_var == x)

        result_bools = first_x_bools_csp(model, n, x_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        for result_bool, expected in zip(result_bools, expected_result):
            assert solver.Value(result_bool) == expected

    @pytest.mark.parametrize("n, x, expected_result", params())
    def test_manual(self, n: int, x: int, expected_result: list[int]):
        self.run_test(n, x, expected_result)

    @pytest.mark.parametrize("n, x, expected_result", generate_random_params())
    def test_random(self, n: int, x: int, expected_result: list[int]):
        self.run_test(n, x, expected_result)


class TestShiftedFirstXBoolsCSP:

    @staticmethod
    def params() -> list[tuple[int, int, int, list[int]]]:
        return [
            (10, 4, 2, [0, 0, 1, 1, 1, 1, 0, 0, 0, 0]),
            (5, 2, 1, [0, 1, 1, 0, 0]),
            (8, 3, 0, [1, 1, 1, 0, 0, 0, 0, 0]),
            (6, 2, 4, [0, 0, 0, 0, 1, 1]),
            (7, 5, 6, [0, 0, 0, 0, 0, 0, 1])
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        n_range = (1, 20)
        x_range = (-30, 30)
        a_range = (-30, 30)

        test_cases: list[tuple[int, int, int, list[int]]] = []
        for _ in range(num_examples):
            n = random.randint(*n_range)
            x = random.randint(*x_range)
            a = random.randint(*a_range)
            expected_result = [int(a <= i < a + x) for i in range(n)]
            test_cases.append((n, x, a, expected_result))

        return test_cases

    def run_test(self, n: int, x: int, a: int, expected_result: list[int]):
        model = cp_model.CpModel()
        x_var = model.NewIntVar(-30, 30, "x")
        a_var = model.NewIntVar(-30, 30, "a")
        model.Add(x_var == x)
        model.Add(a_var == a)

        result_bools = shifted_first_x_bools_csp(model, n, x_var, a_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        for result_bool, expected in zip(result_bools, expected_result):
            assert solver.Value(result_bool) == expected

    @pytest.mark.parametrize("n, x, a, expected_result", params())
    def test_manual(self, n: int, x: int, a: int, expected_result: list[int]):
        self.run_test(n, x, a, expected_result)

    @pytest.mark.parametrize("n, x, a, expected_result", generate_random_params())
    def test_random(self, n: int, x: int, a: int, expected_result: list[int]):
        self.run_test(n, x, a, expected_result)


class TestXSumCSP:

    @staticmethod
    def params() -> list[tuple[list[int], int, int]]:
        return [
            ([3, 9, 4, 1, 7, 8, 9], 4, 17),
            ([5, 2, 6, 1, 3], 3, 13),
            ([8, 1, 2], 2, 9),
            ([4, 4, 4, 4], 2, 8),
            ([10, 20, 30, 40, 50], 5, 150),
            ([10, 20, 30, 40, 50], 7, 150)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        list_size_range = (1, 20)
        element_range = (-100, 100)
        x_range = (-30, 30)

        test_cases: list[tuple[list[int], int, int]] = []
        for _ in range(num_examples):
            list_size = random.randint(*list_size_range)
            variables = [random.randint(*element_range)
                         for _ in range(list_size)]
            x = random.randint(*x_range)
            expected_sum = sum(var for i, var in enumerate(variables) if i < x)
            test_cases.append((variables, x, expected_sum))

        return test_cases

    def run_test(self, variables: list[int], x: int, expected_sum: int):
        model = cp_model.CpModel()
        x_var = model.NewIntVar(-30, 30, "x")
        model.Add(x_var == x)

        int_vars = [model.NewIntVar(
            -100, 100, f"var_{i}") for i in range(len(variables))]
        for int_var, value in zip(int_vars, variables):
            model.Add(int_var == value)

        sum_var = x_sum_csp(model, int_vars, x_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(sum_var) == expected_sum

    @pytest.mark.parametrize("variables, x, expected_sum", params())
    def test_manual(self, variables: list[int], x: int, expected_sum: int):
        self.run_test(variables, x, expected_sum)

    @pytest.mark.parametrize("variables, x, expected_sum", generate_random_params())
    def test_random(self, variables: list[int], x: int, expected_sum: int):
        self.run_test(variables, x, expected_sum)


class TestSandwichSumCSP:

    @staticmethod
    def params() -> list[tuple[list[int], int, int, int]]:
        return [
            ([2, 9, 4, 6, 3, 1, 1, 5], 1, 9, 14),
            ([5, 1, 3, 5, 4, 9, 6, 5], 1, 9, 12),
            ([5, 7, 3, 1, 9, 6, 5, 2], 1, 9, 0),
            ([4, 0, 1, 7, 3, 5, 6, 8], 1, 9, 0),
            ([1, 2, 3, 1, 9, 1, 3, 2], 1, 9, 6)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        list_size_range = (1, 30)
        element_range = (-10, 10)

        test_cases: list[tuple[list[int], int, int, int]] = []
        for _ in range(num_examples):
            list_size = random.randint(*list_size_range)
            variables = [random.randint(*element_range)
                         for _ in range(list_size)]
            a = random.randint(*element_range)
            b = random.randint(*element_range)
            expected_sum = 0
            for i in range(len(variables)):
                left_side = variables[:i]
                right_side = variables[i+1:]
                if (a in left_side and b in right_side) or (b in left_side and a in right_side):
                    expected_sum += variables[i]
            test_cases.append((variables, a, b, expected_sum))

        return test_cases

    def run_test(self, variables: list[int], a: int, b: int, expected_sum: int):
        model = cp_model.CpModel()
        var_range = (-10, 10)
        a_var = model.NewIntVar(*var_range, "a")
        b_var = model.NewIntVar(*var_range, "b")
        model.Add(a_var == a)
        model.Add(b_var == b)

        int_vars = [model.NewIntVar(
            *var_range, f"var_{i}") for i in range(len(variables))]
        for int_var, value in zip(int_vars, variables):
            model.Add(int_var == value)

        sum_var = sandwich_sum_csp(model, int_vars, a_var, b_var, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(sum_var) == expected_sum

    @pytest.mark.parametrize("variables, a, b, expected_sum", params())
    def test_manual(self, variables: list[int], a: int, b: int, expected_sum: int):
        self.run_test(variables, a, b, expected_sum)

    @pytest.mark.parametrize("variables, a, b, expected_sum", generate_random_params())
    def test_random(self, variables: list[int], a: int, b: int, expected_sum: int):
        self.run_test(variables, a, b, expected_sum)


class TestCountUniqueValues:

    @staticmethod
    def params() -> list[tuple[list[int], int]]:
        return [
            ([], 0),
            ([1, 2, 3, 4, 5], 5),
            ([1, 1, 1, 1, 1], 1),
            ([1, 2, 2, 3, 3], 3),
            ([5, 4, 3, 2, 1], 5),
            ([5, 5, 4, 4, 3, 3, 2, 2, 1, 1], 5)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        list_size_range = (1, 30)
        element_range = (-10, 10)

        test_cases: list[tuple[list[int], int]] = []
        for _ in range(num_examples):
            list_size = random.randint(*list_size_range)
            variables = [random.randint(*element_range)
                         for _ in range(list_size)]
            expected_count = len(set(variables))
            test_cases.append((variables, expected_count))

        return test_cases

    def run_test(self, variables: list[int], expected_count: int):
        model = cp_model.CpModel()
        int_vars = [
            model.NewIntVar(-10, 10, f"var_{i}") for i in range(len(variables))]
        for int_var, value in zip(int_vars, variables):
            model.Add(int_var == value)

        count_var = count_unique_values(model, int_vars, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(count_var) == expected_count

    @pytest.mark.parametrize("variables, expected_count", params())
    def test_manual(self, variables: list[int], expected_count: int):
        self.run_test(variables, expected_count)

    @pytest.mark.parametrize("variables, expected_count", generate_random_params())
    def test_random(self, variables: list[int], expected_count: int):
        self.run_test(variables, expected_count)


class TestCountTransitionsCSP:

    @staticmethod
    def params() -> list[tuple[list[int], int]]:
        return [
            ([], 0), ([3], 0),
            ([1, 2, 3, 4, 5], 4),
            ([1, 1, 1, 1, 1], 0),
            ([1, 2, 2, 3, 3], 2),
            ([5, 4, 3, 2, 1], 4),
            ([5, 5, 4, 4, 3, 3, 2, 2, 1, 1], 4)
        ]

    @staticmethod
    def generate_random_params():
        random.seed(42)
        num_examples = 30
        list_size_range = (1, 30)
        element_range = (0, 10)

        test_cases: list[tuple[list[int], int]] = []
        for _ in range(num_examples):
            list_size = random.randint(*list_size_range)
            variables = [random.randint(*element_range)
                         for _ in range(list_size)]
            expected_count = sum(1 for x1, x2 in zip(
                variables, variables[1:]) if x1 != x2)
            test_cases.append((variables, expected_count))

        return test_cases

    def run_test(self, variables: list[int], expected_count: int):
        model = cp_model.CpModel()
        int_vars = [model.NewIntVar(
            0, 10, f"var_{i}") for i in range(len(variables))]
        for int_var, value in zip(int_vars, variables):
            model.Add(int_var == value)

        count_var = count_transitions_csp(model, int_vars, "")
        solver = cp_model.CpSolver()
        solver.solve(model)

        assert solver.Value(count_var) == expected_count

    @pytest.mark.parametrize("variables, expected_count", params())
    def test_manual(self, variables: list[int], expected_count: int):
        self.run_test(variables, expected_count)

    @pytest.mark.parametrize("variables, expected_count", generate_random_params())
    def test_random(self, variables: list[int], expected_count: int):
        self.run_test(variables, expected_count)
