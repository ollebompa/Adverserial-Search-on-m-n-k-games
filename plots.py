from matplotlib import pyplot as plt
import pickle

import pandas as pd

'''
This file calculates the results calculated in timing.py
'''

def times():
    times_dict = {}
    times_wo_pruning = []
    times_w_pruning = []
    for i in [2,3,4]:
        with open(f"{i, i, i}wo_pruning.obj", "rb") as input_file:
                times = pickle.load(input_file)
                total_time = times['times'][-1]
                times_wo_pruning.append(total_time)
                times_dict[f'{i, i, i}'] = times['times']
        with open(f"{i, i, i}w_pruning.obj", "rb") as input_file:
                times = pickle.load(input_file)
                total_time = times['times'][-1]
                times_w_pruning.append(total_time)
                times_dict[f'{i, i, i} pruning'] = times['times']




    data = pd.DataFrame.from_dict(times_dict, orient='index').T
    data.to_csv('times_game.csv')

    plt.figure()
    plt.plot([1,2,3],times_wo_pruning)
    plt.plot([1,2,3],times_w_pruning)
    plt.yscale('log')
    plt.show()
#Create a DataFrame



# fixed k
def times_fixed_k():
    times_dict = {}
    times_wo_pruning = []
    times_w_pruning = []
    m_n = []
    k = 2
    for m, n in [(2,2), (2,3), (3,3), (3,4), (4,4)]:
        with open(f"{m, n, k}wo_pruning_k_fixed.obj", "rb") as input_file:
                times = pickle.load(input_file)
                total_time = times['times'][-1]
                times_wo_pruning.append(total_time)
                times_dict[f'{m, n, k}'] = times['times']
                m_n.append(m*n)
        with open(f"{m, n, k}w_pruning_k_fixed.obj", "rb") as input_file:
                times = pickle.load(input_file)
                total_time = times['times'][-1]
                times_w_pruning.append(total_time)
                times_dict[f'{m, n, k} pruning'] = times['times']




    data = pd.DataFrame.from_dict(times_dict, orient='index').T
    print(data)
    data.to_csv('times_k.csv')

    plt.figure(figsize=(4,4))
    plt.plot(m_n,times_wo_pruning, marker = 'o', label='wo. pruning')
    plt.plot(m_n,times_w_pruning, marker = 'o', label='w. pruning')
    plt.yscale('log')
    plt.xlabel('Board-size(mxn)')
    plt.ylabel('Time(s) (log-scale)')
    plt.legend()
    plt.savefig('times_fixed_k.pdf', bbox_inches='tight')
    plt.show()


def times_fixed_m_n():
    times_dict = {}
    times_wo_pruning = []
    times_w_pruning = []
    k_list = []
    m = 4
    n = 4
    for k in [2, 3, 4]:
        with open(f"{m, n, k}wo_pruning_m_n_fixed.obj", "rb") as input_file:
                times = pickle.load(input_file)
                total_time = times['times'][-1]
                times_wo_pruning.append(total_time)
                times_dict[f'{m, n, k}'] = times['times']
                k_list.append(k)
        with open(f"{m, n, k}w_pruning_m_n_fixed.obj", "rb") as input_file:
                times = pickle.load(input_file)
                total_time = times['times'][-1]
                times_w_pruning.append(total_time)
                times_dict[f'{m, n, k} pruning'] = times['times']




    data = pd.DataFrame.from_dict(times_dict, orient='index').T
    print(data)
    data.to_csv('times_m_n.csv')

    plt.figure(figsize=(4,4))
    plt.plot(k_list,times_wo_pruning, marker = 'o', label='wo. pruning')
    plt.plot(k_list,times_w_pruning, marker = 'o', label='w. pruning')
    plt.yscale('log')
    plt.xlabel('k')
    plt.ylabel('Time(s) (log-scale)')
    plt.legend()
    plt.xticks([2, 3, 4])
    plt.savefig('times_fixed_m_n.pdf', bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    times_fixed_m_n()
