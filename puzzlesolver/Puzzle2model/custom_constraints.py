from itertools import combinations, product
from typing import Iterable

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar, BoundedLinearExpression, IntervalVar, BoundedLinearExprT, LinearExprT

from puzzlesolver.Puzzle2model.puzzle_model_types import AdjacencyDict
from puzzlesolver.utils.ListUtils import get_left_side, get_right_side


VarList = list[int] | list[IntVar] | list[int | IntVar]


def get_domain(x: int | IntVar) -> tuple[int, int]:
    if isinstance(x, IntVar):
        lb = min(x.Proto().domain)
        ub = max(x.Proto().domain)
    else:
        lb, ub = (x, x)
    return lb, ub


def varlist_domain(x: VarList):
    domains: list[tuple[int, int]] = []
    for v in x:
        domain = get_domain(v)
        domains.append(domain)
    return domains


def compute_sum_domain(domains_list: list[tuple[int, int]]) -> tuple[int, int]:
    if not domains_list:
        return (0, 0)

    min_sum, max_sum = 0, 0

    for interval in domains_list:
        current_min, current_max = interval
        min_sum += current_min
        max_sum += current_max

    return (min_sum, max_sum)


def compute_multiplication_domain(domains_list: list[tuple[int, int]]) -> tuple[int, int]:
    if not domains_list:
        return (1, 1)

    # Initialize the product domain
    min_product, max_product = 1, 1

    for interval in domains_list:
        current_min, current_max = interval
        # Calculate all possible products
        temp_min = min(min_product * current_min, min_product * current_max,
                       max_product * current_min, max_product * current_max)
        temp_max = max(min_product * current_min, min_product * current_max,
                       max_product * current_min, max_product * current_max)
        # Update the products
        min_product, max_product = temp_min, temp_max

    return (min_product, max_product)


def reif(model: cp_model.CpModel, expr: BoundedLinearExpression, prefix: str) -> IntVar:
    """
    Return the boolean variable b to express:
        b => expr
    """
    b = model.NewBoolVar(f"{prefix} - reif - bool " + str(expr))
    model.Add(expr).OnlyEnforceIf(b)
    return b


def reif_2(model: cp_model.CpModel, expr: BoundedLinearExpression, b: IntVar) -> IntVar:
    """
    Return the boolean variable b to express
        b <=> expr
    """
    model.Add(expr).OnlyEnforceIf(b)
    return b


def reif2(model: cp_model.CpModel, expr: BoundedLinearExprT, not_expr: BoundedLinearExprT,
          prefix: str) -> IntVar:
    """
    Return the boolean variable b to express:
        b <=> expr
        !b <=> not_expr
    """
    name = f"{prefix} - reif2"
    b = model.NewBoolVar(f"{name} - bool")
    model.Add(expr).OnlyEnforceIf(b)
    model.Add(not_expr).OnlyEnforceIf(b.Not())
    return b


def reif2_2(model: cp_model.CpModel, expr: BoundedLinearExprT, not_expr: BoundedLinearExprT,
            b: IntVar) -> IntVar:
    """
    Return the boolean variable b to express
        b <=> expr
        !b <=> not_expr
    """
    model.Add(expr).OnlyEnforceIf(b)
    model.Add(not_expr).OnlyEnforceIf(b.Not())
    return b


def are_all_true_csp(model: cp_model.CpModel, variables: list[IntVar], prefix: str) -> IntVar:
    """
    Returns a bool variable indicating if all variables are true:
        all_true_bool = all(var == 1 for var in variables)
    """
    prefix = f"{prefix} - all_true_csp"
    all_true_bool = model.NewBoolVar(f"{prefix} - all_true_bool")

    model.AddBoolAnd(variables).OnlyEnforceIf(all_true_bool)
    model.AddBoolOr([var.Not() for var in variables]
                    ).OnlyEnforceIf(all_true_bool.Not())

    return all_true_bool


def are_any_true_csp(model: cp_model.CpModel, variables: list[IntVar], prefix: str) -> IntVar:
    """
    Returns a bool variable indicating if at least one of the variables are true:
        any_true_bool = any(var == 1 for var in variables)
    """
    prefix = f"{prefix} - all_true_csp"
    any_true_bool = model.NewBoolVar(f"{prefix} - any_true_bool")

    model.AddBoolOr(variables).OnlyEnforceIf(any_true_bool)
    model.AddBoolAnd([var.Not() for var in variables]
                     ).OnlyEnforceIf(any_true_bool.Not())

    return any_true_bool


def count_vars(model: cp_model.CpModel, variables: VarList, val: LinearExprT, prefix: str) -> IntVar:
    """
    Counts the number of occurrences of `val` in array `variables`:
        count = sum([var == val for var in variables])
    """
    n = len(variables)
    prefix = f"{prefix} - count_vars"
    count = model.NewIntVar(0, n, f"{prefix} - count")
    if n == 0:
        model.Add(count == 0)
        return count

    b = [model.NewBoolVar(f"{prefix} - b_{i}")
         for i, _ in enumerate(variables)]
    for i in range(n):
        model.Add(variables[i] == val).OnlyEnforceIf(b[i])
        model.Add(variables[i] != val).OnlyEnforceIf(b[i].Not())
    model.Add(count == sum(b))
    return count


def count_different_vars(model: cp_model.CpModel, variables: VarList,
                         val: LinearExprT, prefix: str) -> IntVar:
    """
    Counts the number of occurrences in `variables` that are different from 'val':
        count = sum([var != val for var in variables)
    """
    n = len(variables)
    prefix = f"{prefix} - count_different_vars"
    count_different = model.NewIntVar(0, n, f"{prefix} - count")
    if n == 0:
        model.Add(count_different == 0)
        return count_different

    count_equal = count_vars(model, variables, val, f"{prefix} - count_equal")
    model.Add(count_different == n - count_equal)
    return count_different


def exactly(model: cp_model.CpModel, val: int | IntVar, x: list[IntVar], n: int | IntVar, prefix: str):
    """
    Exactly n occurrences of value val in array x:
        n == sum(val == var for var in x)
    """
    prefix = f"{prefix} - exactly"
    count = count_vars(model, x, val, prefix)
    model.Add(count == n)


def masked_count_vars(model: cp_model.CpModel, variables: VarList,
                      mask_bools: list[IntVar], val: int | IntVar, prefix: str) -> IntVar:
    """
    Counts the number of occurrences of 'val' in array 'variables', masked by mask_bools (a variable only counts toward the final count if the corresponding mask_var is true):
        count = sum(var == val and mask for var, mask in zip(variables, mask_bools))
    """
    n = len(variables)
    prefix = f"{prefix} - masked_count_vars"

    assert n == len(mask_bools)

    count = model.NewIntVar(0, n, f"{prefix} - count")
    if n == 0:
        model.Add(count == 0)
        return count

    equal_and_count_bools: list[IntVar] = []
    for i, (var, mask) in enumerate(zip(variables, mask_bools)):
        is_equal = are_all_equal_csp(
            model, [var, val], f"{prefix} - is_equal {i}")
        equal_and_count_bool = are_all_true_csp(
            model, [is_equal, mask], f"{prefix}_{i} - equal_and_count_bool")

        equal_and_count_bools.append(equal_and_count_bool)

    model.Add(count == sum(equal_and_count_bools))
    return count


def masked_all_different(model: cp_model.CpModel, variables: list[IntVar], mask_bools: list[IntVar], prefix: str):
    """
    Forces all the masked variables in variables to be different. The mask is given by mask_bools:
        var[i] != var[j] <=> i == j == True, for all i != j, i < j, 1 < j < len(variables)
    """
    prefix = f"{prefix} - conditional_all_different"
    n1 = len(variables)
    n2 = len(mask_bools)

    assert n1 == n2, "variables and bools must be the same length."

    for i, ((var1, bool_var1), (var2, bool_var2)) in enumerate(combinations(zip(variables, mask_bools), 2)):
        bool_aux = model.NewBoolVar(f"{prefix} - bool_{i}")
        model.AddBoolAnd(bool_var1, bool_var2).OnlyEnforceIf(bool_aux)
        model.AddBoolOr(bool_var1.Not(), bool_var2.Not()
                        ).OnlyEnforceIf(bool_aux.Not())
        model.Add(var1 != var2).OnlyEnforceIf(bool_aux)


def all_equal(model: cp_model.CpModel, x: list[IntVar]):
    """
    Ensure that all variables in x are equal:
        x[i] == x[j], for all i,j
    """
    n = len(x)

    if n == 0:
        return

    x0 = x[0]
    for i in range(1, n):
        model.Add(x[i] == x0)


def are_all_equal_csp(model: cp_model.CpModel, x: VarList, prefix: str) -> IntVar:
    """
    Encodes the all equal constraint into a bool var:
        bool_var = all(x[0] == x_i for x_i in x[1:])
    """

    prefix = f"{prefix} - are_all_equal_csp"
    n = len(x)

    if n <= 1:
        are_all_equal_bool = model.NewBoolVar(f"{prefix} - are_all_equal_bool")
        model.Add(are_all_equal_bool == 1)
        return are_all_equal_bool

    x0 = x[0]
    bs: list[IntVar] = []
    for i in range(1, n):
        b = model.NewBoolVar(f"{prefix} - b_{i}")
        model.Add(x[i] == x0).OnlyEnforceIf(b)
        model.Add(x[i] != x0).OnlyEnforceIf(b.Not())
        bs.append(b)

    are_all_equal_bool = are_all_true_csp(
        model, bs, f"{prefix} - are_all_equal_bool")
    return are_all_equal_bool


def are_all_diferent_csp(model: cp_model.CpModel, x: VarList, prefix: str) -> IntVar:
    """
    Encodes the all different constraint into a bool var:
        bool_var = all(x1 != x2 for x1, x2 in combinations(x, 2))
    """

    prefix = f"{prefix} - are_all_diferent_csp"
    n = len(x)

    if n <= 1:
        are_all_different_bool = model.NewBoolVar(
            f"{prefix} - are_all_diferent_csp")
        model.Add(are_all_different_bool == 1)
        return are_all_different_bool

    bs: list[IntVar] = []
    for i, (x1, x2) in enumerate(combinations(x, 2)):
        b = model.NewBoolVar(f"{prefix} - b_{i}")
        model.Add(x1 != x2).OnlyEnforceIf(b)
        model.Add(x1 == x2).OnlyEnforceIf(b.Not())
        bs.append(b)

    are_all_different_bool = are_all_true_csp(
        model, bs, f"{prefix} - are_all_different_bool")
    return are_all_different_bool


def increasing(model: cp_model.CpModel, x: list[IntVar]):
    """
    Ensure that x is in increasing order:
        x[i] <= x[i+1], 0 <= i < n - 1
    """
    n = len(x)
    for i in range(1, n):
        model.Add(x[i - 1] <= x[i])


def increasing_strict(model: cp_model.CpModel, x: list[IntVar]):
    """
    Ensure that x is in strictly increasing order:
        all(x1 < x2 for x1, x2 in zip(x, x[1:]))
    """
    for x1, x2 in zip(x, x[1:]):
        model.Add(x1 < x2)


def regular_distance_csp(model: cp_model.CpModel, x: list[IntVar], dist: int | IntVar):
    """
    Ensures the variables in x are regularly spaced with a distance of dist
    (X is an increasing or decreasing vector with x[i] = x[i-1] + dist):
        x[i] - x[i-1] == dist, 1 <= i < n

    """
    n = len(x)
    if n <= 1:
        return
    for i in range(1, n):
        model.Add(x[i] == x[i - 1] + dist)


def is_increasing_strict_csp(model: cp_model.CpModel, x: list[IntVar], prefix: str):
    """
    Encodes whether x is in strictly increasing order into a bool var:
        bool_var = all(x1 < x2 for x1, x2 in zip(x, x[1:]))
    """
    prefix = f"{prefix} - is_increasing_strict_csp"
    n = len(x)

    if n == 0 or n == 1:
        is_increasing_strict = model.NewBoolVar(
            f"{prefix} - is_increasing_strict")
        model.Add(is_increasing_strict == n)
        return is_increasing_strict

    bools: list[IntVar] = []
    for i, (x1, x2) in enumerate(zip(x, x[1:])):
        bool_var = model.NewBoolVar(f"{prefix} - bool_{i}")
        model.Add(x1 < x2).OnlyEnforceIf(bool_var)
        model.Add(x1 >= x2).OnlyEnforceIf(bool_var.Not())
        bools.append(bool_var)

    is_increasing_strict = are_all_true_csp(
        model, bools, f"{prefix} - is_increasing_strict")

    return is_increasing_strict


def decreasing(model: cp_model.CpModel, x: list[IntVar]):
    """
    Ensure that x is in decreasing order:
        x[i-1] >= x[i], 1 <= i < n
    """
    n = len(x)
    for i in range(1, n):
        model.Add(x[i - 1] >= x[i])


def decreasing_strict(model: cp_model.CpModel, x: list[IntVar]):
    """
    Ensure that x is in strict decreasing order:
        x[i-1] > x[i], 1 <= i < n
    """
    n = len(x)
    for i in range(1, n):
        model.Add(x[i - 1] > x[i])


def member_of(model: cp_model.CpModel, x: VarList, val: int | IntVar, prefix: str):
    """
    Ensures that the value `val` is in the array `x`.
    """
    prefix = f"{prefix} - member_of"
    count = count_vars(model, x, val, prefix)
    model.Add(count >= 1)
    return count


def is_member_of(model: cp_model.CpModel, x: VarList, val: int | IntVar, prefix: str) -> IntVar:
    """
    Returns a bool_var indicating whether val is in x:
        bool_var = val in x
    """
    prefix = f"{prefix} - is_member_of"
    is_member = model.NewBoolVar(f"{prefix} - is_member_bool")
    count = count_vars(model, x, val, prefix)
    model.Add(count >= 1).OnlyEnforceIf(is_member)
    model.Add(count == 0).OnlyEnforceIf(is_member.Not())
    return is_member


def is_not_member_of(model: cp_model.CpModel, x: VarList, val: int | IntVar, prefix: str) -> IntVar:
    """
    Returns a bool_var indicating if val is NOT in x:
        bool_var = val not in x
    """
    prefix = f"{prefix} - is_not_member_of"
    is_member = is_member_of(model, x, val, prefix)
    is_not_member = model.NewBoolVar(f"{prefix} - is_not_member_bool")
    model.Add(is_not_member == is_member.Not())
    return is_not_member


def count_in_set(model: cp_model.CpModel, x: VarList,
                 var_set: VarList, prefix: str) -> IntVar:
    """
    Counts how many variables of x are in the var_set
        count = sum(var in var_set for var in x)
    """
    n = len(x)
    prefix = f"{prefix} - count_in_set"
    count = model.NewIntVar(0, n, f"{prefix} - count")

    bools: list[IntVar] = []
    for i, var in enumerate(x):
        is_member = is_member_of(model, var_set, var, f"{prefix} - var_{i}")
        bools.append(is_member)

    model.Add(sum(bools) == count)
    return count


def compare_multisets_csp(model: cp_model.CpModel, set1: VarList,
                          set2: VarList, prefix: str) -> IntVar:
    """
    Encodes whether set1 and set2 represent the same multiset into a bool_var
    """
    n1 = len(set1)
    n2 = len(set2)
    prefix = f"{prefix} - compare_multisets_csp"
    is_equal = model.NewBoolVar(f"{prefix} - is_equal")

    if n1 != n2:
        model.Add(is_equal == 0)
        return is_equal

    bools: list[IntVar] = []
    for i, var in enumerate(set1):
        count1 = count_vars(
            model, set1, var, f"{prefix} - var_{i}, set1_count")
        count2 = count_vars(
            model, set2, var, f"{prefix} - var_{i}, set2_count")
        bool_var = reif2(model, count1 == count2, count1 !=
                         count2, f"{prefix} - var_{i}, count1 == count2")
        bools.append(bool_var)

    model.AddBoolAnd(bools).OnlyEnforceIf(is_equal)
    model.AddBoolOr([b.Not() for b in bools]).OnlyEnforceIf(is_equal.Not())

    return is_equal


def is_inside_interval_2_csp(model: cp_model.CpModel, interval_var: IntervalVar, val: int | IntVar, prefix: str):
    """
    Returns a bool_var indicating if val is inside the interval represented by interval_var:
        bool_var = a <= val < b, where a, b are the start and end of the interval
    """

    prefix = f"{prefix} - is_inside_interval_csp"

    geq_than_start = reif2(model, val >= interval_var.start_expr(), val < interval_var.start_expr(),  # type: ignore
                           f"{prefix} - geq_than_start")
    less_than_end = reif2(model, val < interval_var.end_expr(), val >= interval_var.end_expr(),  # type: ignore
                          f"{prefix} - less_than_end")

    is_inside_bool = are_all_true_csp(
        model, [geq_than_start, less_than_end], f"{prefix} - is_inside_bool")
    return is_inside_bool


def distance_csp(model: cp_model.CpModel, var1: int | IntVar, var2: int | IntVar, prefix: str) -> IntVar:
    """
    Returns dist_var = |var2 - var1|
    """
    prefix = f"{prefix} - distance_csp"
    domain1 = get_domain(var1)
    domain2 = get_domain(var2)
    lb = min(min(domain1), min(domain2))
    ub = max(max(domain1), max(domain2))
    dist_var = model.NewIntVar(0, ub - lb, f"{prefix} - dist_var")
    model.AddAbsEquality(dist_var, var2 - var1)

    return dist_var


def is_sum_csp(model: cp_model.CpModel, variables: VarList,
               sum_var: int | IntVar, prefix: str) -> IntVar:
    """
    Returns is_sum_bool = sum(variables) == sum_var
    """
    prefix = f"{prefix} - is_sum_csp"
    is_sum_bool = model.NewBoolVar(f"{prefix} - is_sum")
    model.Add(sum(variables) == sum_var).OnlyEnforceIf(is_sum_bool)
    model.Add(sum(variables) != sum_var).OnlyEnforceIf(is_sum_bool.Not())

    return is_sum_bool


def scalar_product_csp(model: cp_model.CpModel, x: VarList, y: VarList, prefix: str) -> IntVar:
    """
    Retuns a integer variable that equals the scalar product of x and y:
        sum_var = sum([x_i * y_i for x_i, y_i in zip(x,y)])
    """
    assert len(x) == len(y)

    prefix = f"{prefix} - scalar_product_csp"

    ts: list[IntVar] = []
    for i, (x_i, y_i) in enumerate(zip(x, y)):
        domains = varlist_domain([x[i], y[i]])
        lb, ub = compute_multiplication_domain(domains)
        t_i = model.NewIntVar(lb, ub, f"{prefix} - t_{i}")
        model.AddMultiplicationEquality(t_i, [x_i, y_i])
        ts.append(t_i)

    domains = varlist_domain(ts)
    slb, sub = compute_sum_domain(domains)

    sum_var = model.NewIntVar(slb, sub, f"{prefix} - sum_var")
    model.Add(sum_var == sum(ts))

    return sum_var


def masked_sum_csp(model: cp_model.CpModel, x: VarList,
                   mask_bools: list[IntVar], prefix: str):
    """
    Returns the masked sum of the values of 'x', with a mask given by mask_bools (a variable only counts toward the sum if the corresponding mask_var is true):
        sum_var = sum(var for var, mask in zip(variables, mask_bools) if mask)
            or
        sum_var = sum(var*mask for var, mask in zip(variables, mask_bools))
    """
    prefix = f"{prefix} - masked_sum_csp"

    assert len(x) == len(mask_bools)

    ts: list[IntVar] = []
    for i, (x_i, mask) in enumerate(zip(x, mask_bools)):
        domains = varlist_domain([x_i, mask])
        lb, ub = compute_multiplication_domain(domains)
        t_i = model.NewIntVar(lb, ub, f"{prefix} - t_{i}")
        model.Add(t_i == x_i).OnlyEnforceIf(mask)
        model.Add(t_i == 0).OnlyEnforceIf(mask.Not())
        ts.append(t_i)

    domains = varlist_domain(ts)
    slb, sub = compute_sum_domain(domains)
    sum_var = model.NewIntVar(slb, sub, f"{prefix} - sum_var")

    model.Add(sum_var == sum(ts))
    return sum_var


def multiplication_csp(model: cp_model.CpModel, variables: VarList, prefix: str) -> IntVar:
    """
    Enforces the multiplication constraint:
        product_var = variables[0] * variables[1] * ... * variables[n-1] = 
            reduce(lambda x, y: x * y, variables)
    """

    domains = varlist_domain(variables)
    (plb, pub) = compute_multiplication_domain(domains)

    product_var = model.NewIntVar(plb, pub, f"{prefix} - product")
    model.AddMultiplicationEquality(product_var, variables)

    # prefix = f"{prefix} - multiplication"
    # temp = model.NewIntVar(1, 1, f"{prefix} - temp_0")
    # model.Add(temp == 1)
    # for i, expression in enumerate(variables):
    #     new_temp = model.NewIntVar(plb, pub, f"{prefix} - temp_{i + 1}")
    #     model.AddMultiplicationEquality(new_temp, [temp, expression])
    #     temp = new_temp
    # model.Add(product_var == temp)
    return product_var


def is_inside_interval_csp(model: cp_model.CpModel, x: LinearExprT,
                           a: LinearExprT,
                           b: LinearExprT, prefix: str) -> IntVar:
    """
    Encodes the constraint:
       a <= x <= b into a boolean variable
    into a boolean variable is_inside_bool
    """
    prefix = f"{prefix} - inside_interval_csp"

    b1 = model.NewBoolVar(f'{prefix} - bool1 - a <= x')
    reif2_2(model, a <= x, a > x, b1)  # type: ignore
    b2 = model.NewBoolVar(f'{prefix} - bool1 - x <= b')
    reif2_2(model, x <= b, x > b, b2)  # type: ignore

    is_inside = are_all_true_csp(model, [b1, b2], f"{prefix} - is_inside_bool")

    return is_inside


def renban_csp(model: cp_model.CpModel, variables: VarList, prefix: str) -> tuple[IntVar, IntVar]:
    """
    Adds a renban constraint. On a renban, all values must be different and all values must be consecutive but can be in any order
        is_renban = len(set(variables)) == len(variables) and max(variables) == min(variables) + len(variables) - 1
    Returns that start (min(variables)) and end (max(variables)) of the renban

    Examples:
        [2, 3, 4], [7, 5, 6, 4], [10, 9, 8] are renban
        [2, 3, 2], [2, 5, 4] are not renban
    """
    domains = varlist_domain(variables)
    lb = min(min(domain) for domain in domains)
    ub = max(max(domain) for domain in domains)

    prefix = f"{prefix} - renban_csp"
    start = model.NewIntVar(lb, ub, f'{prefix} - start')
    end = model.NewIntVar(lb, ub, f'{prefix} - end')
    model.Add(end == start + len(variables) - 1)
    model.AddAllDifferent(variables)

    for var in variables:
        model.Add(start <= var)
        model.Add(var <= end)

    return start, end


def is_renban_csp(model: cp_model.CpModel, variables: VarList,
                  prefix: str) -> IntVar:
    """
    Returns a bool var indicating if the variables form a renban. On a renban, all values must be different and all values must be consecutive but can be in any order
        is_renban = len(set(variables)) == len(variables) and max(variables) == min(variables) + len(variables) - 1
    Examples:
        [2, 3, 4], [7, 5, 6, 4], [10, 9, 8] are renban
        [2, 3, 2], [2, 5, 4] are not renban
    """
    domains = varlist_domain(variables)
    lb = min(min(domain) for domain in domains)
    ub = max(max(domain) for domain in domains)

    prefix = f"{prefix} - is_renban_csp"

    start = model.NewIntVar(lb, ub, f'{prefix} - start')
    end = model.NewIntVar(lb, ub, f'{prefix} - end')
    model.AddMinEquality(start, variables)
    model.AddMaxEquality(end, variables)

    # all diferent
    all_different = are_all_diferent_csp(model, variables, f"{prefix}")

    # all values inside interval are in variables
    all_values_in_interval = reif2(model,
                                   end == start + len(variables) - 1,
                                   end != start + len(variables) - 1,
                                   f"{prefix} - has_all_values")

    is_renban = are_all_true_csp(
        model, [all_different, all_values_in_interval], f"{prefix} - is_renban")

    return is_renban


def whispers_csp(model: cp_model.CpModel, line_vars: list[IntVar],
                 min_dist: int | IntVar, prefix: str):
    """
    Adds a whispers constraint to the model, i.e., adjacent variables in line_vars must have a
    distance >= min_dist:
        abs(line_vars[i] - line_vars[i-1]) >= min_dist, 0 < i < n
    """
    prefix = f"{prefix} - whispers_csp"

    for i, var1 in enumerate(line_vars[0:-1]):
        var2 = line_vars[i + 1]
        dist_var = distance_csp(model, var1, var2, prefix)
        model.Add(dist_var >= min_dist)


def is_whispers_csp(model: cp_model.CpModel, variables: VarList, min_dist: int | IntVar) -> IntVar:
    """
    Returns a bool var indicating if the variables form a whispers line. On a whispers line, adjacent variables must have a difference of at least min_dist
        is_whispers = all(abs(x2 - x1) >= min_dist for x1, x2 in zip(variables, variables[1:]))
    Examples:
        [2, 7, 1], [7, 1, 6, 1], [10, 2, 8, 0, 5] are whispers if min_dist = 5
        [2, 6, 1], [2, 8, 4, 9] are not whispers if min_dist = 5
    """

    prefix = f"is_whispers_csp"
    # is_whispers = model.NewBoolVar(f"{prefix} - is_whispers")

    bools: list[IntVar] = []
    for i, var1 in enumerate(variables[0:-1]):
        var2 = variables[i + 1]
        dist_var = distance_csp(model, var1, var2, prefix)
        b = model.NewBoolVar(f'whispers - |{var1}-{var2}| < {min_dist}')
        bools.append(b)
        model.Add(dist_var >= min_dist).OnlyEnforceIf(b)
        model.Add(dist_var < min_dist).OnlyEnforceIf(b.Not())

    is_whispers = are_all_true_csp(model, bools, f"{prefix} - is_whispers")

    return is_whispers


def palindrome_csp(model: cp_model.CpModel, line_vars: VarList):
    """
    Adds a palindrome constraint to the model:
        line_vars[i] == line_vars[n-i-1], n = len(line_vars)
    """
    n = len(line_vars)
    for i in range(n // 2):
        model.Add(line_vars[i] == line_vars[n - i - 1])


def consecutive_csp(model: cp_model.CpModel, var1: IntVar | int, var2: IntVar | int):
    """
    Enforces the consecutive constraint, i.e., abs(var2 - var1) == 1
    """
    model.AddAbsEquality(1, var2 - var1)


def nonconsecutive_csp(model: cp_model.CpModel, var1: IntVar, var2: IntVar):
    """
    Enforces the nonconsecutive constraint, i.e., abs(var2 - var1) != 1
    """

    model.Add(var2 - var1 != 1)
    model.Add(var1 - var2 != 1)


def are_consecutive_csp(model: cp_model.CpModel, var1: IntVar, var2: IntVar, prefix: str):
    """
        Returns a bool var indicating if the var1 and var2 are consecutive
            are_consecutive = abs(var2 - var1) == 1
    """
    domain1, domain2 = get_domain(var1), get_domain(var2)
    lb = min(min(domain1), min(domain2))
    ub = max(max(domain1), max(domain2))
    prefix = f"{prefix} - are_consecutive_csp"

    dist = model.NewIntVar(0, ub - lb, f"{prefix} - dist")
    model.AddAbsEquality(dist, var2 - var1)
    are_consecutive = model.NewBoolVar(f"{prefix} - bool_var")
    model.Add(dist == 1).OnlyEnforceIf(are_consecutive)
    model.Add(dist != 1).OnlyEnforceIf(are_consecutive.Not())

    return are_consecutive


def is_ratio_1_r_csp(model: cp_model.CpModel, var1: IntVar | int, var2: IntVar | int,
                     r: int | IntVar, prefix: str):
    """
    Returns a bool var indicating if the var1 and var2 are in a 1:r ratio
        is_ratio = r*var1 == var2 or var2*r == var1
    For example:
        [1, 2], [4, 2], [8, 4], [8, 16] are in a 1:2 ratio
        [2, 6], [12, 4] are in a 1:3 ratio
        [2, 3], [5, 3] are not a 1:2 ratio or 1:3 ratio

    """
    domain1 = get_domain(var1)
    domain2 = get_domain(var2)
    # lb = min(min(var.Proto().domain) for var in [var1, var2])
    ub = max(max(domain1), max(domain2))
    prefix = f"{prefix} - is_ratio_1/x_csp"
    is_ratio = model.NewBoolVar(f'{prefix} - is_ratio')

    if isinstance(r, int):
        case1 = reif2(model, r * var1 == var2,
                      r * var1 != var2, f'{prefix} - r * var1 == var2')
        case2 = reif2(model, r * var2 == var1,
                      r * var2 != var1, f'{prefix} - r * var1 == var2')

        is_ratio = are_any_true_csp(
            model, [case1, case2], f"{prefix} - is_ratio")
        return is_ratio

    # r * var1 == var2
    domain_r = get_domain(r)

    lb, ub = compute_multiplication_domain([domain1, domain_r])
    t1 = model.NewIntVar(lb, ub, f"{prefix} - t1")
    model.AddMultiplicationEquality(t1, [var1, r])
    case1 = reif2(model, t1 == var2, t1 !=
                  var2, f'{prefix} - r_var * var1 == var2')

    # r * var2 == var1
    lb, ub = compute_multiplication_domain([domain2, domain_r])
    t2 = model.NewIntVar(lb, ub, f"{prefix} - t2")
    model.AddMultiplicationEquality(t2, [var2, r])
    case2 = reif2(model, t2 == var1, t2 !=
                  var1, f'{prefix} - r_var * var2 == var1')

    # r * var1 == var2 OR r * var2 == var1
    is_ratio = are_any_true_csp(model, [case1, case2], f"{prefix} - is_ratio")
    return is_ratio


def is_sandwiched_csp(model: cp_model.CpModel, variables: VarList, idx: int,
                      a: int | IntVar, b: int | IntVar, prefix: str) -> IntVar:
    """ Returns a bool variable indicating if the variable at index idx is sandwiched between a and b
            bool_var = (a in variables[:idx] and b in variables[idx+1:]) or 
                     (b in variables[:idx] and a in variables[idx+1:])

        For example if variables=[2, 9, 4, 6, 3, 1, 1, 5], a=1 and b=4:
            bool_var will be 1 for idx = 3, 4, 5 and 0 for all other indexes
    """
    prefix = f"{prefix} - is_sandwiched_csp"

    is_sandwiched = model.NewBoolVar(f"{prefix} - is_sandwiched_bool")
    if idx < 0 or idx >= len(variables):
        model.Add(is_sandwiched == 0)
        return is_sandwiched

    left_side = variables[0:idx]
    right_side = variables[idx+1:]

    a_member_of_left = is_member_of(
        model, left_side, a, f"{prefix} - a_member_of_left_side")
    b_member_of_right = is_member_of(
        model, right_side, b, f"{prefix} - b_member_of_right_side")
    is_middle_bool_1 = are_all_true_csp(model, [a_member_of_left, b_member_of_right],
                                        f"{prefix} - is_middle_bool_1")

    b_member_of_left = is_member_of(
        model, left_side, b, f"{prefix} - b_member_of_left_side")
    a_member_of_right = is_member_of(
        model, right_side, a, f"{prefix} - a_member_of_right_side")
    is_middle_bool_2 = are_all_true_csp(model, [b_member_of_left, a_member_of_right],
                                        f"{prefix} - is_middle_bool_2")

    model.AddBoolOr(is_middle_bool_1, is_middle_bool_2).OnlyEnforceIf(
        is_sandwiched)
    model.AddBoolAnd(is_middle_bool_1.Not(), is_middle_bool_2.Not()).OnlyEnforceIf(
        is_sandwiched.Not())

    return is_sandwiched


def sandwich_bools_csp(model: cp_model.CpModel, variables: VarList,
                       a: int | IntVar, b: int | IntVar, prefix: str) -> list[IntVar]:
    """
        Returns a list of bool vars for every variable in variables, indicating if it is sandwiched between a and b:
            bools = [(a in variables[:i] and b in variables[i+1:]) or 
                     (b in variables[:i] and a in variables[i+1:])
                      for i, var in enumerate(variables)]
        For example if a=1 and b=9:
            [2, 9, 4, 6, 3, 1, 1, 5] -> [0, 0, 1, 1, 1, 1, 0, 0]
            [5, 1, 3, 5, 4, 9, 6, 5] -> [0, 0, 1, 1, 1, 0, 0, 0]
            [5, 7, 3, 1, 9, 6, 5, 2] -> [0, 0, 0, 0, 0, 0, 0, 0]
            [4, 0, 1, 7, 3, 5, 6, 8] -> [0, 0, 0, 0, 0, 0, 0, 0]
    """

    prefix = f"{prefix} - sandwich_bools_csp"

    is_middle_bools: list[IntVar] = []
    for j, _ in enumerate(variables):
        is_sandwiched = is_sandwiched_csp(
            model, variables, j, a, b, f"{prefix} - idx={j}")
        is_middle_bools.append(is_sandwiched)

    return is_middle_bools


def sandwich_sum_csp(model: cp_model.CpModel, variables: list[IntVar],
                     a: int | IntVar, b: int | IntVar, prefix: str) -> IntVar:
    """
    Returns an int var equal to the sum of the values of variables sandwiched between a and b
    bools = [(a in variables[:i] and b in variables[i+1:]) or 
            (b in variables[:i] and a in variables[i+1:])
            for i, var in enumerate(variables)]
    sum_var = [var for var, bool_var in zip(variables, bools) if bool_var]
        For example if a=1 and b=9:
            [2, 9, 4, 6, 3, 1, 1, 5] -> sum_var = 4 + 6 + 3 + 1 = 14
            [5, 1, 3, 5, 4, 9, 6, 5] -> sum_var = 3 + 5 + 4 = 12
            [5, 7, 3, 1, 9, 6, 5, 2] -> sum_var = 0
            [4, 0, 1, 7, 3, 5, 6, 8] -> sum_var = 0
    """

    prefix = f"{prefix} - sandwich_sum_scp"

    is_middle_bools = sandwich_bools_csp(model, variables, a, b, prefix)
    sum_val = masked_sum_csp(model, variables, is_middle_bools, f"{prefix}")

    return sum_val


def first_x_bools_csp(model: cp_model.CpModel, n: int,
                      x: int | IntVar, prefix: str) -> list[IntVar]:
    """
    Returns a list of bool vars of size n, where the first x entries are 1 and the remaining are 0. x may be greater than n
        bools = [i<x for i in range(n)]
    For example if n=10 and x=4:
        bools = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]

    Useful for x-sum and  battlefield constraints.
    """

    prefix = f"{prefix} - count_x_csp"
    bools: list[IntVar] = []
    for j in range(n):
        bool_var = model.NewBoolVar(f"{prefix} - bool_var_{j}")
        model.Add(j < x).OnlyEnforceIf(bool_var)
        model.Add(j >= x).OnlyEnforceIf(bool_var.Not())
        bools.append(bool_var)

    return bools


def shifted_first_x_bools_csp(model: cp_model.CpModel, n: int,
                              x: int | IntVar, a: int | IntVar, prefix: str):
    """
    Returns a list of bool vars of size n, where the first x entries, starting at index a, are 1 and the remaining are 0. x may be greater than n
        bools = [a <= i < a + x for i in range(n)]
    For example if n=10, x=4, a = 2:
        bools = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0]
    """

    prefix = f"{prefix} - shifted_first_x_bools_csp"
    bools: list[IntVar] = []

    # a <= j < a + x
    for j in range(n):
        is_inside = is_inside_interval_csp(
            model, j, a, a+x-1, f"{prefix} - is_inside_bool")  # type: ignore
        bools.append(is_inside)

    return bools


def x_sum_csp(model: cp_model.CpModel, variables: list[IntVar], x: int | IntVar, prefix: str) -> IntVar:
    """
    Returns an int var representing the sum of the first x elements of variables.
        sum_var = [var for i, var in enumerate(variables) if i<x]
    For example, if
        variables = [3, 9, 4, 1, 7, 8, 9] and x = 4, sum_var = 17
    """

    prefix = f"{prefix} - x_sum_csp"
    n = len(variables)

    count_x_bools = first_x_bools_csp(model, n, x, prefix)
    sum_var = masked_sum_csp(
        model, variables, count_x_bools, f"{prefix} - sum_var")
    return sum_var


def shifted_x_sum_csp(model: cp_model.CpModel, variables: list[IntVar], sum_var: int | IntVar,
                      x: int | IntVar, a: int | IntVar, prefix: str):
    """
    Enforces the shifted x-sum constraint, the sum of the first X digits from the Nth variable,
    where X is the digit in the Nth cell and N is the digit in the first cell from that side:
    shifted_x_sum = sum(variables[N:N+X])
    """

    prefix = f"{prefix} - shifted_x_sum_csp"
    n = len(variables)
    count_x_bools = shifted_first_x_bools_csp(model, n, x, a, prefix)
    model.Add(sum(count_x_bools) == x)
    masked_sum = masked_sum_csp(model, variables, count_x_bools, f"{prefix}")
    model.Add(masked_sum == sum_var)


def shortsighted_x_sum_csp(model: cp_model.CpModel, variables: list[IntVar], sum_var: int | IntVar,
                           x: int | IntVar):
    """
    Enforces the shortsighted x-sum constraint:
        sum_var is the sum of the first X or X-1 variables, where variables[0] = X
    """

    domains = varlist_domain(variables)
    prefix = f"shortsighted_x_sum_csp"
    lb = min(min(domain) for domain in domains)
    ub = max(max(domain) for domain in domains)

    sum_x = x_sum_csp(model, variables, x, f"{prefix} - sum_X")

    x_1 = model.NewIntVar(lb - 1, ub - 1, f"{prefix} - (X-1)")
    model.Add(x_1 == x - 1)
    sum_x_1 = x_sum_csp(model, variables, x_1, f"{prefix} - sum_(X-1)")

    member_of(model, [sum_x, sum_x_1], sum_var, f"{prefix}")


def broken_x_sum_csp(model: cp_model.CpModel, variables: list[IntVar], sum_var: int | IntVar,
                     x: int | IntVar):
    """
    Enforces the broken x-sum constraint: sum_var is the sum of the first X-1 or X+1 variables
    """

    prefix = f"broken_x_sum_csp"

    x_lb, x_ub = get_domain(x)

    x_m_1 = model.NewIntVar(x_lb - 1, x_ub - 1, f"{prefix} - (X-1)")
    model.Add(x_m_1 == x - 1)
    sum_x_m_1 = x_sum_csp(model, variables, x_m_1, f"{prefix} - sum_(X-1)")

    x_p_1 = model.NewIntVar(x_lb + 1, x_ub + 1, f"{prefix} - (X+1)")
    model.Add(x_p_1 == x + 1)
    sum_x_p_1 = x_sum_csp(model, variables, x_p_1, f"{prefix} - sum_(X+11)")

    member_of(model, [sum_x_m_1, sum_x_p_1], sum_var, f"{prefix}")


def xor_csp(model: cp_model.CpModel, a: IntVar, b: IntVar, prefix: str) -> IntVar:
    """
    Returns xor_res = a XOR b
    """
    prefix = f"{prefix} - xor_csp"

    xor_aux1 = model.NewBoolVar(f"{prefix} - xor_aux1")
    model.AddBoolAnd(a, b.Not()).OnlyEnforceIf(xor_aux1)
    model.AddBoolOr(a.Not(), b).OnlyEnforceIf(xor_aux1.Not())

    xor_aux2 = model.NewBoolVar(f"{prefix} - xor_aux2")
    model.AddBoolAnd(a.Not(), b).OnlyEnforceIf(xor_aux2)
    model.AddBoolOr(a, b.Not()).OnlyEnforceIf(xor_aux2.Not())

    xor_res = model.NewBoolVar(f"{prefix} - xor_res")
    model.AddBoolOr(xor_aux1, xor_aux2).OnlyEnforceIf(xor_res)
    model.AddBoolAnd(xor_aux1.Not(), xor_aux2.Not()
                     ).OnlyEnforceIf(xor_res.Not())

    return xor_res


def greater_than_all_csp(model: cp_model.CpModel, variables: list[IntVar], target: IntVar | int, prefix: str) -> IntVar:
    """
    Retuns a bool var indicating if target is greater than all variables in 'variables'
        bool_var = all([target > var for var in variables])
    """

    prefix = f"{prefix} - greater_than_all_csp"
    n = len(variables)

    if n == 0:
        greater_than_all_bool = model.NewBoolVar(
            f"{prefix} - greater_than_all_bool")
        model.Add(greater_than_all_bool == 1)
        return greater_than_all_bool

    bools = [model.NewBoolVar(f"{prefix} - b_{i}") for i in range(n)]
    for i, var in enumerate(variables):
        model.Add(var < target).OnlyEnforceIf(bools[i])
        model.Add(var >= target).OnlyEnforceIf(bools[i].Not())

    greater_than_all_bool = are_all_true_csp(
        model, bools, f"{prefix} - greater_than_all_bool")

    return greater_than_all_bool


def skyscraper_csp(model: cp_model.CpModel, count: IntVar | int, variables: list[IntVar]):
    """
    The variables represent buildings of height equal to their value. Buildings of height x at index i obstruct the view of buildings smaller than x beyong i (for indexes greater than i).

    This function returns an int var representing the number of skyscrapers that can be seen from the start of variables.

    Enforces the Skyscraper constraint:
        count = sum(all(variables[j] < var_i for j in range(i)) for i, var_i in enumerate(variables))
    """

    prefix = f"skyscraper_csp"

    bools: list[IntVar] = []
    for i, var in enumerate(variables):
        left_side = variables[:i]
        greater_than_all_bool = greater_than_all_csp(
            model, left_side, var, f"{prefix} - {i}")
        bools.append(greater_than_all_bool)

    model.Add(sum(bools) == count)
    return bools


def conditional_skyscraper_csp(model: cp_model.CpModel, count: int | IntVar,
                               variables: list[IntVar],
                               cond_bools: list[IntVar]):
    """
    Enforces the Skyscraper constraint:
        bool[i] == all([variables[j] < variables[i] for j in range(0, i)])      (j < i)
        sum(bools) == count
    """

    prefix = f"conditional_skyscraper_csp"
    n = len(variables)
    larger_than_left_side_bools: list[IntVar] = []
    seen_skyscrapers_bools = [model.NewBoolVar(
        f"{prefix}: skyscraper_is_seen_bool_{i}") for i in range(n)]

    for i, var in enumerate(variables):
        left_side = get_left_side(variables, i)
        larger_than_all_bool = greater_than_all_csp(
            model, left_side, var, f"{prefix} - {i}")
        larger_than_left_side_bools.append(larger_than_all_bool)

        model.AddBoolAnd(larger_than_left_side_bools[i], cond_bools[i]).OnlyEnforceIf(
            seen_skyscrapers_bools[i])
        model.AddBoolOr(larger_than_left_side_bools[i].Not(), cond_bools[i].Not()).OnlyEnforceIf(
            seen_skyscrapers_bools[i].Not())

    model.Add(sum(seen_skyscrapers_bools) == count)
    return seen_skyscrapers_bools


def count_lesser_until_greater_csp(model: cp_model.CpModel,
                                   variables: list[IntVar], target: int | IntVar):
    """
    Counts the variables that are smaller than target until one of the variables is larger. FOr example,
    if target = 7 and variables = [5,3,6,4,1,9,8,2] then the count is 5 because [5,3,6,4,1] are smaller than 7, and 9 is larger.
    """

    prefix = f"count_lesser_until_greater_csp"
    n = len(variables)
    count = model.NewIntVar(0, n, f"{prefix} - count")

    bools: list[IntVar] = []
    for i, _ in enumerate(variables):
        left_side = variables[0:i+1]
        larger_than_all_bool = greater_than_all_csp(
            model, left_side, target, f"{prefix}_{i}")
        bools.append(larger_than_all_bool)

    model.Add(sum(bools) == count)
    return count


def is_farsight_csp(model: cp_model.CpModel, n: int | IntVar, variables: list[IntVar], prefix: str):
    """
    Encodes the farsight constraint into a bool var:
        |variables[0] - variables[n]| == 1 <=> is_farsight
    """

    prefix = f"{prefix} - is_farsight_csp"
    is_farsight = model.NewBoolVar(f"{prefix} - is_farsight")
    size = len(variables)
    lb = min(min(var.Proto().domain) for var in variables)
    ub = max(max(var.Proto().domain) for var in variables)

    # if n < 0 or n >= size => is not farsight; n does not index the list
    b1 = reif2(model, n < 0, n >= 0, f"{prefix} - n < 0")
    b2 = reif2(model, n >= size, n < size, f"{prefix} - n >= size")
    inside_interval = model.NewBoolVar(f"{prefix} - n < 0 OR n >= size")
    model.AddBoolOr(b1, b2).OnlyEnforceIf(inside_interval.Not())
    model.AddBoolAnd(b1.Not(), b2.Not()).OnlyEnforceIf(inside_interval)

    # if not inside interval set target = variables[0] as default behaviour to avoid multiple solutions
    target = model.NewIntVar(lb, ub, f"{prefix} - target")
    idx_var = model.NewIntVar(0, size - 1, f"{prefix} - idx")
    model.Add(idx_var == n).OnlyEnforceIf(inside_interval)
    model.Add(idx_var == 0).OnlyEnforceIf(inside_interval.Not())
    model.AddElement(idx_var, variables, target)

    is_consecutive = are_consecutive_csp(
        model, variables[0], target, f"{prefix}")

    model.AddBoolAnd(
        is_consecutive, inside_interval).OnlyEnforceIf(is_farsight)
    model.AddBoolOr(is_consecutive.Not(), inside_interval.Not()
                    ).OnlyEnforceIf(is_farsight.Not())

    return is_farsight


def count_watchtower_csp(model: cp_model.CpModel, watchtower_idx: int, variables: list[IntVar], prefix: str) -> IntVar:
    """
    The variables represent buildings of height equal to their value. The building at watchtower_idx is a watchtower. Watchtowers see buildings to their left and right, but cannot see buildings  taller than their own height, nor past them. This function returns an int var corresponding to how many buildings the watchtower can see.
    """

    prefix = f"{prefix} - count_watchtower"
    n = len(variables)

    assert 0 <= watchtower_idx < n

    target = variables[watchtower_idx]
    left_side = variables[0:watchtower_idx]
    left_side.reverse()
    right_side = variables[watchtower_idx+1:]
    count_left = count_lesser_until_greater_csp(model, left_side, target)
    count_right = count_lesser_until_greater_csp(model, right_side, target)

    count = model.NewIntVar(0, n, f"{prefix} - count")
    model.Add(count_left + count_right == count)
    return count


def is_watchtower_csp(model: cp_model.CpModel, var: IntVar,
                      row_vars: list[IntVar], col_vars: list[IntVar],
                      prefix: str) -> IntVar:
    """
    Returns a bool var indicating if var is a watchtower. A var is a watchtower if the total number of buildings it can see in its row and column, plus itself, are equal to its value.

    The variables represent buildings of height equal to their value. The building at watchtower_idx is a watchtower. Watchtowers see buildings to their left and right, but cannot see buildings  taller than their own height, nor past them.
    """

    prefix = f"{prefix} - is_watchtower_csp"
    is_watchtower = model.NewBoolVar(f"{prefix} - is_watchtower")
    row_idx = row_vars.index(var)
    col_idx = col_vars.index(var)
    n_row = len(row_vars)
    n_col = len(col_vars)
    in_row = 0 <= row_idx < n_row
    in_col = 0 <= col_idx < n_col

    if not in_row and not in_col:
        model.Add(is_watchtower == 0)
        return is_watchtower

    if in_row:
        count_row = count_watchtower_csp(
            model, row_idx, row_vars, f"{prefix} - count_row")
    else:
        count_row = 0

    if in_col:
        count_col = count_watchtower_csp(
            model, col_idx, col_vars, f"{prefix} - count_col")
    else:
        count_col = 0

    model.Add(count_row + count_col + 1 == var).OnlyEnforceIf(is_watchtower)
    model.Add(count_row + count_col + 1 !=
              var).OnlyEnforceIf(is_watchtower.Not())

    return is_watchtower


def modulo_count_csp(model: cp_model.CpModel,
                     target: int | IntVar,
                     mod: int | IntVar,
                     variables: list[IntVar], prefix: str) -> IntVar:
    """
    Returns an int var counting the number of variables 'in variables' whose remainder when devided by mod is equal to target
        count == sum([var % mod == target for var in variables])
    """

    prefix = f"{prefix} - modulo_count_csp"
    lb, ub = get_domain(mod)
    bound = max(abs(lb), abs(ub))

    n = len(variables)
    count = model.NewIntVar(0, n, f"{prefix} - count")

    bools = [model.NewBoolVar(f"modular-count-bool-{i}") for i in range(n)]
    for i, var in enumerate(variables):
        mod_res = model.NewIntVar(-(bound-1), bound-1, f"modulo_count")
        model.AddModuloEquality(mod_res, var, mod)
        model.Add(mod_res == target).OnlyEnforceIf(bools[i])
        model.Add(mod_res != target).OnlyEnforceIf(bools[i].Not())

    model.Add(sum(bools) == count)
    return count


def distance_to_target_csp(model: cp_model.CpModel,
                           from_idx: int | IntVar,
                           value: int | IntVar,
                           variables: list[IntVar]) -> IntVar:
    """
    Computes the distance for d = |from_idx - j|, where j is such that variables[j] == value:
    """

    n = len(variables)
    target_index = model.NewIntVar(0, n - 1, f"distanceToTarget-index")
    model.AddElement(target_index, variables, value)
    dist = model.NewIntVar(0, n, f"distanceToTarget-dist")
    model.AddAbsEquality(dist, from_idx - target_index)

    return dist


def battlefield_csp(model: cp_model.CpModel, variables: list[IntVar], sum_var: int | IntVar):
    """
    Consider the first X variables and the last Y variables in 'variables', where X is the value of the first variable and Y is the value of the last variable. 
    This function returns the sum of values in variables where these groups overlap, or the sum of the values in the gap between the groups if they don't overlap.
    """
    reversed_vars = list(reversed(variables))
    prefix = f"battlefield_csp"

    n = len(variables)
    bools1 = first_x_bools_csp(
        model, n, variables[0], f"{prefix} - left_to_right")
    bools2 = first_x_bools_csp(
        model, n, reversed_vars[0], f"{prefix} - right_to_left")
    bools2.reverse()

    overlap = [model.NewBoolVar(f"{prefix} - overlap_bool_{var.Name()}")
               for var in variables]
    for i, b in enumerate(overlap):
        res = xor_csp(model, bools1[i], bools2[i], f"{prefix} - xor_{i}")
        model.Add(b == res.Not())

    masked_sum = masked_sum_csp(model, variables, overlap, f"{prefix}")
    model.Add(masked_sum == sum_var)

    return overlap


def is_magic_square_csp(model: cp_model.CpModel, square: list[list[IntVar]]):
    """
    Encodes a magic square constraint into a boolean
    """
    variables = [var for row in square for var in row]
    m = len(square)
    n = len(variables)
    prefix = f"is_magic_square_csp"
    if n % len(square) != 0:
        return

    for row in square:
        if len(row) != len(square):
            return

    # lb = min(min(var.Proto().domain) for var in variables)
    ub = max(max(var.Proto().domain) for var in variables)
    min_sum = 0
    max_sum = sum(range(ub - m + 1, ub + 1))

    sum_var = model.NewIntVar(min_sum, max_sum, f"{prefix} - sum_magic_square")

    bools_row = [model.NewBoolVar(
        f"magic-square-rows-bool-{i}") for i in range(m)]
    for i, row in enumerate(square):
        model.Add(sum(row) == sum_var).OnlyEnforceIf(bools_row[i])
        model.Add(sum(row) != sum_var).OnlyEnforceIf(bools_row[i].Not())

    bools_col = [model.NewBoolVar(
        f"magic-square-cols-bool-{i}") for i in range(m)]
    for j in range(m):
        col = [square[i][j] for i in range(m)]
        model.Add(sum(col) == sum_var).OnlyEnforceIf(bools_col[j])
        model.Add(sum(col) != sum_var).OnlyEnforceIf(bools_col[j].Not())

    n_diag = [square[i][i] for i in range(m)]
    n_diag_bool = model.NewBoolVar(f"magic-square-n_diag-bool")
    model.Add(sum(n_diag) == sum_var).OnlyEnforceIf(n_diag_bool)
    model.Add(sum(n_diag) != sum_var).OnlyEnforceIf(n_diag_bool.Not())

    p_diag = [square[m - i - 1][i] for i in range(m)]
    p_diag_bool = model.NewBoolVar(f"magic-square-p_diag-bool")
    model.Add(sum(p_diag) == sum_var).OnlyEnforceIf(p_diag_bool)
    model.Add(sum(p_diag) != sum_var).OnlyEnforceIf(p_diag_bool.Not())

    all_bools = bools_row + bools_col + [n_diag_bool] + [p_diag_bool]

    is_magic_square_bool = are_all_true_csp(
        model, all_bools, f"{prefix} - is_magic_square_bool")
    model.Add(sum_var == 0).OnlyEnforceIf(is_magic_square_bool.Not())

    return is_magic_square_bool


def count_until_target(model: cp_model.CpModel, variables: list[IntVar], target: int | IntVar) -> IntVar:
    """
    Returns the idx of the first occurrence of target in variables (starting at 1).
    For example if value = 6 and variables = [3,2,6,3,2,6] then idx = 3
    """

    n = len(variables)
    prefix = f"count_until_target"
    dist = model.NewIntVar(0, n, f"{prefix} - dist")

    if n == 0:
        model.Add(dist == 0)
        return dist

    bools: list[IntVar] = []
    for i, var in enumerate(variables):
        left_side = get_left_side(variables, i)
        b = is_not_member_of(model, left_side + [var], target, prefix)
        bools.append(b)

    model.Add(sum(bools) == dist)
    return dist


def cycle_order_csp(model: cp_model.CpModel, variables: list[IntVar], start_idx: int):
    """
    Returns the order of a cycle inside the variables array.
    For example suppose variables = [5, x, x, x, 9, x, x, x, 1]
    The order of the cycle that starts at variables[0] is 3
    """
    n = len(variables)

    transition_vars = [model.NewIntVar(
        1, n + 1, f"t{i + 1}") for i in range(n)]
    model.Add(transition_vars[0] == variables[start_idx])
    for i, _ in enumerate(transition_vars[1:], 1):
        temp = model.NewIntVar(0, n - 1, f"temp")
        model.Add(temp == transition_vars[i - 1] - 1)
        model.AddElement(temp, variables, transition_vars[i])

    count = count_until_target(model, transition_vars, start_idx + 1)
    _, ub = count.Proto().domain
    order = model.NewIntVar(0, ub + 1, f"cycle-order: order")
    model.Add(order == count + 1)

    return order


def factors_csp(model: cp_model.CpModel, var1: IntVar, var2: IntVar, prefix: str):
    """
    Enforces the constraint: var1 % var2 == 0 or var2 % vars1 == 0, i.e., one variable must be divisile by the other
    """

    [_, ub1] = var1.Proto().domain
    [_, ub2] = var2.Proto().domain
    prefix = f"{prefix} - factors_csp"

    b = model.NewBoolVar(f'{prefix} - bool_{var1.Name()}_{var2.Name()}')
    target1 = model.NewIntVar(
        0, ub2, f'{prefix} - t1 = {var1.Name()} mod {var2.Name()}')
    target2 = model.NewIntVar(
        0, ub1, f'{prefix} - t2 = {var2.Name()} mod {var1.Name()}')

    model.AddModuloEquality(target1, var1, var2)
    model.AddModuloEquality(target2, var2, var1)

    model.Add(target1 == 0).OnlyEnforceIf(b)
    model.Add(target2 == 0).OnlyEnforceIf(b.Not())


def is_unimodular_csp(model: cp_model.CpModel, x: list[IntVar], mod: int, prefix: str) -> tuple[IntVar, IntVar]:
    """
    Returns a bool var that indicates if x is unimodular, i.e., if the remainder of every var in x when divided by mod is the same, and the remainder (if it exists, if not it is set to zero by default)
        is_unimodular = len(set(x_i % mod for x_i in x)) == 1
    On an unimodular lines: x[i] % mod = t, for some t in [0, mod-1] and for all x[i] in x
    """
    prefix = f"{prefix} - is_unimodular_csp"

    target = model.NewIntVar(0, mod-1, f"{prefix} - target")
    if len(x) == 0:
        is_unimodular = model.NewBoolVar(f"{prefix} - is_unimodular")
        model.Add(is_unimodular == 0)
        model.Add(target == 0)
        return is_unimodular, target

    targets: list[IntVar] = []
    for i, x_i in enumerate(x):
        target_i = model.NewIntVar(0, mod-1, f"{prefix} - target_{i}")
        model.AddModuloEquality(target_i, x_i, mod)
        targets.append(target_i)

    is_unimodular = are_all_equal_csp(
        model, targets, f"{prefix} - is_unimodular")

    model.Add(target == targets[0]).OnlyEnforceIf(is_unimodular)
    model.Add(target == 0).OnlyEnforceIf(is_unimodular.Not())

    return is_unimodular, target


def is_modular_line_csp(model: cp_model.CpModel, x: list[IntVar], mod: int, prefix: str) -> IntVar:
    """
    Encodes the modular line constraint onto a boolean variable.
    On a modular lines, every set of mod sequential digits has a value that belong to each congruent group:
        x[j] % mod = t[j], for i <= j <= i + mod - 1, all t[j]'s form a set {0, ..., mod - 1} not necessarily in order

    For example, in modular mod 3 lines, every set of three sequential digits contains one digit from {1,4,7},
    one from {2,5,8} and one from {3,6,9}.
    """
    n = len(x)
    seq_size = mod
    num_groups = min(seq_size, n)
    prefix = f"{prefix} - is_modular_line_csp"

    unimodular_bools: list[IntVar] = []
    targets: list[IntVar] = []
    for j in range(num_groups):
        group = x[j::seq_size]

        is_unimodular, target = is_unimodular_csp(
            model, group, mod, f"{prefix} - group {j} - is_unimodular")

        unimodular_bools.append(is_unimodular)
        targets.append(target)

    all_targets_different = are_all_diferent_csp(
        model, targets, f"{prefix} - all_targets_different")

    all_bools = unimodular_bools + [all_targets_different]
    is_modular = are_all_true_csp(
        model, all_bools, f"{prefix} - is_modular_bool")

    return is_modular


def is_entropic_line_csp(model: cp_model.CpModel, x: list[IntVar],
                         entropic_groups: list[VarList], prefix: str) -> IntVar:
    """
    Encodes the entropic line constraint onto a boolean

    Along entropic lines, each segment of N cells must contain one value of each entropic group

    For example, each segment of three cells must contain one low digit (1,2,3), one medium digit (4,5,6) and
    one high digit (7,8,9). Digits may repeat along these lines if allowed by other rules.
    """
    n = len(x)
    seq_size = len(entropic_groups)
    num_groups = min(seq_size, n)
    prefix = f"{prefix} - is_entropic_line_csp"
    is_entropic = model.NewBoolVar(f"{prefix} - is_entropic_bool")

    all_group_bools: list[list[IntVar]] = []
    for j in range(num_groups):
        group = x[j::seq_size]
        m = len(group)

        bools = [model.NewBoolVar(
            f"{prefix} - group_{j} belongs_to_same_set_{k}") for k in range(seq_size)]
        counts: list[IntVar] = []
        all_group_bools.append(bools)

        for k in range(seq_size):
            entropic_set = entropic_groups[k]
            count = count_in_set(model, group, entropic_set,
                                 f"{prefix} - group_{j} set_{k} count")
            counts.append(count)
            model.Add(count == m).OnlyEnforceIf(bools[k])
            model.Add(count != m).OnlyEnforceIf(bools[k].Not())

    bs = [model.NewBoolVar(f"{prefix} - group_{j} same_set_bool")
          for j in range(num_groups)]
    for j in range(num_groups):
        literals = all_group_bools[j]
        model.Add(sum(literals) == 1).OnlyEnforceIf(bs[j])
        model.Add(sum(literals) != 1).OnlyEnforceIf(bs[j].Not())

    cs = [model.NewBoolVar(f"{prefix} - at_most_one_group_in_set_{k}")
          for k in range(seq_size)]
    for k in range(seq_size):
        literals = [_bools[k] for _bools in all_group_bools]
        model.Add(sum(literals) <= 1).OnlyEnforceIf(cs[k])
        model.Add(sum(literals) > 1).OnlyEnforceIf(cs[k].Not())

    bcs = bs + cs
    model.AddBoolAnd(bcs).OnlyEnforceIf(is_entropic)
    model.AddBoolOr([bool_var.Not() for bool_var in bcs]
                    ).OnlyEnforceIf(is_entropic.Not())

    return is_entropic


def at_least_n_in_each_group_csp(model: cp_model.CpModel, x: list[IntVar],
                                 groups: list[VarList], n: int | IntVar, prefix: str):
    """
        For each set in groups, the list of variables x must have at least n elements in that set:
            len(intersection(x, group)) >= n for group in groups
    """

    prefix = f"{prefix} - at_least_n_in_each_group_csp"
    for i, group in enumerate(groups):
        count = count_in_set(model, x, group, f"{prefix} - group_{i}")
        model.Add(count >= n)


def count_unique_values(model: cp_model.CpModel, x: VarList, prefix: str) -> IntVar:
    """
    Returns an int var equal to the number of unique values in x:
        count = len(set(x))
    """
    prefix = f"{prefix} - count_unique_values"
    n = len(x)
    count = model.NewIntVar(0, n, f"{prefix} - count")

    bs: list[IntVar] = []
    for i, var in enumerate(x):
        left_side = x[:i]
        b = is_not_member_of(model, left_side, var, prefix)
        bs.append(b)

    model.Add(sum(bs) == count)
    return count


def count_transitions_csp(model: cp_model.CpModel, x: list[IntVar], prefix: str) -> IntVar:
    """
    Retuns an int var equal to the number of transitions to different values along x:
        count = sum(x1 != x2 for x1, x2 in zip(x, x[1:]))
    """

    n = len(x)
    prefix = f"{prefix} - count_transitions_csp"
    count = model.NewIntVar(0, n, f"{prefix} - count")

    ts: list[IntVar] = []
    for i, (x1, x2) in enumerate(zip(x, x[1:])):
        t = model.NewBoolVar(f"{prefix} - t_{i}")
        model.Add(x1 != x2).OnlyEnforceIf(t)
        model.Add(x1 == x2).OnlyEnforceIf(t.Not())
        ts.append(t)

    model.Add(count == sum(ts))
    return count


def find_first_mod_target(model: cp_model.CpModel, variables: list[IntVar],
                          mod: int, target: int | IntVar) -> list[IntVar]:
    """ Returns an array of BoolVar, where at most 1 of them is 1 and the others are zero.
    The BoolVar that is equal to 1 corresponds to the first var in variables that satisfies the condition:
        var % mod == target
    variables[n] % mod == target => first_bools[n] == 1

    Args:
        model (cp_model.CpModel): 
        variables (list[IntVar]): 
        mod (int | IntVar): 
        target (int | IntVar): 

    Returns:
        list[IntVar]: 
    """

    prefix = f"find_first_mod_target"
    # bool == 1 if var % mod == target, else bool == 0 (var % mod != target)
    bools = [model.NewBoolVar(f"{prefix} - mod_bool_{i}")
             for i, _ in enumerate(variables)]
    for i, var in enumerate(variables):
        target_var = model.NewIntVar(-mod, mod, f"{prefix} - target-{i}")
        model.AddModuloEquality(target_var, var, mod)
        model.Add(target_var == target).OnlyEnforceIf(bools[i])
        model.Add(target_var != target).OnlyEnforceIf(bools[i].Not())

    first_bools = [model.NewBoolVar(
        f"{prefix} - first_bool_{i}") for i, _ in enumerate(variables)]
    for i, _bool in enumerate(bools):
        left_side = get_left_side(bools, i)
        count_mod_left = count_vars(
            model, left_side, 1, f"{prefix} - count_mod_left_{i}")

        any_to_the_left_bool = reif2(model, count_mod_left == 0, count_mod_left != 0,
                                     f"{prefix} - any_to_the_left_bool")

        is_first_bool = are_all_true_csp(
            model, [any_to_the_left_bool, _bool], f"{prefix} - is_first_bool_{i}")

        model.Add(first_bools[i] == 1).OnlyEnforceIf(is_first_bool)
        model.Add(first_bools[i] == 0).OnlyEnforceIf(is_first_bool.Not())

    return first_bools


def count_larger_or_equal_than_x(model: cp_model.CpModel, variables: list[IntVar],
                                 x: int | IntVar, prefix: str) -> IntVar:
    """
    Counts the number of variables larger or equal to x:
        count = sum(var >= x for var in variables)
    """
    n = len(variables)
    b = [model.NewBoolVar(f"{prefix} - count_larger_or_equal_than_x: bool-{i}") for
         i, _ in enumerate(variables)]
    count = model.NewIntVar(
        0, n, f"{prefix} - count_larger_or_equal_than_x: count")
    for i in range(n):
        model.Add((variables[i] >= x)).OnlyEnforceIf(b[i])
        model.Add((variables[i] < x)).OnlyEnforceIf(b[i].Not())
    model.Add(count == sum(b))
    return count


def rising_streak_csp(model: cp_model.CpModel, variables: list[IntVar], min_streak: int | IntVar):
    """
    A number outside the grid indicates there is a streak of AT LEAST that many increasing, consecutive digits in the
    row or column in that direction (e.g. a number above the grid indicates a downward streak in that column).

    For instance, the row '214678935' has a maximal streak of 4 digits to the right (6789)
    and 2 digits to the left (21).
    """
    n = len(variables)
    prefix = f"rising_streak_csp"
    streak_counts = [model.NewIntVar(
        1, n, f'{prefix} - count_{i}') for i in range(n)]

    model.Add(streak_counts[0] == 1)
    for i, count in enumerate(streak_counts[1:], 1):
        is_consecutive = model.NewBoolVar(f"consecutive-{i}")

        model.Add(variables[i] - variables[i - 1] ==
                  1).OnlyEnforceIf(is_consecutive)
        model.Add(variables[i] - variables[i - 1] !=
                  1).OnlyEnforceIf(is_consecutive.Not())

        model.Add(count == 1).OnlyEnforceIf(is_consecutive.Not())
        model.Add(count == streak_counts[i - 1] +
                  1).OnlyEnforceIf(is_consecutive)

    count = count_larger_or_equal_than_x(
        model, streak_counts, min_streak, prefix)
    model.Add(count >= 1)


def count_uninterrupted_csp(model: cp_model.CpModel, variables: list[IntVar], target: int | IntVar) -> IntVar:
    """
    Returns the count the number of uninterrupted occurrences of target in the variables list,
    from the start ot the list.
    For example if target = 6 and variables = [6,6,6,3,2,6], then count = 3
    """

    n = len(variables)
    prefix = "count_uninterrupted_csp"
    count = model.NewIntVar(0, n, f"{prefix} - count")

    if n == 0:
        return count

    bools: list[IntVar] = []
    for i, _ in enumerate(variables):
        sub_list = variables[:i + 1]
        count_intermediate = count_vars(
            model, sub_list, target, f"{prefix} - count_intermediate-{i}")
        b = model.NewBoolVar(f"{prefix} - b-{i}")
        model.Add(count_intermediate == len(sub_list)).OnlyEnforceIf(b)
        model.Add(count_intermediate != len(sub_list)).OnlyEnforceIf(b.Not())
        bools.append(b)

    model.Add(sum(bools) == count)
    return count


def count_uninterrupted_left_right_csp(model: cp_model.CpModel, variables: list[IntVar],
                                       idx: int, target: int | IntVar):
    """
    Given an array of variables, counts the uninterrupted occurrences of target on the left and right side of idx.
    For example given the array [7,8,6,6,6,3,6,6,4], with the target of 6 and idx = 5, it returns a count of 3 + 2 = 5
    (3 uninterrupted 6's on the left side and 2 uninterrupted 6's on the right side)
    """
    n = len(variables)
    count = model.NewIntVar(0, n, f"count_uninterrupted_left_right: count")
    if idx < 0 or idx >= n:
        model.Add(count == 0)
        return count

    left_side = get_left_side(variables, idx)
    left_side.reverse()
    right_side = get_right_side(variables, idx)

    count_uninterrupted_left = count_uninterrupted_csp(
        model, left_side, target)
    count_uninterrupted_right = count_uninterrupted_csp(
        model, right_side, target)

    model.Add(count == count_uninterrupted_left + count_uninterrupted_right)
    return count


def same_remainder_csp(model: cp_model.CpModel, var1: IntVar, var2: IntVar, mod: int, prefix: str) -> IntVar:
    """
    Returns a bool var indicating if var1 and var2 have the same remainder when divided by mod:
        bool_var = var1 % mod == var2 % mod
    """
    prefix = f"{prefix} - same_remainder_csp"

    var1_remainder = model.NewIntVar(
        0, mod - 1, f"{prefix} - remainder1 = var1 % {mod}")
    var2_remainder = model.NewIntVar(
        0, mod - 1, f"{prefix} - remainder2 = var2 % {mod}")
    same_remainder_bool = model.NewBoolVar(f"{prefix} - same_remainder_bool")

    model.AddModuloEquality(var1_remainder, var1, mod)
    model.AddModuloEquality(var2_remainder, var2, mod)
    model.Add(var1_remainder == var2_remainder).OnlyEnforceIf(
        same_remainder_bool)
    model.Add(var1_remainder != var2_remainder).OnlyEnforceIf(
        same_remainder_bool.Not())

    return same_remainder_bool


def is_even_csp(model: cp_model.CpModel, var1: IntVar, prefix: str) -> IntVar:
    """
    Returns a bool var indicating ir var1 is even
    """
    prefix = f"{prefix} - is_even_csp"
    remainder = model.NewIntVar(-1, 1, f"{prefix} - remainder")
    model.AddModuloEquality(remainder, var1, 2)
    is_even_bool = model.NewBoolVar(f"{prefix} - is_even_bool")
    model.Add(remainder == 0).OnlyEnforceIf(is_even_bool)
    model.Add(remainder != 0).OnlyEnforceIf(is_even_bool.Not())
    return is_even_bool


def is_odd_csp(model: cp_model.CpModel, var1: IntVar, prefix: str) -> IntVar:
    """
    Returns a bool var indicating ir var1 is odd
    """
    prefix = f"{prefix} - is_odd_csp"
    remainder = model.NewIntVar(-1, 1, f"{prefix} - remainder")
    model.AddModuloEquality(remainder, var1, 2)
    is_odd_bool = model.NewBoolVar(f"{prefix} - is_odd_bool")
    model.Add(remainder != 0).OnlyEnforceIf(is_odd_bool)
    model.Add(remainder == 0).OnlyEnforceIf(is_odd_bool.Not())
    return is_odd_bool


def segment_by_transitions_csp(model: cp_model.CpModel, variables: list[IntVar], prefix: str) -> list[IntVar]:
    """
    Given a list of variables, enumerates each segment of the list each time it transitions to a different value:
    For example:
        [4, 4, 1, 1, 1, 2, 6, 6, 8] -> [0, 0, 1, 1, 1, 2, 3, 3, 4]
        [3, 3, 1, 4, 4, 2, 2, 1, 1] -> [0, 0, 1, 2, 2, 3, 3, 4, 4]
    """

    prefix = f"{prefix} - segment_by_transitions_csp"
    n = len(variables)
    segments = [model.NewIntVar(
        0, n - 1, f"{prefix} - {var.Name()} - segment") for var in variables]
    model.Add(segments[0] == 0)
    for i in range(1, n):
        is_different = model.NewBoolVar(
            f"{prefix} - is_different - {variables[i - 1].Name()}, {variables[i].Name()}")
        model.Add(variables[i] != variables[i - 1]).OnlyEnforceIf(is_different)
        model.Add(variables[i] == variables[i - 1]
                  ).OnlyEnforceIf(is_different.Not())

        model.Add(segments[i] == segments[i - 1]
                  ).OnlyEnforceIf(is_different.Not())
        model.Add(segments[i] == segments[i - 1] +
                  1).OnlyEnforceIf(is_different)

    return segments


def region_sum_with_unknown_regions_csp(model: cp_model.CpModel, variables: list[IntVar],
                                        regions: list[IntVar], prefix: str):
    """
    """

    prefix = f"{prefix} - region_sum_with_unknown_regions_csp"

    assert len(variables) == len(regions)

    n = len(variables)
    # lb = min(min(var.Proto().domain) for var in variables)
    ub = max(max(var.Proto().domain) for var in variables)

    segments = segment_by_transitions_csp(model, regions, prefix)
    sum_var = model.NewIntVar(0, ub * n, f"{prefix} - sum_var")

    for seg_i in range(n):
        bools = [model.NewBoolVar(f"{prefix} - bool_region_segment_{seg_i} - {region_var.Name()}") for region_var in
                 regions]
        for j in range(n):
            model.Add(segments[j] == seg_i).OnlyEnforceIf(bools[j])
            model.Add(segments[j] != seg_i).OnlyEnforceIf(bools[j].Not())

        bool_has_segment = model.NewBoolVar(
            f"{prefix} - bool_has_segment_{seg_i}")
        model.Add(sum(bools) == 0).OnlyEnforceIf(bool_has_segment.Not())
        model.Add(sum(bools) > 0).OnlyEnforceIf(bool_has_segment)

        segment_sum = scalar_product_csp(
            model, variables, bools, f"{prefix} - segment_{seg_i} - sum")
        model.Add(sum_var == segment_sum).OnlyEnforceIf(bool_has_segment)

    return sum_var


def is_radar_csp(model: cp_model.CpModel, var: IntVar, row_vars: list[IntVar], col_vars: list[IntVar],
                 target: int | IntVar, prefix: str) -> IntVar:
    """
    Radars are variables that have a value indicating the distance to the closest TARGET on their row or column.
    """
    prefix = f"{prefix} - is_radar_csp"
    is_radar = model.NewBoolVar(f"{prefix} - is_radar")
    row_idx = row_vars.index(var)
    col_idx = col_vars.index(var)
    in_row = row_idx != -1
    in_col = col_idx != -1
    max_len = max(len(row_vars), len(col_vars))

    if not in_row and not in_col:
        model.Add(is_radar == 0)
        return is_radar

    elif in_row and not in_col:
        row_dist = distance_to_target_csp(model, row_idx, target, row_vars)
        min_dist = row_dist

    elif not in_row and in_col:
        col_dist = distance_to_target_csp(model, col_idx, target, col_vars)
        min_dist = col_dist

    else:
        row_dist = distance_to_target_csp(model, row_idx, target, row_vars)
        col_dist = distance_to_target_csp(model, col_idx, target, col_vars)
        min_dist = model.NewIntVar(0, max_len, f"{prefix} - min_dist")
        model.AddMinEquality(min_dist, [row_dist, col_dist])

    model.Add(var == min_dist).OnlyEnforceIf(is_radar)
    model.Add(var != min_dist).OnlyEnforceIf(is_radar.Not())
    return is_radar


def expand(adjacency_dict: AdjacencyDict, cells: Iterable[tuple[int, int]]):
    """Given a region of visited cells, expands the region with the new cells that can be visited,
    from the region

    Args:
        adjacency_dict (AdjacencyDict): 
        cells (Iterable[tuple[int, int]]): 

    Returns:
        _type_: 
    """
    cells2 = set(cells)
    for c in cells:
        cells2 |= adjacency_dict[c]
    return cells2


def only_first_of_bools(model: cp_model.CpModel, variables: list[IntVar], prefix: str):
    prefix = f"{prefix} - only_first_of_bools"
    bools = [model.NewBoolVar(f"{prefix} - bool_{i}")
             for i, _ in enumerate(variables)]
    for i, var in enumerate(variables):
        left_side = get_left_side(bools, i)
        if len(left_side):
            bool_var = are_any_true_csp(
                model, left_side, f"{prefix} - any_to_the_left_{i}")
            model.Add(bools[i] == 0).OnlyEnforceIf(bool_var)
            model.Add(bools[i] == var).OnlyEnforceIf(bool_var.Not())
        else:
            model.Add(bools[i] == var)
    return bools


def index_of_first_bools_csp(model: cp_model.CpModel, variables: list[IntVar]) -> IntVar:
    """
    Returns a var with the index of the first true bool in variables. If all variables are false then idx = -1
    Variables is a list of bool variables.
    """
    n = len(variables)
    prefix = f"index_of_first_bools_csp"
    idx_var = model.NewIntVar(-1, n - 1, f"{prefix} - index")
    if n == 0:
        model.Add(idx_var == -1)
        return idx_var

    bools = only_first_of_bools(model, variables, f"{prefix}")
    for i, var in enumerate(bools):
        model.Add(idx_var == i).OnlyEnforceIf(var)

    no_target_bool = model.NewBoolVar(f"{prefix} - no_target")
    model.AddBoolOr(bools).OnlyEnforceIf(no_target_bool.Not())
    model.AddBoolAnd([x.Not() for x in bools]).OnlyEnforceIf(no_target_bool)
    model.Add(idx_var == -1).OnlyEnforceIf(no_target_bool)

    return idx_var


def index_of_first_target_csp(model: cp_model.CpModel, variables: list[IntVar], target: int | IntVar) -> IntVar:
    """
    Returns a var = variables.index(target)
    """
    n = len(variables)
    prefix = f"index_of_first_target_csp"
    if n == 0:
        idx_var = model.NewIntVar(-1, n - 1, f"{prefix} - index")
        model.Add(idx_var == -1)
        return idx_var

    match_bools = [model.NewBoolVar(f"{prefix} - bools_{i}")
                   for i, _ in enumerate(variables)]
    for i, var in enumerate(variables):
        bool_var = match_bools[i]
        model.Add(var == target).OnlyEnforceIf(bool_var)
        model.Add(var != target).OnlyEnforceIf(bool_var.Not())

    idx_var = index_of_first_bools_csp(model, match_bools)
    return idx_var


def between_line_csp(model: cp_model.CpModel, variables: VarList, prefix: str):
    end1 = variables[0]
    end2 = variables[-1]
    middle_vars = variables[1:-1]

    b = model.NewBoolVar(f'{prefix} - bool')
    # b == True => e1_var < e2_var
    # b == False => e1_var > e2_var
    for middle_var in middle_vars:
        model.Add(end1 < middle_var).OnlyEnforceIf(b)
        model.Add(middle_var < end2).OnlyEnforceIf(b)
        model.Add(end2 < middle_var).OnlyEnforceIf(b.Not())
        model.Add(middle_var < end1).OnlyEnforceIf(b.Not())


# http://kmkeen.com/sat-flood-fill/
def floodfill(model: cp_model.CpModel, adjacency_dict: dict[tuple[int, int], set[tuple[int, int]]],
              region_max_size: int, seed: list[tuple[int, int]] | None = None):
    # volume: set[tuple[int, int, int]] = set()

    exact: bool = False
    # (r, c, depth)
    volume_vars_dict: dict[tuple[int, int, int], IntVar] = dict()
    base = set(adjacency_dict.keys())
    max_size = len(base)
    prefix = f"floodfill"

    summary_vars_dict: dict[tuple[int, int], IntVar] = {}
    for r, c in base:
        summary_vars_dict[(r, c)] = model.NewBoolVar(
            f"{prefix} - summary_var ({r}, {c})")

    size_var = model.NewIntVar(0, max_size, f"{prefix} - size_var")
    all_summary_vars = list(summary_vars_dict.values())
    model.Add(sum(all_summary_vars) == size_var)
    enforce_layer_sum_bool = model.NewBoolVar(
        f"{prefix} - enforce_layer_sum_bool")
    model.Add(size_var == 0).OnlyEnforceIf(enforce_layer_sum_bool.Not())
    model.Add(size_var > 0).OnlyEnforceIf(enforce_layer_sum_bool)

    current_layer_cells: set[tuple[int, int]] = base
    if seed is not None:
        current_layer_cells = set(seed)

    for layer in range(region_max_size):
        cells2 = [(row, col, layer) for row, col in current_layer_cells]
        # volume |= set(cells2)
        for r, c, l in cells2:
            volume_vars_dict[(r, c, l)] = model.NewBoolVar(
                f"{prefix} - floodfill_volume: ({r},{c},{l})")

        # at layer 0 only 1 variable can be 1 (the seed)
        # if exact => only one cell can be 1 per layer (and its only 1 at most once per column)
        if layer == 0 or exact:
            layer_vars = [volume_vars_dict[coords] for coords in cells2]
            model.Add(sum(layer_vars) == 1).OnlyEnforceIf(
                enforce_layer_sum_bool)

        # growth rules
        prev_layer = (layer - 1) % region_max_size
        for r, c in current_layer_cells:
            cell_and_adjacent = expand(adjacency_dict, [(r, c)])
            current_layer_cell_var = volume_vars_dict[(r, c, layer)]
            if layer == 0:
                continue

            if exact:
                cell_and_adjacent.discard((r, c))
                previous_layers = [_l for _l in range(layer)]
                prev_layer_cell_and_adj = set((_r, _c, _l) for (_r, _c), _l
                                              in product(cell_and_adjacent, previous_layers))
            else:
                # if a cell is 1 in the previous layer then it cannot be 1 in the current one
                prev_layer_cell_var = volume_vars_dict.get((r, c, prev_layer))
                if prev_layer_cell_var is not None:
                    model.Add(current_layer_cell_var == 0).OnlyEnforceIf(
                        prev_layer_cell_var)
                prev_layer_cell_and_adj = set(
                    (_r, _c, prev_layer) for _r, _c in cell_and_adjacent)

            prev_layer_cell_and_adj &= set(volume_vars_dict.keys())
            cells3_vars = [volume_vars_dict[coords]
                           for coords in prev_layer_cell_and_adj]

            # if the cell and adjacent in the previous layer are all zero, then the cell in the current layer must
            # be zero also
            model.AddBoolOr(*cells3_vars, current_layer_cell_var.Not())

        current_layer_cells = expand(adjacency_dict, current_layer_cells)

    # wrapping up
    columns: dict[tuple[int, int], set[IntVar]] = dict()
    for (r, c, _l), var in volume_vars_dict.items():
        curr_set = columns.setdefault((r, c), {var})
        curr_set.add(var)
    for (r, c), variables in columns.items():
        # at most 1 per column
        model.Add(sum(variables) <= 1)

        summary_var = summary_vars_dict[(r, c)]
        # at least 1 in column <= summary_var
        model.AddBoolOr(variables).OnlyEnforceIf(summary_var)
        # !summary_var => none in the column (all zero)
        model.AddBoolAnd([var.Not() for var in variables]
                         ).OnlyEnforceIf(summary_var.Not())

    # dead columns (happens if the grid is not fully connected, because the cells cannot expand to the part of
    # the grid that's not connected)
    flat_volume = set((r, c) for r, c, _ in volume_vars_dict.keys())
    dead = base - flat_volume
    for x in dead:
        summary_var = summary_vars_dict[x]
        model.Add(summary_var == 0)

    return summary_vars_dict
