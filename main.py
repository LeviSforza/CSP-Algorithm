import time
import matplotlib.pyplot as plt
from Binary2 import Binary2
from Futoshiki import Futoshiki
from utils import read_grid_from_file

if __name__ == '__main__':
    problem: Futoshiki = Futoshiki(True, True)
    problem_lsc: Futoshiki = Futoshiki(False, True)
    problem_mrv: Futoshiki = Futoshiki(True, False)
    problem_all: Futoshiki = Futoshiki(True, True)
    bt_first, bt_all, fc_first, fc_all, n = [], [], [], [], []
    exec_time_bt, exec_time_fc = [], []
    grids = []

    print('Futoshiki (variable=field)')
    r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_3x3')
    grids.append(r)
    n.append(3)

    r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_4x4')
    grids.append(r)
    n.append(4)

    r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_5x5')
    grids.append(r)
    n.append(5)

    r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_6x6')
    grids.append(r)
    n.append(6)

    r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_7x7')
    grids.append(r)
    n.append(7)

    r = read_grid_from_file('binary-futoshiki_dane_v1.0/futoshiki_8x8')
    grids.append(r)
    n.append(8)

    for i in range(len(grids)):
        print(n[i])
        print('BT')
        start = time.time()
        sol = problem.solve(n[i], grids[i], False, False)
        end = time.time()
        bt_first.append(sol[1])
        bt_all.append(sol[2])
        exec_time_bt.append(end - start)
        print('time bt: ' + str(exec_time_bt[i]))
        print('FC')
        start = time.time()
        sol = problem.solve(n[i], grids[i], False, True)
        end = time.time()
        fc_first.append(sol[1])
        fc_all.append(sol[2])
        exec_time_fc.append(end - start)
        print('time fc: ' + str(exec_time_fc[i]))

    plt.plot(n, bt_first, label='BT_first')
    plt.plot(n, bt_all, label='BT_all')
    plt.plot(n, fc_first, label='FC_first')
    plt.plot(n, fc_all, label='FC_all')
    plt.ylabel('Visited nodes')
    plt.xlabel('Dimensions')
    plt.legend()
    plt.title("Visited nodes")
    plt.show()

    plt.plot(n, exec_time_bt, label='BT')
    plt.plot(n, exec_time_fc, label='FC')
    plt.ylabel('Execution time')
    plt.xlabel('Dimensions')
    plt.legend()
    plt.title("Time duration")
    plt.show()
