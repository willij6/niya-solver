import random
import time
import threading


# how shall we represent a Niya position?
# let's represent tiles by pairs (i,j) where i,j are 0 to 3
# let's represent pieces of the players by (-1,1) and (-1,-1)


# no point actually storing things as a 4 by 4 array

def code(i,j):
    return i + j*4

def get_checks():
    for i in range(4):
        yield([code(i,j) for j in range(4)])
    for i in range(4):
        yield([code(j,i) for j in range(4)])
    yield([code(i,i) for i in range(4)])
    yield([code(i,3-i) for i in range(4)])
    for i in range(3):
        for j in range(3):
            t = []
            for ii in range(2):
                for jj in range(2):
                    t.append(code(i+ii,j+jj))
            yield(t)

            
checks = list(get_checks())


# because python orders tuples lexicographically,
# scores will now work this way:
# (1,i) means that Plus wins by i points (i tiles remain)
# (-1,-i) means that Minus wins by i points (i tiles remain)
# (0,j) means neither player won (got the configuration of pieces)
# in which case... we iterate over checks, and
# for each position which could be completed, we assign 10**n pieces
# for a row/column/etc with n friendly pieces and no enemy pieces

def score(board):
    runningTotal = 0
    for c in checks:
        plus = 0
        minus = 0
        for i in c:
            if(board[i][0] == -1):
                if(board[i][1] == 1):
                    plus += 1
                else:
                    minus += 1
        if plus==4:
            return (1,tiles_left(board))
        if minus==4:
            return (-1,-tiles_left(board))
        if plus > 0 and minus == 0:
            runningTotal += 10**plus
        elif minus > 0 and plus == 0:
            runningTotal -= 10**plus
    return (0,runningTotal)

def tiles_left(board):
    count = 0
    for i in range(16):
        if(board[i][0] != -1):
            count += 1
    return count


def name_piece(t):
    if(t[0] != -1):
        return "abcd"[t[0]] + str(t[1])
    if(t[1] == 1):
        return '++'
    return '--'


def display(board):
    for i in range(4):
        s = ""
        for j in range(4):
            s += name_piece(board[code(i,j)]) + " "
        print(s)


cache = {}
remember_depth = 4

# FUN WITH CLOSURES

def bestMoveAndScore(board,who,previous,lookahead):
    print("bMAS called with position")
    display(board)
    print("And " + ("Red" if who == -1 else "Black") + " is about to move")
    depth = 0
    
    lookup = {}
    for i in range(4):
        for j in range(4):
            lookup[(i,j)] = False
    for i in range(16):
        lookup[board[i]] = i

    def next_moves():
        '''return the locations of the next possible moves'''
        if(previous == None):
            perimeter = [ 0, 1, 2, 3,
                          4,       7,
                          8,      11,
                         12,13,14,15]
            return [p for p in perimeter if board[p][0] != -1]
        running_list = []
        def helper(t):
            if(t == previous):
                return
            if(lookup[t] and board[lookup[t]] == t):
                running_list.append(lookup[t])
        for i in range(4):
            helper((previous[0],i))
        for i in range(4):
            helper((i,previous[1]))
        return running_list

    # returns (move,score), where
    # min(ub,max(lb,score)) = min(ub,max(lb,true_score))
    # and where move is a move attaining score
    # assuming lb < score < ub and the game ain't over
    # and lookahead is positive...
    # else move is garbage/None
    def recursive_eval(ub,lb):
        key = (who,previous,tuple(board))
        if(key in cache):
            return cache[key]
        (move,score) = inner_recursive_eval(ub,lb)
        if(depth <= remember_depth and lookahead > 0
           and lb < score and score < ub):
            cache[key] = (move,score)
        return (move,score)
    
    def inner_recursive_eval(ub,lb):
        nonlocal who, previous, lookahead, depth
        # nonlocal board, lookup... except they're not getting assigned to

        # print("Considering this position with lookahead = %d:" % lookahead)
        # display(board)
        
        moves = next_moves()
        if(len(moves) == 0):
            return (None,(-who,-who*tiles_left(board)))
        s = score(board)
        if(lookahead <= 0 or s[0] != 0): # s[0] != 0 checks for game over
            return (None,s)

        # sort the moves
        pairs = []
        for m in moves:
            t = board[m]
            board[m] = (-1,who)
            s = score(board)*who
            pairs.append((m,s))
            board[m] = t
        pairs.sort(key = lambda x : x[1], reverse=True)
        moves = [x[0] for x in pairs]
        # now the moves are sorted

        if(who > 0):
            bestScore = lb
            bestMove = None

            lookahead -= 1
            depth += 1
            who = -1
            old_prev = previous
            for m in moves:
                t = board[m]
                previous = t # paranoia
                board[m] = (-1,1)
                (junk,s) = recursive_eval(ub,bestScore)
                board[m] = t
                if s > bestScore:
                    bestMove = m
                    bestScore = s
                if bestScore >= ub:
                    break
            previous = old_prev
            who = 1
            lookahead += 1
            depth -= 1
            return (bestMove,bestScore)
        else:
            bestScore = ub
            bestMove = None

            lookahead -= 1
            depth += 1
            who = 1
            old_prev = previous
            for m in moves:
                t = board[m]
                previous = t
                board[m] = (-1,-1)
                (junk,s) = recursive_eval(bestScore,lb)
                board[m] = t
                if s < bestScore:
                    bestMove = m
                    bestScore = s
                if bestScore <= lb:
                    break
            previous = old_prev
            who = -1
            lookahead += 1
            depth -= 1
            return (bestMove,bestScore)
        
    return recursive_eval((2,0),(-2,0))


       
    
def do_stuff():


    board = [(i % 4,i//4) for i in range(16)]
    random.shuffle(board)
    display(board)

    prev = None
    who = 1

    over = False
    while not over:    
        ahead = 16
        # print("Analyzing with lookahead " + str(ahead))
        blah = time.perf_counter()
        (mov,scor) = bestMoveAndScore(board,who,prev,ahead)
        blah = time.perf_counter() - blah
        print("After thinking for %.2f secs, " % blah,end="")
        if mov is None:
            over = True
            print("Player " + str(who) + " forfeits")
        else:
            prev = board[mov]
            print("Player " + str(who) + " is picking up piece " +
                  name_piece(prev)+  ", expecting a score of " + str(scor))
            board[mov] = (-1,who)
            display(board)
            # print("Score is now " + str(score(x)))
            who = -who
            ess = score(board)
            if (ess[0] == 1):
                over = True
                print("Player 1 wins!")
            elif (ess[0] == -1):
                over = True
                print("Player -1 wins!")



# do_stuff()

# threading.Thread(target=do_stuff).start()
# while(True):
#     blah = input("> ")
#     print("You typed " + blah)

    
