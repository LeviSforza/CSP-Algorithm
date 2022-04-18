import itertools
from typing import List, Dict
from CSP import CSP, Constraint, Problem, Grid


class RowsConstraint(Constraint[tuple[int, int], int]):
    def __init__(self, variables: List[tuple[int, int]]) -> None:
        super().__init__(variables)
        self.variables: List[tuple[int, int]] = variables

    def satisfied(self, assignment: Dict[tuple[int, int], List[int]]) -> bool:
        # print(assignment)
        keys = assignment.keys()
        # if all(elem in keys for elem in self.variables):
        row = []
        for variable in self.variables:
            if variable in keys:
                row.append(assignment[variable])
        if len(row) != len(set(row)):
            return False
        return True


class ColumnsConstraint(Constraint[tuple[int, int], int]):
    def __init__(self, variables: List[tuple[int, int]]) -> None:
        super().__init__(variables)
        self.variables: List[tuple[int, int]] = variables

    def satisfied(self, assignment: Dict[tuple[int, int], List[int]]) -> bool:
        keys = assignment.keys()
        # if all(elem in keys for elem in self.variables):
        column = []
        for variable in self.variables:
            if variable in keys:
                column.append(assignment[variable])
        if len(column) != len(set(column)):
            return False
        return True


class FutoshikiConstraint(Constraint[tuple[int, int], int]):
    def __init__(self, grt_field: tuple[int, int], ls_field: tuple[int, int]) -> None:
        super().__init__([grt_field, ls_field])
        self.grt_field: tuple[int, int] = grt_field
        self.ls_field: tuple[int, int] = ls_field

    def satisfied(self, assignment: Dict[tuple[int, int], List[int]]) -> bool:
        # check if grt_field > ls_field
        if self.grt_field in assignment and self.ls_field in assignment:
            if assignment[self.grt_field] <= assignment[self.ls_field]:
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


# Base class for all problems
class Futoshiki(Problem):
    # Solutions for problem
    def __init__(self, MRV, LSC) -> None:
        super().__init__()
        self.MRV = MRV
        self.LSC = LSC

    def solve(self, n: int, grid: Grid, to_first_solution: bool, forward_checking: bool):
        variables: List[tuple[int, int]] = list(itertools.product(list(range(n)), list(range(n))))
        domains = self.generate_domains(n)
        csp: CSP[tuple[int, int], int] = CSP(variables, domains)

        self.define_futoshiki_constraints(grid, csp)

        rows, columns = generate_lines(n)
        for row in rows:
            csp.add_constraint(RowsConstraint(row))
        for column in columns:
            csp.add_constraint(ColumnsConstraint(column))

        start_assignment = self.find_start_assignment(grid)

        if forward_checking:
            csp.forward_checking_search(start_assignment, to_first_solution=to_first_solution, MRV=self.MRV,
                                        LSC=self.LSC)
        else:
            csp.backtracking_search(start_assignment, to_first_solution=to_first_solution, MRV=self.MRV, LSC=self.LSC)

        first = 0
        if csp.solutions:
            # for solution in csp.solutions:
            #     print('Visited nodes: ' + str(solution[1]))
            first = csp.solutions[0]
            print('Visited nodes: ' + str(first[1]))
            # display_solution(n, first[0])
            # print('Number of solutions: ' + str(len(csp.solutions)))
            print('All visited nodes: ' + str(csp.nodes_visited))
        else:
            print("No solution found!")
        return n, first[1], csp.nodes_visited

    @staticmethod
    def generate_domains(n: int) -> dict[(int, int), list[int]]:
        domains = {}
        for i in range(n):
            for j in range(n):
                domains[(i, j)] = list(range(1, n + 1))
        return domains

    @staticmethod
    def define_futoshiki_constraints(grid: Grid, csp: CSP) -> None:
        cosntr_row, cosntr_col = [], []
        for i in range(len(grid)):
            if (i % 2) == 0:
                cosntr_row.append([])
                for j in range(len(grid[i])):
                    if grid[i][j] == '>' or grid[i][j] == '<' or grid[i][j] == '-':
                        cosntr_row[int(i / 2)].append(grid[i][j])
            else:
                cosntr_col.append([])
                for j in range(len(grid[i])):
                    if grid[i][j] == '>' or grid[i][j] == '<' or grid[i][j] == '-':
                        cosntr_col[int(i / 2)].append(grid[i][j])

        for i in range(len(cosntr_row)):
            for j in range(len(cosntr_row[i])):
                if cosntr_row[i][j] == '>':
                    csp.add_constraint(FutoshikiConstraint((i, j), (i, j + 1)))
                if cosntr_row[i][j] == '<':
                    csp.add_constraint(FutoshikiConstraint((i, j + 1), (i, j)))

        for i in range(len(cosntr_col)):
            for j in range(len(cosntr_col[i])):
                if cosntr_col[i][j] == '>':
                    csp.add_constraint(FutoshikiConstraint((i, j), (i + 1, j)))
                if cosntr_col[i][j] == '<':
                    csp.add_constraint(FutoshikiConstraint((i + 1, j), (i, j)))
        return

    @staticmethod
    def find_start_assignment(grid):
        assignment = {}
        for i in range(len(grid)):
            if (i % 2) == 0:
                for j in range(len(grid[i])):
                    if grid[i][j] != '>' and grid[i][j] != '<' and grid[i][j] != '-' and grid[i][j] != 'x':
                        assignment[(int(i / 2), int(j / 2))] = int(grid[i][j])
        return assignment


# if __name__ == "__main__":
#     f: Futoshiki = Futoshiki()
#     r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_4x4')
#     display_grid(r)
#     f.solve(4, r, False)
#
#     r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_5x5')
#     display_grid(r)
#     f.solve(5, r, True)
#
#     r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_6x6')
#     display_grid(r)
#     f.solve(6, r, True)
