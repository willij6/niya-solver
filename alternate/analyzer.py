import random
import time
import threading

# Utility functions

# To represent players
# TODO: use an Enum
def red():
    return -1
def black():
    return 1
def other_player(who):
    return -who

# To represent pieces
def tile(i,j):
    return (i,j)
def player_piece(who):
    return (-1,who)


# Additional functions to help the Position class

# Represent the board as a one-dimensional array of length 16
# rather than a 4x4 two-dimensional array,
# Why?
# * Speed
# * We care about certain sets of locations, and nothing else
#   (adjacency and directions are irrelevant)


# Encode a two-dimensional location as a number in the range 0 to 15
def loc(i,j):
    return i + j*4


def get_perimeter():
    '''Return a list of the perimeter locations, encoded using loc'''
    perimeter = set()
    for i in range(4):
        perimeter.add(loc(i,0))
        perimeter.add(loc(i,3))
        perimeter.add(loc(0,i))
        perimeter.add(loc(3,i))
    return list(perimeter)


def get_victory_configs():
    '''Return a list of victory configurations
    Each victory configuration is a list of four locations,
    encoded using loc
    A player wins by controlling all four locations
    (of any of the 19 configurations)'''

    v_configs = []
    # rows
    for i in range(4):
        v_configs.append([loc(i,j) for j in range(4)])
    # columns
    for i in range(4):
        v_configs.append([loc(j,i) for j in range(4)])
    # main diagonal
    v_configs.append([loc(i,i) for i in range(4)])
    # anti-diagonal
    v_configs.append([loc(i,3-i) for i in range(4)])
    # the 2x2 blocks
    for i in range(3):
        for j in range(3):
            config = []
            for ii in range(2):
                for jj in range(2):
                    config.append(loc(i+ii,j+jj))
            v_configs.append(config)
    return v_configs



class Position:
    '''Encapsulates a position of the game, including info on who moves next,
    and what the most recent move was'''
    
    def __init__(self,pieces,next_player,previous_piece):
        '''Create a new Position with the specified 4x4 array
        of pieces, the specified next-player-to-move,
        and specified previous piece'''

        self.pieces = [None for i in range(4*4)]
        self.tile_count = 0
        for i in range(4):
            for j in range(4):
                self.pieces[loc(i,j)] = pieces[i][j]
                # non-tile pieces (player tokens) are
                # distinguished by the -1 in their first coordinate
                if pieces[i][j][0] != -1:
                    self.tile_count += 1

        self.next_player = next_player
        self.previous_piece = previous_piece
        
        self.perimeter = get_perimeter()
        self.checks = get_victory_configs()


    def get_piece(self,i,j):
        '''Get the piece at location (i,j)'''
        return self.pieces[loc(i,j)]

    def whose_move(self):
        '''Return the player who moves next'''
        return self.next_player

    # return a list of Moves
    def get_moves(self):
        if self.previous_piece is None:
            return [Move(self,p) for p in self.perimeter]

        moves = []
        for i in range(4*4):
            piece = self.pieces[i]
            if(piece[0] == -1):
                continue
            if (piece[0] == self.previous_piece[0] or
                piece[1] == self.previous_piece[1]):
                moves.append(i)
        return [Move(self,p) for p in moves]


    # return (1,score) if victory for black
    # return (-1,-score) if victory for red
    # return (0,blah) if neither,
    # where blah is a numerical value that will help us
    # sort moves later.
    # add 1, 10, or 100
    def score(self):
        running_total = 0
        for config in self.checks:
            reds = blacks = 0
            for pos in config:
                if self.pieces[pos] == player_piece(black()):
                    blacks += 1
                elif self.pieces[pos] == player_piece(red()):
                    reds += 1
                if(reds > 0 and blacks > 0):
                    break
            if(reds > 0 and blacks > 0):
                continue
            if blacks == 4:
                return (1,self.tile_count)
            if reds == 4:
                return (-1,-self.tile_count)
            if blacks > 0:
                running_total += 10**blacks
            elif reds > 0:
                running_total -= 10**reds

        # also check for victory via no moves remaining
        if not self.get_moves():
            if self.next_player == red():
                return (1,self.tile_count)
            else:
                return (-1,-self.tile_count)

        return (0,running_total)
            
    # return red() or black() if one of those one, else return 0
    def check_victory(self):
        (winner,details) = self.score()
        return winner

    def eval(self):
        '''Evaluate a position, by analyzing it completely using
        the helper class Analysis'''
        immediate_score = self.score()
        if immediate_score[0] != 0:
            return immediate_score
        # (2,0) is higher than any possible score,
        # and (-2,0) is lower than any possible score
        return Analysis(self).alpha_beta_helper((2,0),(-2,0))

    def best_move(self):
        '''Return an optimal move (as a Move object),
        or None if the game is over'''
        immediate_score = self.score()
        if immediate_score[0] != 0:
            return None
        if self.next_player > 0:
            # Black to move, so maximize the score
            bestMove = None
            bestScore = (-2,0)
            for move in self.get_moves():
                move.do()
                score = Analysis(self).alpha_beta_helper((2,0),bestScore)
                move.undo()
                if(score > bestScore):
                    bestScore = score
                    bestMove = move
            return bestMove
        else:
            # Red to move, so minimize the score
            bestMove = None
            bestScore = (2,0)
            for move in self.get_moves():
                move.do()
                score = Analysis(self).alpha_beta_helper(bestScore,(-2,0))
                move.undo()
                if(score < bestScore):
                    bestScore = score
                    bestMove = move
            return bestMove


    def __str__(self):
        retval = ""
        for i in range(4):
            for j in range(4):
                p = loc(i,j)
                piece= self.pieces[p]
                if(piece == (-1,-1)):
                    retval += "Red    "
                elif piece==(-1,1):
                    retval += "Black  "
                else:
                    retval += str(self.pieces[p]) + " "
            retval += "\n"
        retval += ("Black" if self.next_player > 0 else "Red") + " to move"
        retval += ", also prev piece is " + str(self.previous_piece)
        return retval




class Move:
    '''Abstract representation of a possible move in a position.
    Calling do() changes the original position, and then calling
    undo() undoes it.  These calls must alternate.'''
    
    def __init__(self,parent,location):
        '''Move(p,Position.loc(i,j)) creates an abstract
        rep of a move in position p, at location (i,j)'''
        self.parent = parent
        self.location = location
        
    def do(self):
        '''Carry out the move'''
        position = self.parent
        self.old_previous = position.previous_piece
        position.previous_piece = position.pieces[self.location]
        position.pieces[self.location] = player_piece(position.next_player)
        position.next_player = other_player(position.next_player)
        position.tile_count -= 1

    def undo(self):
        '''Undo a move that has been carried out'''
        position = self.parent
        position.next_player = other_player(position.next_player)
        position.pieces[self.location] = position.previous_piece
        position.previous_piece = self.old_previous
        position.tile_count += 1

    def get_location(self):
        '''Return the location of the move'''
        i = self.location % 4
        j = self.location // 4
        return (i,j)

    
class Analysis:
    '''A class for managing all the temporary data
    involved with the alpha-beta pruning algorithm.

    Namely, just,
    * The transposition table cache
    * How deep we are in the recursion, to know whether
      to store in the transposition table.'''
    # TODO: that's not very much.  Is this class really necessary?
    
    # a map from triples (tuple(pieces),who,previous)
    # to scores
    cache = {}
    remember_depth = 4

    def __init__(self,position):
        self.position = position
        self.depth = 0


    # *assuming* self.position isn't over...
    # returns a number s such that
    # min(ub,max(lb,s)) = min(ub,max(lb,true_score))
    # where true_score is the true minmax score
    #
    # Note ub, lb, score, s are all tuples
    def alpha_beta_helper(self,ub,lb):
        # memoize around inner_alpha_beta_helper(ub,lb)
        key = (tuple(self.position.pieces),self.position.next_player,
               self.position.previous_piece)
        if(key in Analysis.cache):
            return Analysis.cache[key]
        score = self.inner_alpha_beta_helper(ub,lb)
        if(self.depth <= Analysis.remember_depth
           and lb < score and score < ub):
            Analysis.cache[key] = score
        return score


    def inner_alpha_beta_helper(self,ub,lb):

        # used to sort moves
        def sort_key(x):
            return x[0]

        # Break into cases by who moves next
        if(self.position.next_player > 0):
            # Black's moving next, so maximize the score

            moves = self.position.get_moves()

            non_terminal_moves = [] # a list of pairs (score,move)

            # first check for immediate victories,
            # If none exist, sort the non-terminal moves
            # by score and analyze them one by one
            for round in range(2):                
                bestScore = lb
                for m in moves:
                    m.do()
                    if round == 0:
                        score = self.position.score()
                    else:
                        self.depth += 1
                        score = self.alpha_beta_helper(ub,bestScore)
                        self.depth -= 1
                    m.undo()
                    if round == 0 and score[0] == 0:
                        non_terminal_moves.append((score[1],m))
                    if(score >= ub):
                        return score
                    if(score > bestScore):
                        bestScore = score
                if round == 1 or bestScore[0] != 0:
                    return bestScore
                # sort the moves, highest score first
                non_terminal_moves.sort(key = sort_key, reverse=True)
                moves = [pair[1] for pair in non_terminal_moves]
                # now the moves are sorted, and stripped of their temp scores                
        else:
            # Red's moving next, so minimize the score

            moves = self.position.get_moves()

            non_terminal_moves = [] # a list of pairs (score,move)

            # first check for immediate victories,
            # If none exist, sort the non-terminal moves
            # by score and analyze them one by one
            for round in range(2):                
                bestScore = ub
                for m in moves:
                    m.do()
                    if round == 0:
                        score = self.position.score()
                    else:
                        self.depth += 1
                        score = self.alpha_beta_helper(bestScore,lb)
                        self.depth -= 1
                    m.undo()
                    if round == 0 and score[0] == 0:
                        non_terminal_moves.append((score[1],m))
                    if(score <= lb):
                        return score
                    if(score < bestScore):
                        bestScore = score
                if round == 1 or bestScore[0] != 0:
                    return bestScore
                # sort the moves, lowest score first
                non_terminal_moves.sort(key = sort_key, reverse=False)
                moves = [pair[1] for pair in non_terminal_moves]
                # now the moves are sorted, and stripped of their temp scores



def trial_run():

    pieces = [[tile(i,j) for i in range(4)] for j in range(4)]
    board = Position(pieces,black(),None)
    print(board)
    while(True):
        v = board.check_victory()
        if v != 0:
            if v > 0:
                print("Black wins")
            else:
                print("Red wins")
            break
        else:
            # m = board.get_moves().pop()
            m = board.best_move()
            tup = m.get_location()
            print("Best move is at " + str(tup))
            m.do()
            print(board)

