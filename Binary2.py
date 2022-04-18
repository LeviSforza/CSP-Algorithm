import itertools
from typing import List, Dict
from CSP import CSP, Constraint, Problem, Grid
from utils import all_unique


class BinaryConstraint(Constraint[tuple[int, int], int]):
    def __init__(self, left: tuple[int, int], middle: tuple[int, int], right: tuple[int, int]) -> None:
        super().__init__([left, middle, right])
        self.left: tuple[int, int] = left
        self.middle: tuple[int, int] = middle
        self.right: tuple[int, int] = right

    def satisfied(self, assignment: Dict[tuple[int, int], List[int]]) -> bool:
        # check if left == middle == right
        if self.left in assignment and self.middle in assignment and self.right in assignment:
            if assignment[self.left] == assignment[self.middle] == assignment[self.right]:
                return False
        return True


class ZerosEqualsOnesConstraint(Constraint[tuple[int, int], int]):
    def __init__(self, line: List[tuple[int, int]]) -> None:
        super().__init__(line)
        self.line: List[tuple[int, int]] = line

    def satisfied(self, assignment: Dict[tuple[int, int], List[int]]) -> bool:
        # check if number of zeros equals number of ones
        if all(elem in assignment for elem in self.line):
            zero_count, one_count = 0, 0
            for t in self.line:
                if assignment[t] == 0:
                    zero_count += 1
                else:
                    one_count += 1
            if zero_count != one_count:
                return False
        return True


class ColumnConstraint(Constraint[tuple[int, int], int]):
    def __init__(self, fields: List[tuple[int, int]], n: int, columns: List[List[tuple[int, int]]]) -> None:
        super().__init__(fields)
        self.fields: List[tuple[int, int]] = fields
        self.n = n
        self.columns = columns
        self.fields.sort()

    def satisfied(self, assignment: Dict[tuple[int, int], List[int]]) -> bool:
        # check if every column is unique
        keys = assignment.keys()
        lines = []
        for column in self.columns:
            if all(elem in keys for elem in column):
                line = [assignment[x] for x in column]
                lines.append(line)

        if not all_unique(lines):
            return False
        return True


class RowConstraint(Constraint[tuple[int, int], int]):
    def __init__(self, fields: List[tuple[int, int]], n: int, rows: List[List[tuple[int, int]]]) -> None:
        super().__init__(fields)
        self.fields: List[tuple[int, int]] = fields
        self.n = n
        self.rows = rows
        self.fields.sort()

    def satisfied(self, assignment: Dict[tuple[int, int], List[int]]):
        # check if every row is unique
        keys = assignment.keys()
        lines = []
        for row in self.rows:
            if all(elem in keys for elem in row):
                line = [assignment[x] for x in row]
                lines.append(line)
        if not all_unique(lines):
            return False
        return True


def generate_lines(n: int):
    rows, columns = [], []
    for i in range(n):
        row = []
        column = []
        for j in range(n):
            row.append((i, j))
            column.append((j, i))
        rows.append(row)
        columns.append(column)
    return rows, columns


class Binary2(Problem):
    # Solutions for problem
    def __init__(self, MRV, LSC) -> None:
        super().__init__()
        self.MRV = MRV
        self.LSC = LSC

    @staticmethod
    def generate_domains(n: int) -> dict[(int, int), list[int]]:
        domains = {}
        for i in range(n):
            for j in range(n):
                domains[(i, j)] = [0, 1]
        return domains

    @staticmethod
    def find_start_assignment(grid):
        assignment = {}
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] != 'x':
                    assignment[(i, j)] = int(grid[i][j])
        return assignment

    @staticmethod
    def define_binary_constraints(grid: Grid, csp: CSP) -> None:
        for i in range(len(grid)):
            for j in range(len(grid) - 2):
                csp.add_constraint(BinaryConstraint((i, j), (i, j + 1), (i, j + 2)))
        for i in range(len(grid) - 2):
            for j in range(len(grid)):
                csp.add_constraint(BinaryConstraint((i, j), (i + 1, j), (i + 2, j)))
        return

    @staticmethod
    def define__zeros_equals_ones_constraints(grid: Grid, csp: CSP) -> None:
        lines = []
        for i in range(len(grid)):
            line = []
            line2 = []
            for j in range(len(grid)):
                line.append((i, j))
                line2.append((j, i))
            lines.append(line)
            lines.append(line2)
        for line in lines:
            csp.add_constraint(ZerosEqualsOnesConstraint(line))
        return

    def solve(self, n: int, grid: Grid, to_first_solution: bool, forward_checking: bool):
        variables: List[tuple[int, int]] = list(itertools.product(list(range(n)), list(range(n))))
        domains = self.generate_domains(n)
        csp: CSP[tuple[int, int], int] = CSP(variables, domains)

        self.define_binary_constraints(grid, csp)
        self.define__zeros_equals_ones_constraints(grid, csp)

        rows, columns = generate_lines(n)
        csp.add_constraint(RowConstraint(variables, n, rows))
        csp.add_constraint(ColumnConstraint(variables, n, columns))
        start_assignment = self.find_start_assignment(grid)

        if forward_checking:
            csp.forward_checking_search(start_assignment, to_first_solution=to_first_solution, MRV=self.MRV,
                                        LSC=self.LSC)
        else:
            csp.backtracking_search(start_assignment, to_first_solution=to_first_solution, MRV=self.MRV, LSC=self.LSC)

        self.solutions = csp.solutions
        first = 0
        if csp.solutions:
            for solution in csp.solutions:
                print('Visited nodes: ' + str(solution[1]))
                first = solution[1]
                # display_solution(n, solution[0])
            # print('Number of solutions: ' + str(len(csp.solutions)))
            print('All visited nodes: ' + str(csp.nodes_visited))
        else:
            print("No solution found!")
        return n, first, csp.nodes_visited
