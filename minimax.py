from typing import List, Tuple
import random
import numpy as np
import time

def main():
    '''
    Setup and play the game. Running minimax.py calls this function.
    '''
    game = Game(3, 3, 3, automatic_players = [1,2], manual_players = [1], display = True)
    game.play()

UPPER_CASE_OFFSET = 64

class Game(object):
    """
    Class representing the (m, n, k)-game.
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
        Initilise the game. Allows the user to set the parameters of the game
        when instantiating a new Game. The state of the game is reperesented by
        a 2-tuple of sets (set(), set()), where the first set cotains the moves
        made by player1(max) and the second set moves made by player2(min).
        Each move is reperesented by a 2-tuple (coord_x, coord_y) where coord_x
        is an integer representing the projection of a coordinate on the x-axis
        of the board i.e a column of the game-grid. This coordinate is reperensented
        alphabetically to the user such that A==first column, B==second column etc.
        coord_y is an integer representing the projection of a coordinate on the y-axis
        of the board i.e a row of the game-grid such that 1==first row, 2==second_row etc.
        For players in both automatic_players and manual_players the minimax algorithm will
        suggest a move but the user can choose what move to make.

        :param m: integer representing the size of the grid along the x-axis
        :param n: integer representing the size of the grid along the y-axis
        :param k: integer representing the number of consecutive squares a player
        needs to occupy on the grid to win the game
        :param automatic_players: List defining the player to be played automatically
                   by the mininmax algorithm. [1, 2] means both
                   player1 and player2 are played automatically.
                   And empty list [] means none are played automatically
        :param manual_players: List defining the player to be played manually
                by the mininmax algorithm.
        :param display: Boolean deciding if the graphical a reperesentation of the game
         will be displayed or not.
        """


        self.m = m
        self.n = n
        self.k = k

        self.automatic_players = automatic_players
        self.manual_players = manual_players
        self.display = display

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
        """
        Simulates an entire game. Prints necessary information about the
        current state of the board. Players in self.manual_players are played by
        user and players in self.automatic_players are played automatically by
        the minimax algorithm. For players in both self.manual_players and self.automatic_players
        moves are reccomended by the minimax algoritim but the user chooses which
        move to make.
        :return: a list of the execution times of moves made by automatic players
        with the last element being the total game time.
        """
        player = 1
        terminal = False
        winning_player = None

        message_manual = 'The computer recommends the move(s): '
        message_automatic = 'The computer makes the move: '
        message_invalid = 'Invalid move!. That cell is either occupied or out of bounds.'

        times = []
        game_start = time.time()
        #game loop
        while True:
            state = self.state
            if self.display:
                self.drawboard(self.state)
            # if current state is terminal print relevat message about the result.
            if terminal:
                if winning_player == 1:
                    print('Player 1 WON!')
                elif winning_player == 2:
                    print('Player 2 WON!')
                elif winning_player == 0:
                    print('Its a TIE!')
                break

            print(f'Player {player} to move...')
            #manual player with assitance from algorithm
            if player in self.automatic_players and player in self.manual_players:
                actions = self.minimax_action(state, player)
                board_coordinates = self.array_to_board_coordinates(actions)
                message = message_manual + board_coordinates
                print(message)
                board_coordinates = input('Input your move: ')
                action = self.board_to_array_coordinates(board_coordinates)
            # fully automatic player
            elif player in self.automatic_players:
                action_start = time.time()
                action = self.minimax_action(state, player)[0]
                action_end = time.time()
                times.append(action_end-action_start)
                board_coordinates = self.array_to_board_coordinates([action])
                message = message_automatic + board_coordinates
                print(message)
            #fully manual player
            elif player in self.manual_players:
                board_coordinates = input('Input your move: ')
                action = self.board_to_array_coordinates(board_coordinates)
            #check if the move is valid
            if self.is_valid(self.state, action):
                #if valid update state and check if new state is terminal
                self.state = self.resulting_state(state, action, player)
                terminal, winning_player = self.is_terminal(self.state, action, player)
                #clear saved states to avoid running ou of RAM
                self.buffer.clear()
                #switch current player
                player = player%2 + 1
            else:
                # if move invalid return to top of loop without changing the state
                # or current player.
                print(message_invalid)

        game_end = time.time()
        times.append(game_end - game_start)
        return times


    def minimax_action(self, state, player):
        """
        Calculates the minimax action for a given player in a given game state

        :param state: 2-tuple of sets(set(), set()) reperesentin the current
                      state of the game.
        :param player: The player to make a move:
                       player = 1 --> max-action
                       player = 2 --> min-action
        :return: a list all optimal actions possible in the current game state. i.e
                 actions with values equal to the action value of the minimax actions
                 for the given player.
       """
        optimal_actions = []
        self.action_values.clear()
        if player == 1: #max-action
            optimal_value = self.max_value(state, last_action = None, depth = 0)
        elif player == 2: #min-action
            optimal_value = self.min_value(state, last_action = None, depth = 0)
        for action, value in self.action_values.items():
            if value == optimal_value:
                optimal_actions.append(action)
        return optimal_actions


    def max_value(self, state, last_action, depth, player=2):
        """
        Calculates the minimax value for player 'max'(player1) for a given state.
        Apart from the standard minimax algorithm this
        function also has some extra lines to store values of states and to
        recall values of already seen states. This is necissary to speed up the
        calculation which otherwise took unreasoably long for anny game bigger
        than (3,3,3).

        :param state: 2-tuple of sets(set(), set()) reperesenting the current
                      state of the game.

        :param last_action: The last action taken in the game(the previous move
                            by the opposing player). Used to speed up the is_terminal
                            calculation.
        :param depth: Parameterer to track the depth of the recursion to store
                      values of states one move away from the current state as the recursion
                      unwinds.
        :param player: The player who made the last move. Used in the is_terminal
                       calculation.

        :return: The maximum action value for the current state.
       """
        terminal, winning_player = self.is_terminal(state, last_action, player)
        if terminal:
            return(self.utility(winning_player))
        v = -float('inf')
        ###############################################
        # THESE LINES ARE FOR LOOKING UP VALUES OF
        # PREVIOUS STATES TO SPEED THE CALCULATION UP
        ###############################################
        v_buffer = self.buffer.lookup(state)
        if v_buffer == None:
            pass
        elif v_buffer != None:
            return v_buffer
        ###############################################
        # THESE LINES ARE FOR LOOKING UP VALUES OF
        # PREVIOUS STATES TO SPEED THE CALCULATION UP
        ###############################################
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 1)
            v_new = self.min_value(new_state, action, depth + 1)
            v = max(v, v_new)
            if depth == 0:
                self.action_values[action] = v_new

        self.buffer.add(state, v)
        return v


    def min_value(self, state, last_action, depth, player=1):
        """
        Calculates the minimax value for player 'min'(player2) for a given state.
        part from the standard minimax algorithm this
        function also has some extra lines to store values of states and to
        recall values of already seen states. This is necissary to speed up the
        calculation which otherwise took unreasoably long for any game bigger
        than (3,3,3).

        :param state: 2-tuple of sets(set(), set()) reperesenting the current
                      state of the game.
                      can be discared as not being better than what has already been seen.
        :param last_action: The last action taken in the game(the previous move
                            by the opposing player). Used to speed up the is_terminal
                            calculation.
        :param depth: Parameterer to track the depth of the recursion to store
                      values of states one move away from the current state as the recursion
                      unwinds.
        :param player: The player who made the last move. Used in the is_terminal
                       calculation.

        :return: The minimum action value for the current state.
       """
        terminal, winning_player = self.is_terminal(state, last_action, player)
        if terminal:
            return(self.utility(winning_player))
        v = float('inf')
        ###############################################
        # THESE LINES ARE FOR LOOKING UP VALUES OF
        # PREVIOUS STATES TO SPEED THE CALCULATION UP
        ###############################################
        v_buffer = self.buffer.lookup(state)
        if v_buffer == None:
            pass
        elif v_buffer != None:
            return v_buffer
        ###############################################
        # THESE LINES ARE FOR LOOKING UP VALUES OF
        # PREVIOUS STATES TO SPEED THE CALCULATION UP
        ###############################################
        for action in self.actions(state):
            new_state = self.resulting_state(state, action, 2)
            v_new = self.max_value(new_state, action, depth + 1)
            v = min(v, v_new)
            if depth == 0:
                self.action_values[action] = v_new

        self.buffer.add(state, v)
        return v


    def actions(self, state):
        """
        Calculates the possible action is a gives state as the difference between
        the possible action on an empty board and the current state.

        :param state: 2-tuple of sets(set(), set()) reperesenting the current
                      state of the game.

        :return: A set of the possible actions in the given state.
        """
        return(self.possible_moves - state[0] - state[1])


    def resulting_state(self, state:tuple, action:tuple, player):
        """
        Calculates the resulting state if a given action is taken in a given state.

        :param state: 2-tuple of sets(set(), set()) reperesenting the current
                      state of the game.
        :param action: 2-tuple (coord_x, coord_y) representin an action where coord_x
                       is an integer representing the projection of a coordinate on the x-axis
                       of the board i.e a column of the game-grid. coord_y is an
                       integer representing the projection of a coordinate on the y-axis.

        :return: 2-tuple of sets(set(), set()) reperesenting the resulting
                 state of the game.
        """
        new_state = (state[0].copy(), state[1].copy())
        if player == 1:
            new_state[0].add(action)
            return(new_state[0], new_state[1])
        elif player == 2:
            new_state[1].add(action)
            return(new_state[0], new_state[1])


    def utility(self, winning_player):
        """
        Calculates the utility of a terminal state given the winning player.

        :param winning_player: integer representing the winning player:
                               winning_player = 1 --> 'max' won
                               winning_player = 2 --> 'min' won
                               winning_player = 0 --> game is tied

        :return: if winning_player = 1 --> 1
                 if winning_player = 2 --> -1
                 if winning_player = 0 --> 0
        """
        if winning_player == 1:
            return 1
        elif winning_player == 2:
            return -1
        elif winning_player == 0:
            return 0


    def horizontal(self, x, y, step):
        """
        Helper function to search for is_terminal to find terminal states.

        :param x: An integer representing the projection of a coordinate on the x-axis.
        :param y: An integer representing the projection of a coordinate on the y-axis.
        :param step: An integer representing the number of "steps" to take horizontally
                    from (x, y).

        :return: (x+step, y)
        """
        return(x+step, y)

    def diagonal_R(self, x, y, step):
        """
        Helper function to search for is_terminal to find terminal states.

        :param x: An integer representing the projection of a coordinate on the x-axis.
        :param y: An integer representing the projection of a coordinate on the y-axis.
        :param step: An integer representing the number of "steps" to take on the right
                     diagonal from (x, y).

        :return: (x+step, y+step)
        """
        return(x+step, y+step)

    def verical(self, x, y, step):
        """
        Helper function to search for is_terminal to find terminal states.

        :param x: An integer representing the projection of a coordinate on the x-axis.
        :param y: An integer representing the projection of a coordinate on the y-axis.
        :param step: An integer representing the number of "steps" to take vertically
                    from (x, y).

        :return: (x, y+step)
        """
        return(x, y+step)

    def diagonal_L(self, x, y, step):
        """
        Helper function to search for is_terminal to find terminal states.

        :param x: An integer representing the projection of a coordinate on the x-axis.
        :param y: An integer representing the projection of a coordinate on the y-axis.
        :param step: An integer representing the number of "steps" to take on the left
                     diagonal from (x, y).

        :return: (x-step, y+step)
        """
        return(x-step, y+step)


    def is_terminal(self, state, last_action, player):
        """
        Terminal check from the given state. Uses the last action taken and the player
        who took this action to speed up calculations since this allows to look
        only for terminal combinations that involve the last action taken.
        For example in this state of a (3,3,3)-game:
                                A   B   C
                              -------------
                            3 | O | O | X | 3
                              -------------
                            2 | X | X | X | 2
                              -------------
                            1 | O | X | O | 1
                              -------------
                                A   B   C
        knowing that the last action was for example C2 allows to look only
        at combinations involving C2 in the terminal check.

        :param state: 2-tuple of sets(set(), set()) reperesenting the current
                      state of the game.

        :param last_action: The last action taken in the game.

        :param player: The player who made the last move.

        :return: (terminal, winning_player) where terminal is a boolean which:
                 terminal = True --> state is terminal
                 terminal = False --> state is not terminal
                 and winning_player representing the winner of the game:

                 winning_player = 1 --> 'max' won
                 winning_player = 2 --> 'min' won
                 winning_player = 0 --> game is tied
                 winning_player = None if terminal=False
        """
        terminal = False
        winning_player = None
        if last_action == None:
            return terminal, winning_player
        previous_moves = state[player - 1]
        x = last_action[0]
        y = last_action[1]

        for direction in self.directions:#check each direction
            comb_len = 1
            step = 1
            while True:
                if direction(x, y, step) in previous_moves:#player also occupies this cell
                    comb_len += 1
                    step += 1
                else:#player does not occupies this cell
                    break

            step = -1#check the other way
            while True:
                if direction(x, y, step) in previous_moves:#player also occupies this cell
                    comb_len += 1
                    step -= 1
                else:#player does not occupies this cell
                    break

            if comb_len >= self.k:#check if the combination is long enough to win
                terminal = True
                winning_player = player
                break

        if not terminal and len(state[0]) + len(state[1]) == self.n*self.m:#check if tied
            winning_player = 0
            terminal = True

        return terminal, winning_player


    def is_valid(self, state, action):
        """
        Check if a given action is valid in a given state. The action needs to be
        in bounds of the board and be an unoccupied cell.

        :param state: 2-tuple of sets(set(), set()) reperesenting the current
                      state of the game.
        :param action: 2-tuple (coord_x, coord_y) representin an action where coord_x
                       is an integer representing the projection of a coordinate on the x-axis
                       of the board i.e a column of the game-grid. coord_y is an
                       integer representing the projection of a coordinate on the y-axis.

        :return: True if action is valid, False if action is invalid.
        """
        x_bound = 1 <= action[0] <= self.m
        y_bound = 1 <= action[1] <= self.n
        not_occupied_p1 = action not in state[0]
        not_occupied_p2 = action not in state[1]

        return(all([x_bound, y_bound, not_occupied_p1, not_occupied_p2]))


    def drawboard(self, state):
        """
        Function to draw the board on screen for a given state.
        """
        array_board = [[' ' for _ in range(self.m)] for _ in range(self.n)]
        for x, y in state[0]:
            array_board[self.n - y][x - 1] = 'X'

        for x, y in state[1]:
            array_board[self.n - y][x - 1] = 'O'

        board_str = self.get_board_string(array_board)
        print(board_str)


    def get_board_string(self, array_board):
        """
        Convert array representing the boards state to a printable string.
        """
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
        """
        Convert coordinates from array index to its printed representation.
        """
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
        """
        Convert coordinates from its printed representation to array index.
        """
        x_array = ord(coordinate[0].upper()) - UPPER_CASE_OFFSET
        y_array = int(coordinate[1])
        return(x_array, y_array)


class ExperienceBuffer:
    '''
    Class to setup the storage of state values. This is used to achive reasonable
    execution times on the computers avalable to me.
    '''

    def __init__(self):
        self.buffer = {}

    def add(self, state, value):
        '''
        Add state to buffer.
        '''
        frozen_state = (frozenset(state[0]), frozenset(state[1]))
        if frozenset not in self.buffer:
            self.buffer[frozen_state] = value
        else:
            pass

    def lookup(self, state):
        '''
        Lookup the value for a stored state
        '''
        frozen_state = (frozenset(state[0]), frozenset(state[1]))
        if frozen_state in self.buffer:
            return(self.buffer[frozen_state])
        else:
            return None

    def clear(self):
        '''
        Clear stored states
        '''
        self.buffer.clear()

if __name__ == "__main__":
    main()
