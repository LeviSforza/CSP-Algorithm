import itertools
from typing import List, Dict
import numpy as np
from CSP import CSP, Constraint, Problem, Grid
from utils import all_equal


def generate_possible(row: List[str]) -> list[str]:
    base_option = ['0'] * int(len(row) / 2) + ['1'] * int(len(row) / 2)
    possible_rows = list(set(list(itertools.permutations(base_option))))
    for i in range(len(row)):
        if row[i] != 'x':
            possible_rows = [x for x in possible_rows if x[i] == row[i]]

    res = possible_rows.copy()

    for pos_row in possible_rows:
        for i in range(2, len(pos_row)):
            if pos_row[i] == pos_row[i - 1] == pos_row[i - 2]:
                if pos_row in res:
                    res.remove(pos_row)
    return res


class BackwardConstraint(Constraint[int, str]):
    def __init__(self, rows: List[int]) -> None:
        super().__init__(rows)
        self.rows: List[int] = rows

    def satisfied(self, assignment: Dict[int, List[str]]) -> bool:
        # check if no column has more than two identical numbers next to each other
        for row_idx in assignment:
            if row_idx-1 in assignment and row_idx-2 in assignment:
                for i in range(len(assignment[row_idx])):
                    if assignment[row_idx][i] == assignment[row_idx-1][i] == assignment[row_idx-2][i]:
                        return False
        return True


class ForwardConstraint(Constraint[int, str]):
    def __init__(self, rows: List[int]) -> None:
        super().__init__(rows)
        self.rows: List[int] = rows

    def satisfied(self, assignment: Dict[int, List[str]]) -> bool:
        # check if no column has more than two identical numbers next to each other
        for row_idx in assignment:
            if row_idx+1 in assignment and row_idx+2 in assignment:
                for i in range(len(assignment[row_idx])):
                    if assignment[row_idx][i] == assignment[row_idx+1][i] == assignment[row_idx+2][i]:
                        return False
        return True


class MiddleConstraint(Constraint[int, str]):
    def __init__(self, rows: List[int]) -> None:
        super().__init__(rows)
        self.rows: List[int] = rows

    def satisfied(self, assignment: Dict[int, List[str]]) -> bool:
        # check if no column has more than two identical numbers next to each other
        for row_idx in assignment:
            if row_idx-1 in assignment and row_idx+1 in assignment:
                for i in range(len(assignment[row_idx])):
                    if assignment[row_idx][i] == assignment[row_idx-1][i] == assignment[row_idx+1][i]:
                        return False
        return True


class ZerosAndOnesConstraint(Constraint[int, str]):
    def __init__(self, rows: List[int]) -> None:
        super().__init__(rows)
        self.rows: List[int] = rows

    def satisfied(self, assignment: Dict[int, List[str]]) -> bool:
        # check if number of zeros equals number of ones
        values = list(assignment.values())
        if len(assignment) == len(values[0]):
            rows = []
            zero_count = [0] * len(assignment[0])
            one_count = [0] * len(assignment[0])
            for row_idx in assignment:
                rows.append(assignment[row_idx])
                for i in range(len(assignment[row_idx])):
                    if assignment[row_idx][i] == '0':
                        zero_count[i] += 1
                    else:
                        one_count[i] += 1
            if not all_equal(zero_count) or not all_equal(one_count):
                return False
        return True


class UniqueConstraint(Constraint[int, str]):
    def __init__(self, rows: List[int]) -> None:
        super().__init__(rows)
        self.rows: List[int] = rows

    def satisfied(self, assignment: Dict[int, List[str]]) -> bool:
        # check if every row is unique
        rows = []
        for row_idx in assignment:
            rows.append(assignment[row_idx])
        if len(set(rows)) != len(rows):
            return False

        # check if every column is unique
        values = list(assignment.values())
        if len(assignment) == len(values[0]):
            numpy_array = np.array(rows)
            transpose = numpy_array.T
            columns = transpose.tolist()
            columns = [tuple(elem) for elem in columns]
            if len(set(columns)) != len(columns):
                return False
        return True


# Base class for all problems
class Binary(Problem):
    # Solutions for problem
    def __init__(self, MRV, LSC) -> None:
        super().__init__()
        self.MRV = MRV
        self.LSC = LSC

    @staticmethod
    def generate_domains(grid: Grid) -> dict[int, list[str]]:
        domains = {}
        for i in range(len(grid)):
            domains[i] = generate_possible(grid[i])
        return domains

    def solve(self, n: int, grid: Grid, to_first_solution: bool, forward_checking: bool) -> None:
        rows: List[int] = list(range(n))
        domains = self.generate_domains(grid)

        csp: CSP[int, str] = CSP(rows, domains)
        csp.add_constraint(UniqueConstraint(rows))
        csp.add_constraint(ZerosAndOnesConstraint(rows))
        csp.add_constraint(MiddleConstraint(rows[1:-1]))
        csp.add_constraint(BackwardConstraint(rows[2:]))
        csp.add_constraint(ForwardConstraint(rows[:-2]))

        if forward_checking:
            csp.forward_checking_search(to_first_solution=to_first_solution, MRV=self.MRV,
                                        LSC=self.LSC)
        else:
            csp.backtracking_search(to_first_solution=to_first_solution, MRV=self.MRV, LSC=self.LSC)

        self.solutions = csp.solutions
        if csp.solutions:
            for solution in csp.solutions:
                print('Visited nodes: ' + str(solution[1]))
                solution_lst = list(solution[0].values())
                solution_grid: Grid = [list(elem) for elem in solution_lst]
                # display_grid(solution_grid)
            # print('Number of solutions: ' + str(len(csp.solutions)))
            print('All visited nodes: ' + str(csp.nodes_visited))
        else:
            print("No solution found!")
