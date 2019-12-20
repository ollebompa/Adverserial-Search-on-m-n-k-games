from typing import List, Tuple
import random
import numpy as np


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
        self.previous_moves = set()
        self.state = (self.previous_moves_p1, self.previous_moves_p2)


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
        x_array = ord(coordinate[0]) - UPPER_CASE_OFFSET
        y_array = int(coordinate[1])
        return(x_array, y_array)


    def play(self):
        turn = 1
        state = self.state
        game.drawboard(self.state)

        while True:
            terminal, winning_player = self.is_terminal(self.state)
            if terminal:
                if winning_player == 1:
                    print('Player 1 WON!')
                elif winning_player == 2:
                    print('Player 2 WON!')
                elif winning_player == 0:
                    print('Its a TIE!')
                break

            state = self.state
            if turn == 1:
                print('Player 1 to move...')
                start, moves, end =\
                        self.array_to_board_coordinates(self.max_action(state))
                print(start + moves + end)
                action = \
                    self.board_to_array_coordinates(input('Input your move: '))
                valid = self.is_valid(self.state, action)
                if valid:
                    self.state = game.resulting_state(state, action, 1)
                    game.drawboard(self.state)
                    turn = 2
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


    def min_action(self, state):
        actions = []
        values = []
        for action in self.actions(state):
            value = self.max_value(self.resulting_state(state, action, 2))
            actions.append(action)
            values.append(value)

        return(actions[np.argmin(values)])


    def max_action(self, state):
        actions = []
        values = []
        for action in self.actions(state):
            value = self.min_value(self.resulting_state(state, action, 1))
            actions.append(action)
            values.append(value)
        argmax = np.argwhere(values == np.amax(values)).flatten()
        actions = np.array(actions)
        return(actions[argmax])



    def max_value(self, state):
        terminal, winning_player = self.is_terminal(state)
        if terminal:
            return(self.utility(winning_player))
        v = -float('inf')
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 1)
            v = max(v, self.min_value(new_state))
        return v


    def min_value(self, state):
        terminal, winning_player = self.is_terminal(state)
        if terminal:
            return(self.utility(winning_player))
        v = float('inf')
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 2)
            v = min(v, self.max_value(new_state))
        return v


    def player(self, state):
        if len(state[0]) == len(state[1]):
            return 1
        else:
            return 2


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


    def is_terminal(self, state):
        winning_player = None
        terminal = False

        for player, player_state in enumerate(state, 1):
            if terminal:
                break
            for move in player_state:
                terminal = self.combination_length(state, player, move[0], move[1])
                if terminal:
                    winning_player = player
                    break

        if not terminal and len(state[0]) + len(state[1]) == self.n*self.m:
            winning_player = 0
            terminal = True

        return terminal, winning_player


    def combination_length(self, state, player, x, y):
        terminal = False

        if player == 1:
            previous_moves = state[0]
        elif player == 2:
            previous_moves = state[1]

        def horizontal(x, y, step):
            return(x+step, y)

        def diagonal_R(x, y, step):
            return(x+step, y+step)

        def verical(x, y, step):
            return(x, y+step)

        def diagonal_L(x, y, step):
            return(x-step, y+step)

        directions = [horizontal, diagonal_R, verical, diagonal_L]

        for direction in directions:
            if terminal:
                break
            step=1
            while True:
                if direction(x, y, step) in previous_moves:
                    step += 1
                else:
                    if step >= self.k:
                        terminal = True
                    break
        return terminal


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




if __name__ == "__main__":
    game = Game(4, 4, 4)
    game.play()
