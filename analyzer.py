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
        (score,move) = self.alpha_beta_helper((2,0),(-2,0),0)
        return score
        # # (2,0) is higher than any possible score,
        # # and (-2,0) is lower than any possible score
        # return Analysis(self).alpha_beta_helper((2,0),(-2,0))

    def best_move(self):
        '''Return an optimal move (as a Move object),
        or None if the game is over'''
        print("Best move called on \n" + str(self))
        immediate_score = self.score()
        if immediate_score[0] != 0:
            return None
        (score,move) = self.alpha_beta_helper((2,0),(-2,0),0)
        return move




    # get a hashable description of this position
    def get_key(self):
        return (tuple(self.pieces),self.next_player,self.previous_piece)



    def alpha_beta_helper(self,upper,lower,depth):
        '''Recursively evaluate this position,
        Assumption: self is non-terminal, upper >= lower
        Return (s,move) where
            min(upper,max(lower,s)) = min(upper,max(lower,score))
        where score is the true final score under perfect play,
        AND if lower < s < upper, then move is an optimal move.'''        

        # first try all the moves and collect their scores
        def assess_move(move):
            move.do()
            score = self.score()
            move.undo()
            return score

        move_list = []
        for m in self.get_moves():
            score = assess_move(m)
            if(score[0] == self.next_player):
                return (score,m) # it's optimal
            elif(score[0] == -self.next_player):
                garbage = (score,m)
            else:
                move_list.append((score,m))
        
        if len(move_list) == 0:
            # all moves were (equally) terrible
            return garbage
            
        # sort the moves
        if(self.next_player > 0):
            # Black is maximizing the score
            move_list.sort(key = (lambda x: x[0]), reverse = True)
        else:
            # Red is minimizing the score
            move_list.sort(key = (lambda x: x[0]), reverse = False)
        # strip off the immediate scores
        move_list = [move for (score,move) in move_list]
            
        if(self.next_player > 0):
            bestScore = lower
            bestMove = None
            for move in move_list:
                move.do()
                (score,junk) = self.alpha_beta_helper(upper,bestScore,depth+1)
                move.undo()
                if(score > bestScore):
                    bestScore = score
                    bestMove = move
                if(score >= upper):
                    return (bestScore,bestMove)
            return (bestScore,bestMove)
        else:
            bestScore = upper
            bestMove = None
            for move in move_list:
                move.do()
                (score,junk) = self.alpha_beta_helper(bestScore,lower,depth+1)
                move.undo()
                if(score < bestScore):
                    bestScore = score
                    bestMove = move
                if(score <= lower):
                    return (bestScore,bestMove)
            return (bestScore,bestMove)

    # Let's see whether I can do this correctly
    inner_ab = alpha_beta_helper
    cache = {}
    def alpha_beta_helper(self,upper,lower,depth):
        key = self.get_key()
        if key in Position.cache:
            return Position.cache[key]
        (score,move) = Position.inner_ab(self,upper,lower,depth)
        if depth < 4 and lower < score and score < upper:
            Position.cache[key] = (score,move)
        return (score,move)
    
                
            
        
        

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


