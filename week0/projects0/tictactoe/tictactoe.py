"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    """ 
        The idea I'll implement is that we will check 
        how many moves have been made so far. Technically, a human
        would consider three scenarios: 
            1 - If board is empty, then it would say it's turn of X
            2 - if board is not empty, it would count number of Xs and Os,
            reasoning that if Xs are equal to 0s then, it's X's turn as the first player.
            If not, it would be then 0's turn.
            3 - If board is full, then it's no one's turn. The game is over.
    """
    num_x_played = 0
    num_o_played = 0
    num_empty = 0
    # Counting what's happening on the board
    for row in board:
        for col in row:
            if col == "X":
                num_x_played += 1
            elif col == "O":
                num_o_played += 1
            else:
                num_empty += 1
    
    # The reasoning
    if num_x_played == num_o_played:
        # If the board is not full, then equality of Xs and 0s 
        # should mean that X will play since X is the first mover.
        if not num_empty == 0:
            return X
        else:
            # Basically, it should be no one's turn.
            return None
    # If there is no equality, then it should be 0 player's turn.
    # We can check for a 'glitch' where Os could be higher than X but
    # in reality it should not. I will write the validation anyway.
    else:
        if num_x_played > num_o_played:
            return O
        else:
            raise Exception("You cannot have more Os than Xs at any point of the game. You hacked the game?!")


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    # Creating the set
    possible_actions = set()
    
    # Using enumerate as I need to access the index of the tile along with its value
    for i, row in enumerate(board):
        for j, col in enumerate(row):
            if col == EMPTY:
                possible_actions.add((i, j))
    
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # Understanding the current player for the given board
    current_move = player(board)
    # Making a deep copy of the original board
    """
        We are making a copy instead of editing the board itself as 
        we still want to have access to the old board. We will store this
        in the search problem with minimax as we store the parent, the board
        that led to the new board.

        We want to make a deep copy as opposed to a shallow copy since
        a shallow copy (copy.copy(board)) would keep the refrences of the 
        items within the list, meaning that if we make changes to the items
        in the copy, it would change the items in the original list.
    """
    new_board = copy.deepcopy(board)

    # Getting the indices of the action with double assignment
    action_row, action_column = action

    # Adding the desired action to the new board
    new_board[action_row][action_column] = current_move

    return new_board
    

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    """
        So the idea is that there are eight possible scenarios where
        if all the values are 'X' then X player wins or if they are all
        'O' then 'O' player wins. 
    """

    winning_states = [
        [(0,0), (0, 1), (0, 2)],
        [(0,0), (1, 0), (2, 0)],
        [(0,0), (1, 1), (2, 2)],
        [(0,1), (1, 1), (2, 1)],
        [(0,2), (1, 1), (2, 0)],
        [(0,2), (1, 2), (2, 2)],
        [(1,0), (1, 1), (1, 2)],
        [(2,0), (2, 1), (2, 2)],
    ]

    for state in winning_states:
        tile0 = state[0]
        tile1 = state[1]
        tile2 = state[2]

        if board[tile0[0]][tile0[1]] == board[tile1[0]][tile1[1]] == board[tile2[0]][tile2[1]] and board[tile0[0]][tile0[1]] is not EMPTY:
            return board[tile0[0]][tile0[1]]
    
    # No winning state has been found
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # Let's first check if there is any winner. If yes, the game is over.
    if winner(board) is not None:
        return True
    
    """
        Checks each section of the board to see if any is empty
        This is assuming that boards are proper. We can add some 
        validation here if we wanted but no need.
    """
    for row  in board:
        for col in row:
            if col == EMPTY:
                # If any empty, then says there is still play to go
                return False
    # If no empty, returns true that game is over. 
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == 'X':
        return 1
    
    elif winner(board) == "O":
        return -1
    
    elif winner(board) == None:
        return 0

    else:
        raise Exception("You might have called the utility function before the game is over.")

# This is how the 'X' player is thinking, trying to maximize the value.
def max_value(board, min_val_seen=None, provide_move=False):
    # We need this to break out of the recursive once we get to the end of the game
    if terminal(board):
        return utility(board)
    
    # Assigning negative infinity to max value so that we know that every value
    # will be larger than this in the first place.
    max_val_seen = float("-inf")
    best_action = None

    # Looping over all the possible actions to see what board we might get and
    # then seeing what would be the minimum value of that board that our opponent
    # might want to take advantage of.
    for action in actions(board):
        highest_value_possible = min_value(result(board, action), max_val_seen=max_val_seen)

        # Allows Alpha-Beta Pruning
        if  min_val_seen and highest_value_possible > min_val_seen:
            return highest_value_possible

        if highest_value_possible > max_val_seen:
            max_val_seen = highest_value_possible
            best_action = action

    # I've added this bit as a prop to turn on and off when needed.
    if provide_move:
        return best_action
    else:
        return max_val_seen


# Basically, this function is how the 'O' player is thinking, trying to minimize the value.
def min_value(board, max_val_seen=None, provide_move=False):
    if terminal(board):
        return utility(board)

    # Assigning positive infinity to current value, which allows us to be impartial to all the 
    # possible actions.
    min_val_seen = float("inf")
    best_action = None

    for action in actions(board):
        lowest_value_possible = max_value(result(board, action), min_val_seen=min_val_seen)
    
        # Allows Alpha-Beta Pruning
        if max_val_seen and lowest_value_possible < max_val_seen:
            return lowest_value_possible

        if lowest_value_possible < min_val_seen:
            min_val_seen = lowest_value_possible
            best_action = action
    
    if provide_move:
        return best_action
    else:
        return min_val_seen


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # Let's return none before doing any hard work if the game is already over
    if terminal(board):
        return None

    # We need to know if AI is the X or O player to know what value to maximize.
    if player(board) == 'X':
        return max_value(board, provide_move=True)

        
    # We need to know if AI is the X or O player to know what value to maximize.
    if player(board) == 'O':
        return min_value(board, provide_move=True)
