from typing import List, Tuple
import random
import numpy as np
import time


UPPER_CASE_OFFSET = 64

class Game(object):
    """
    """

    def __init__(self,
                 m:int,
                 n:int,
                 k:int):
        """
        :param m:
        :param n:
        :param k:
        """
        self.initilize_game(m, n, k)


    def initilize_game(self, m, n, k):
        self.m = m
        self.n = n
        self.k = k

        self.state= (set(), set())

        self.possible_moves =\
                {(i,j) for i in range(1,self.m+1) for j in range(1, self.n+1)}
        self.previous_moves_p1 = set()
        self.previous_moves_p2 = set()
        self.state = (self.previous_moves_p1, self.previous_moves_p2)
        self.directions =\
            (self.horizontal, self.diagonal_R, self.verical, self.diagonal_L)

        self.buffer = ExperienceBuffer()


    def array_to_board_coordinates(self, coordinates):
        board_coordinates = []
        for x, y in coordinates:
            x_board = chr(x + UPPER_CASE_OFFSET)
            y_board = str(y)
            board_coordinates.append(x_board + y_board)
        board_coordinates.sort()
        moves = str()
        for coordinate in board_coordinates:
            moves += coordinate + ', '
        moves = moves[:-2]
        end = str()
        if len(board_coordinates) == 1:
            end = '.'
        else:
            end = '. They are all equally good in this position.'
        start = 'The computer recommends the move(s): '
        return start, moves, end


    def board_to_array_coordinates(self, coordinate):
        x_array = ord(coordinate[0].upper()) - UPPER_CASE_OFFSET
        y_array = int(coordinate[1])
        return(x_array, y_array)


    def play(self):
        plays = 0
        turn = 1
        last_turn = 2
        state = self.state
        game.drawboard(self.state)

        while True:
            state = self.state
            if turn == 1:
                print('Player 1 to move...')
                if plays == 0:
                    action = list(self.actions(state))
                else:
                    start_time = time.time()
                    action = self.max_action(state)
                    end_time = time.time()
                    print(end_time-start_time)
                start, moves, end =\
                        self.array_to_board_coordinates(action)


                print(start + moves + end)
                action = \
                    self.board_to_array_coordinates(input('Input your move: '))
                valid = self.is_valid(self.state, action)
                if valid:
                    self.state = game.resulting_state(state, action, 1)
                    game.drawboard(self.state)
                    turn = 2
                    last_turn = 1
                    plays += 1
                else:
                    print('Invalid move!. Choose an unoccupied cell.')
                    turn = 1

            elif turn == 2:
                print('Player 2 to move...')
                action = self.min_action(state)
                move = self.array_to_board_coordinates([action])[1]
                print(f'The computer makes move: {move}')
                self.state = game.resulting_state(state, action, 2)
                game.drawboard(self.state)
                turn = 1
                last_turn = 2
                plays += 1

            terminal, winning_player = self.is_terminal(self.state, action, last_turn)
            if terminal:
                if winning_player == 1:
                    print('Player 1 WON!')
                elif winning_player == 2:
                    print('Player 2 WON!')
                elif winning_player == 0:
                    print('Its a TIE!')
                break


    def min_action(self, state):
        actions = []
        values = []
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 2)
            value = self.max_value(new_state, action)
            actions.append(action)
            values.append(value)

        return(actions[np.argmin(values)])


    def max_action(self, state):
        actions = []
        values = []
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 1)
            value = self.min_value(new_state, action)
            actions.append(action)
            values.append(value)
        argmax = np.argwhere(values == np.amax(values)).flatten()
        actions = np.array(actions)
        return(actions[argmax])


    def max_value(self, state, last_action, player=2):
        terminal, winning_player = self.is_terminal(state, last_action, player)
        if terminal:
            return(self.utility(winning_player))
        v = -float('inf')
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 1)
            value = self.buffer.lookup(new_state)
            if value == None:
                v = max(v, self.min_value(new_state, action))
                self.buffer.add(state, v)
            else:
                v = max(v, value)
        return v


    def min_value(self, state, last_action, player=1):
        terminal, winning_player = self.is_terminal(state, last_action, player)
        if terminal:
            return(self.utility(winning_player))
        v = float('inf')
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 2)
            value = self.buffer.lookup(new_state)
            if value == None:
                v = min(v, self.max_value(new_state, action))
                self.buffer.add(state, v)
            else:
                v = min(v, value)
        return v


    def actions(self, state):
        return(self.possible_moves - state[0] - state[1])


    def resulting_state(self, state:tuple, action:tuple, player):
        new_state = (state[0].copy(), state[1].copy())
        if player == 1:
            new_state[0].add(action)
            return(new_state[0], new_state[1])
        elif player == 2:
            new_state[1].add(action)
            return(new_state[0], new_state[1])


    def utility(self, winning_player):
        if winning_player == 1:
            return 1
        elif winning_player == 2:
            return -1
        elif winning_player == 0:
            return 0


    def horizontal(self, x, y, step):
        return(x+step, y)

    def diagonal_R(self, x, y, step):
        return(x+step, y+step)

    def verical(self, x, y, step):
        return(x, y+step)

    def diagonal_L(self, x, y, step):
        return(x-step, y+step)


    def is_terminal(self, state, last_action, player):
        terminal = False
        winning_player = None
        previous_moves = state[player - 1]
        x = last_action[0]
        y = last_action[1]

        for direction in self.directions:
            comb_len = 1
            step = 1
            while True:
                if direction(x, y, step) in previous_moves:
                    comb_len += 1
                    step += 1
                else:
                    break

            step = -1
            while True:
                if direction(x, y, step) in previous_moves:
                    comb_len += 1
                    step -= 1
                else:
                    break

            if comb_len >= self.k:
                terminal = True
                winning_player = player
                break

        if not terminal and len(state[0]) + len(state[1]) == self.n*self.m:
            winning_player = 0
            terminal = True

        return terminal, winning_player


    def is_valid(self, state, action):
        x_bound = 1 <= action[0] <= self.m
        y_bound = 1 <= action[1] <= self.n
        not_occupied_p1 = action not in state[0]
        not_occupied_p2 = action not in state[1]

        return(all([x_bound, y_bound, not_occupied_p1, not_occupied_p2]))


    def drawboard(self, state):
        array_board = [[' ' for _ in range(self.m)] for _ in range(self.n)]
        for x, y in state[0]:
            array_board[self.n - y][x - 1] = 'X'

        for x, y in state[1]:
            array_board[self.n - y][x - 1] = 'O'

        board_str = self.get_board_string(array_board)
        print(board_str)


    def get_board_string(self, array_board):
        list_lines = []

        array_first_line =\
                [chr(code + UPPER_CASE_OFFSET) for code in range(1, self.m + 1)]
        first_line =\
                ' ' * (len(str(self.n)) + 3) +\
                (' ' * 3).join(array_first_line) + ' \n'

        for index_line, array_line in enumerate(array_board, 1):
            index_line = self.n + 1 - index_line
            number_spaces_before_line = len(str(self.n)) - len(str(index_line))
            space_before_line = number_spaces_before_line * ' '
            list_lines.append(f'{space_before_line}{index_line} | ' +\
                            ' | '.join(array_line) + f' | {index_line}\n')

        line_dashes = (len(str(self.n)) + 1)*' ' + '-' * 4 * self.m + '-\n'

        board_str = first_line + line_dashes + line_dashes.join(list_lines) +\
                    line_dashes + first_line

        return board_str

class ExperienceBuffer:

    def __init__(self):
        self.buffer = {}

    def add(self, state, value):
        frozen_state = (frozenset(state[0]), frozenset(state[1]))
        if frozenset not in self.buffer:
            self.buffer[frozen_state] = value
        else:
            pass

    def lookup(self, state):
        frozen_state = (frozenset(state[0]), frozenset(state[1]))
        if frozen_state in self.buffer:
            return(self.buffer[frozen_state])
        else:
            return None


if __name__ == "__main__":
    game = Game(5, 5, 5)
    # state = game.resulting_state(game.state, (1,1), 1)
    # game.drawboard(state)
    # print(game.is_terminal(state, (1,1), 1))
    game.play()
