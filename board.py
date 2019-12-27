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
                 k:int,
                 automatic_players:List = [1, 2],
                 manual_players:List = [1],
                 display:bool = True
                 ):
        """
        :param m:
        :param n:
        :param k:
        """
        self.initilize_game(m, n, k, automatic_players, manual_players, display)


    def initilize_game(self,
                          m,
                          n,
                          k,
                          automatic_players,
                          manual_players,
                          display):
        self.m = m
        self.n = n
        self.k = k

        self.automatic_players = automatic_players
        self.manual_players = manual_players
        self.display = display

        self.state= (set(), set())
        self.possible_moves =\
                {(i,j) for i in range(1,self.m+1) for j in range(1, self.n+1)}
        self.previous_moves_p1 = set()
        self.previous_moves_p2 = set()
        self.state = (self.previous_moves_p1, self.previous_moves_p2)
        self.directions =\
            (self.horizontal, self.diagonal_R, self.verical, self.diagonal_L)

        self.buffer = ExperienceBuffer()

        self.action_values = {}


    def play(self):
        player = 1
        terminal = False
        winning_player = None

        message_manual = 'The computer recommends the move(s): '
        message_automatic = 'The computer makes the move: '
        message_invalid = 'Invalid move!. That cell is either occupied or out of bounds.'

        while True:
            state = self.state
            if self.display:
                game.drawboard(self.state)

            if terminal:
                if winning_player == 1:
                    print('Player 1 WON!')
                elif winning_player == 2:
                    print('Player 2 WON!')
                elif winning_player == 0:
                    print('Its a TIE!')
                break

            print(f'Player {player} to move...')

            if player in self.automatic_players and player in self.manual_players:
                s = time.time()
                actions = self.minimax_action(state, player)
                s2 = time.time()
                print(s2-s)
                board_coordinates = self.array_to_board_coordinates(actions)
                message = message_manual + board_coordinates
                print(message)
                board_coordinates = input('Input your move: ')
                action = self.board_to_array_coordinates(board_coordinates)

            elif player in self.automatic_players:
                action = self.minimax_action(state, player)[0]
                board_coordinates = self.array_to_board_coordinates([action])
                message = message_automatic + board_coordinates
                print(message)

            elif player in self.manual_players:
                board_coordinates = input('Input your move: ')
                action = self.board_to_array_coordinates(board_coordinates)

            if self.is_valid(self.state, action):
                self.state = game.resulting_state(state, action, player)
                terminal, winning_player = self.is_terminal(self.state, action, player)
                self.buffer.clear()
                player = player%2 + 1
            else:
                print(message_invalid)


    def minimax_action(self, state, player):
        alpha = -float('inf')
        beta = float('inf')
        optimal_actions = []
        self.action_values.clear()
        if player == 1:
            optimal_value = self.max_value(state, alpha, beta, last_action = None, depth = 0)
        elif player == 2:
            optimal_value = self.min_value(state, alpha, beta, last_action = None, depth = 0)
        for action, value in self.action_values.items():
            if value[0] == optimal_value and not value[1]:
                optimal_actions.append(action)
        return optimal_actions


    def max_value(self, state, alpha, beta, last_action, depth, player=2):
        terminal, winning_player = self.is_terminal(state, last_action, player)
        if terminal:
            return(self.utility(winning_player))
        v = -float('inf')
        v_buffer, cut_flag = self.buffer.lookup(state)
        if v_buffer == None:
            pass
        elif v_buffer != None and not cut_flag:
            return v_buffer
        elif v_buffer != None and cut_flag:
            if v_buffer >= beta:
                return v_buffer
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 1)
            v_new = self.min_value(new_state, alpha, beta, action, depth + 1)

            v = max(v, v_new)

            if depth == 0:
                if action in self.action_values:
                    self.action_values[action][0] = v_new
                else:
                    self.action_values[action] = [v_new, False]
            if v >= beta:
                self.buffer.add(state, v, True)
                if depth == 1:
                    self.action_values[last_action] = [None, True]
                return v
            alpha = max(alpha, v)
        self.buffer.add(state, v, False)
        return v


    def min_value(self, state, alpha, beta, last_action, depth, player=1):
        cut = False
        terminal, winning_player = self.is_terminal(state, last_action, player)
        if terminal:
            return(self.utility(winning_player))
        v = float('inf')
        v_buffer, cut_flag = self.buffer.lookup(state)
        if v_buffer == None:
            pass
        elif v_buffer != None and not cut_flag:
            return v_buffer
        elif v_buffer != None and cut_flag:
            if v_buffer <= alpha:
                return v_buffer
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 2)
            v_new = self.max_value(new_state, alpha, beta, action, depth + 1)
            v = min(v, v_new)
            if depth == 0:
                if action in self.action_values:
                    self.action_values[action][0] = v_new
                else:
                    self.action_values[action] = [v_new, False]
            if v <= alpha:
                self.buffer.add(state, v, True)
                if depth == 1:
                    self.action_values[last_action] = [None, True]
                return v
            beta = min(beta, v)
        self.buffer.add(state, v, False)
        return v


    def actions(self, state):
        column_priority = [0 for _ in range(self.m)]
        row_priority = [0 for _ in range(self.n)]
        dia_priority = [0 for _ in range(2)]
        for move in state[0]:
            column_priority[move[0] - 1] += 1
            row_priority[move[1] - 1] += 1
            if move[0] == move[1]:
                dia_priority[0] += 1
            if move[0] + self.m -1 == move[1]:
                dia_priority[1] += 1
        for move in state[1]:
            column_priority[move[0] - 1] += 1
            row_priority[move[1] - 1] += 1
            if move[0] == move[1]:
                dia_priority[0] += 1
            elif move[0] + self.m -1 == move[1]:
                dia_priority[1] += 1
        moves = list(self.possible_moves - state[0] - state[1])
        move_priority = []
        for move in moves:
            prioity = column_priority[move[0] - 1] + row_priority[move[1] - 1]
            if move[0] == move[1]:
                prioity+= dia_priority[0]
            elif move[0] + self.m -1 == move[1]:
                prioity += dia_priority[1]
            move_priority.append(prioity)
        prioritised_moves = [move for _, move in sorted(zip(move_priority, moves), reverse=True)]
        return(prioritised_moves)
        # return(self.possible_moves - state[0] - state[1])


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
        if last_action == None:
            return terminal, winning_player
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


    def array_to_board_coordinates(self, coordinates):
        board_coordinates = []
        for x, y in coordinates:
            x_board = chr(x + UPPER_CASE_OFFSET)
            y_board = str(y)
            board_coordinates.append(x_board + y_board)
        board_coordinates.sort()
        coordinate_string = str()
        for coordinate in board_coordinates:
            coordinate_string += coordinate + ', '
        return coordinate_string[:-2] + '.'


    def board_to_array_coordinates(self, coordinate):
        x_array = ord(coordinate[0].upper()) - UPPER_CASE_OFFSET
        y_array = int(coordinate[1])
        return(x_array, y_array)


class ExperienceBuffer:

    def __init__(self):
        self.buffer = {}

    def add(self, state, value, cut_flag):
        frozen_state = (frozenset(state[0]), frozenset(state[1]))
        if frozenset not in self.buffer:
            self.buffer[frozen_state] = [value, cut_flag]
        else:
            pass

    def lookup(self, state):
        frozen_state = (frozenset(state[0]), frozenset(state[1]))
        if frozen_state in self.buffer:
            return(self.buffer[frozen_state])
        else:
            return None, False

    def clear(self):
        self.buffer.clear()

if __name__ == "__main__":
    game = Game(4, 4, 4, automatic_players = [1,2], manual_players = [1], display = True)
    game.play()
