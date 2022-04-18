from CSP import Grid


def read_grid_from_file(path) -> Grid:
    file = open(path, "r")
    rows = file.read().splitlines()
    file.close()
    return [list(elem) for elem in rows]


def display_grid(grid: Grid) -> None:
    print()
    for row in grid:
        print("".join(row))


def display_solution(n: int, solution: dict) -> None:
    print()
    rows = []
    for i in range(n):
        rows.append([])
        for j in range(n):
            rows[i].append(solution[(i, j)])
    for row in rows:
        print(row)


def all_equal(lst):
    return not lst or lst.count(lst[0]) == len(lst)


def all_unique(x):
    seen = list()
    return not any(i in seen or seen.append(i) for i in x)

