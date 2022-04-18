import copy
from typing import Generic, TypeVar, Dict, List, Optional, Any
from abc import ABC, abstractmethod

from Constraint import Constraint

V = TypeVar('V')  # variable type
D = TypeVar('D')  # domain type
Grid = List[List[str]]  # type alias for grids


# Base class for all problems
class Problem(ABC):
    # Solutions for problem
    def __init__(self) -> None:
        self.solutions = {}

    # Must be overridden by subclasses
    @abstractmethod
    def solve(self, n: int, grid: Grid, to_first_solution: bool, forward_checking: bool) -> None:
        ...


class CSP(Generic[V, D]):
    def __init__(self, variables: List[V], domains: Dict[V, List[D]]) -> None:
        self.variables: List[V] = variables  # variables to be constrained
        self.domains: Dict[V, List[D]] = domains  # domain of each variable
        self.domains_copy = copy.deepcopy(domains)
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        self.constr_map_variable: Dict[Constraint[V, D], List[V]] = {}
        self.solutions = []
        self.nodes_visited = 0
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it.")

    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        self.constr_map_variable[constraint] = constraint.variables
        # print(self.constr_map_variable[constraint])
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)

    # Check if the value assignment is consistent by checking all constraints
    # for the given variable against it
    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True

    def backtracking_search(self, assignment=None, to_first_solution=True, MRV=False, LSC=False) -> dict[V, D] | None:
        # assignment is complete if every variable is assigned (our base case)
        if assignment is None:
            assignment = {}
        if len(assignment) == len(self.variables):
            self.solutions.append((assignment, self.nodes_visited))
            return

        # get all variables in the CSP but not in the assignment
        unassigned: List[V] = [v for v in self.variables if v not in assignment]

        if MRV:
            first: V = self.MRV(unassigned)
        else:
            first: V = unassigned[0]

        if LSC:
            values = self.LSC(first, assignment, unassigned)
        else:
            values = self.domains[first]

        for value in values:
            self.nodes_visited += 1
            local_assignment = assignment.copy()
            local_assignment[first] = value
            # if we're still consistent, we recurse (continue)
            if self.consistent(first, local_assignment):
                self.backtracking_search(local_assignment, to_first_solution, MRV, LSC)
                # if we didn't find the result, we will end up backtracking
                if to_first_solution and self.solutions:
                    return
        return

    def forward_checking_search(self, assignment=None, to_first_solution=True, MRV=False, LSC=False) -> dict[V, D] | None:
        if assignment is None:
            assignment = {}
        if len(assignment) == len(self.variables):
            self.solutions.append((assignment, self.nodes_visited))
            return

        unassigned: List[V] = [v for v in self.variables if v not in assignment]
        # print(self.domains)
        if MRV:
            first: V = self.MRV(unassigned)
        else:
            first: V = unassigned[0]

        if LSC:
            values = self.LSC(first, assignment, unassigned)
        else:
            values = self.domains[first]

        for value in values:
            self.nodes_visited += 1
            local_assignment = assignment.copy()
            local_assignment[first] = value

            if self.consistent(first, local_assignment):
                emptyDomainFound = False
                for variable in self.get_unassigned_from_constraints(first, unassigned[1:]):
                    wipe, new_domain = self.forward_check(variable, local_assignment)
                    if wipe:
                        emptyDomainFound = True
                        self.domains = copy.deepcopy(self.domains_copy)
                        break
                    else:
                        self.domains[variable] = new_domain
                if not emptyDomainFound:
                    self.forward_checking_search(local_assignment, to_first_solution, MRV, LSC)
                    if to_first_solution and self.solutions:
                        return
        return

    def get_unassigned_from_constraints(self, curr_variable, unassigned):
        # unnecessary when we have constraints related to all variables
        # implementation possibly needed for other problems
        variables = []
        for constraint in self.constraints[curr_variable]:
            for v in self.constr_map_variable[constraint]:
                if v in unassigned:
                    variables.append(v)
        return list(dict.fromkeys(variables))

    def MRV(self, unassigned):
        best_variable = unassigned[0]
        best_length = len(self.domains[best_variable])
        for var in unassigned:
            curr_length = len(self.domains[var])
            if curr_length < best_length:
                best_variable = var
                best_length = curr_length
        return best_variable

    def LSC(self, variable, assignment, unassigned):
        ordered_domain = {}
        unassigned_const = self.get_unassigned_from_constraints(variable, unassigned)
        # temp_assignment = copy.deepcopy(assignment)
        for value in self.domains[variable]:
            ordered_domain[value] = 0
            # temp_assignment = copy.deepcopy(assignment)
            # temp_assignment[variable] = value
            for var in unassigned_const:
                temp_assignment = copy.deepcopy(assignment)
                temp_assignment[variable] = value
                for dom in self.domains[var]:
                    temp_assignment[var] = dom
                    # print(temp_assignment)
                    if not self.consistent(var, temp_assignment):
                        ordered_domain[value] += 1
        ordered = {k: v for k, v in sorted(ordered_domain.items(), key=lambda item: item[1], reverse=False)}
        # print(ordered)
        return ordered.keys()

    def forward_check(self, variable, assignment):
        values = copy.deepcopy(self.domains_copy[variable])
        res = []
        for value in values:
            temp_assignment = copy.deepcopy(assignment)
            temp_assignment[variable] = value
            if self.consistent(variable, temp_assignment):
                res.append(value)
        # print(res)
        return len(res) == 0, res
