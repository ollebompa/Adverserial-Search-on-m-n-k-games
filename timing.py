from alpha_beta import Game as Game_w_pruning
from minimax import Game as Game_wo_pruning

import numpy as np
import pickle

'''
This file calculates the time results presented in the report
'''


def main_fixed_k():
    k = 2
    for m, n in [(2,2), (2,3), (3,3), (3,4), (4,4)]:
        average_times_wo_pruning = []
        for i in range(10):

            game = Game_wo_pruning(m, n, k, automatic_players = [1,2], manual_players = [], display = False)
            times_wo_pruning = game.play()
            if i == 0:
                average_times_wo_pruning = times_wo_pruning
            else:
                average_times_wo_pruning = np.vstack((average_times_wo_pruning, times_wo_pruning))

        name = f'{m,n,k}wo_pruning_k_fixed.obj'
        file_pi = open(name , 'wb')
        pickle.dump({'game':(m,n,k), 'times':np.mean(average_times_wo_pruning,axis=0)}, file_pi)

        average_times_w_pruning = []
        for i in range(10):

            game = Game_w_pruning(m, n, k, automatic_players = [1,2], manual_players = [], display = False)
            times_w_pruning = game.play()
            if i == 0:
                average_times_w_pruning = times_w_pruning
            else:
                average_times_w_pruning = np.vstack((average_times_w_pruning, times_w_pruning))

        name = f'{m,n,k}w_pruning_k_fixed.obj'
        file_pi = open(name , 'wb')
        pickle.dump({'game':(m,n,k), 'times':np.mean(average_times_w_pruning,axis=0)}, file_pi)


def main_fixed_m_n():
    m = 4
    n = 4
    for k in [2, 3, 4]:
        average_times_wo_pruning = []
        for i in range(10):

            game = Game_wo_pruning(m, n, k, automatic_players = [1,2], manual_players = [], display = False)
            times_wo_pruning = game.play()
            if i == 0:
                average_times_wo_pruning = times_wo_pruning
            else:
                average_times_wo_pruning = np.vstack((average_times_wo_pruning, times_wo_pruning))

        name = f'{m,n,k}wo_pruning_m_n_fixed.obj'
        file_pi = open(name , 'wb')
        pickle.dump({'game':(m,n,k), 'times':np.mean(average_times_wo_pruning,axis=0)}, file_pi)

        average_times_w_pruning = []
        for i in range(10):

            game = Game_w_pruning(m, n, k, automatic_players = [1,2], manual_players = [], display = False)
            times_w_pruning = game.play()
            if i == 0:
                average_times_w_pruning = times_w_pruning
            else:
                average_times_w_pruning = np.vstack((average_times_w_pruning, times_w_pruning))

        name = f'{m,n,k}w_pruning_m_n_fixed.obj'
        file_pi = open(name , 'wb')
        pickle.dump({'game':(m,n,k), 'times':np.mean(average_times_w_pruning,axis=0)}, file_pi)


def main():
    for m, n, k in [(2, 2, 2), (3, 3, 3), (4, 4, 4)]:
        average_times_wo_pruning = []
        for i in range(10):

            game = Game_wo_pruning(m, n, k, automatic_players = [1,2], manual_players = [], display = False)
            times_wo_pruning = game.play()
            if i == 0:
                average_times_wo_pruning = times_wo_pruning
            else:
                average_times_wo_pruning = np.vstack((average_times_wo_pruning, times_wo_pruning))

        name = f'{m,n,k}wo_pruning.obj'
        file_pi = open(name , 'wb')
        pickle.dump({'game':(m,n,k), 'times':np.mean(average_times_wo_pruning,axis=0)}, file_pi)

        average_times_w_pruning = []
        for i in range(10):

            game = Game_w_pruning(m, n, k, automatic_players = [1,2], manual_players = [], display = False)
            times_w_pruning = game.play()
            if i == 0:
                average_times_w_pruning = times_w_pruning
            else:
                average_times_w_pruning = np.vstack((average_times_w_pruning, times_w_pruning))

        name = f'{m,n,k}w_pruning.obj'
        file_pi = open(name , 'wb')
        pickle.dump({'game':(m,n,k), 'times':np.mean(average_times_w_pruning,axis=0)}, file_pi)

if __name__ == '__main__':
    main_fixed_k()
    main_fixed_m_n()
    main()
