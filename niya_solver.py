# how shall we represent a Niya position?
# let's represent tiles by pairs (i,j) where i,j are 0 to 3
# let's represent pieces of the players by (-1,1) and (-1,-1)


# no point actually storing things as a 4 by 4 array

def code(i,j):
    return i*4 + j

checks = []

def add_condition(x):
    checks.append(tuple(x))

for i in range(4):
    add_condition([code(i,j) for j in range(4)])
for i in range(4):
    add_condition([code(j,i) for j in range(4)])
add_condition([code(i,i) for i in range(4)])
add_condition([code(i,3-i) for i in range(4)])
for i in range(3):
    for j in range(3):
        t = []
        for ii in range(2):
            for jj in range(2):
                t.append(code(i+ii,j+jj))
        add_condition(t)

# scores... 1000 for +1 win, -1000 for -1 win
# For each possible attack, 1 point, 10 points, or 100 points for viability

maxScore = 1000000


def score(board):
    runningTotal = 0
    for c in checks:
        plus = minus = 1
        for i in c:
            if(board[i][0] == -1):
                if(board[i][1] == 1):
                    plus *= 10
                else:
                    minus *= 10
        if(plus == 10000):
            return maxScore*multiplier(board)
        if(minus == 10000):
            return -maxScore*multiplier(board)
        if plus > 1 and minus > 1:
            continue
        runningTotal += plus
        runningTotal -= minus
    return runningTotal

def multiplier(board):
    mult = 1
    for i in range(16):
        if(board[i][0] != -1):
            mult += 1
    return mult

def display(board):
    def helper(t):
        if(t[0] != -1):
            return str(t[0]) + str(t[1])
        if(t[1] == 1):
            return '++'
        return '--'
    for i in range(4):
        s = ""
        for j in range(4):
            s += helper(board[code(i,j)]) + " "
        print(s)

def build_lookup(board):
    lookup = {}
    for i in range(16):
        lookup[board[i]] = i
    return lookup

def next_moves(board,previous,lookup):
    running_list = []
    def helper(t):
        if(t == previous):
            return
        if(board[lookup[t]] == t):
            running_list.append(lookup[t])
    for i in range(4):
        t = (previous[0],i)
        helper(t)
    for i in range(4):
        t = (i,previous[1])
        helper(t)
    return running_list



    # return -1 to indicate no move available
    # if lookahead = 0, the returned move is garbage
    # if the game is OVER, the returned move is garbage
def bestMoveAndScore(board,who,previous,lookup,lookahead,ub,lb):
    moves = next_moves(board,previous,lookup)
    if(len(moves) == 0):
        return (-1,-who*maxScore*multiplier(board))
    if(lookahead <= 0):
        return (-1,score(board))
    ess = score(board)
    if(ess >= maxScore or ess <= -maxScore):
        return (-1,ess)
    pairs = []
    for m in moves:
        t = board[m]
        board[m] = (-1,who)
        s = score(board)*who
        pairs.append((m,s))
        board[m] = t
    pairs.sort(key = lambda x : x[1], reverse = True)
    moves = [x[0] for x in pairs]
    # print("Sorted move list is " + str(moves))

    # ok now handle the moves
    if(who > 0):
        bestScore = lb
        bestMove = -1
        for m in moves:
            t = board[m]
            board[m] = (-1,who)
            (junk,s) = bestMoveAndScore(board,-who,t,lookup,lookahead - 1,ub,bestScore)
            board[m] = t
            if (s > bestScore):
                bestMove = m
                bestScore = s
            if bestScore >= ub:
                return (bestMove,bestScore)
        return (bestMove,bestScore)
    else:
        bestScore = ub
        bestMove = -1
        for m in moves:
            t = board[m]
            board[m] = (-1,who)
            (junk,s) = bestMoveAndScore(board,-who,t,lookup,lookahead - 1,bestScore,lb)
            board[m] = t
            if (s < bestScore):
                bestMove = m
                bestScore = s
            if bestScore <= lb:
                return (bestMove,bestScore)
        return (bestMove,bestScore)



       

       
    


from random import *
x = [(i % 4,i//4) for i in range(16)]
shuffle(x)
print(x)
display(x)
ell = build_lookup(x)
print(ell)
curr = randrange(15)
while(curr in [5,6,9,10]):
    curr = randrange(15)
print("Moving randomly at location " + str(curr))
prev = x[curr]
x[curr] = (-1,1)
display(x)
who = -1
over = False
while not over:    
    mov = next_moves(x,prev,ell)
    ahead = 15
    # print("Analyzing with lookahead " + str(ahead))
    (mov,scor) = bestMoveAndScore(x,who,prev,ell,ahead,100*maxScore,-100*maxScore)
    if mov == -1:
        over = True
        print("Player " + str(who) + " forfeits")
    else:
        prev = x[mov]
        print("Player " + str(who) + " is picking up piece " + str(prev[0]) + str(prev[1]) + ", expecting a score of " + str(scor))
        x[mov] = (-1,who)
        display(x)
        # print("Score is now " + str(score(x)))
        who = -who
        ess = score(x)
        if (ess >= maxScore):
            over = True
            print("Player 1 wins!")
        elif (ess <= -maxScore):
            over = True
            print("Player -1 wins!")




# class GameState:
#     def __init__(self, 
