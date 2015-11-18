#!/usr/bin/python
'''Do random validation that stuff runs and is sound'''
from analyzer import *
import random

def random_initial_board():
    pieces = []
    for i in range(4):
        for j in range(4):
            pieces.append(tile(i,j))
    random.shuffle(pieces)
    pieces = [[pieces[i*4+j] for i in range(4)] for j in range(4)]
    board = Position(pieces,black(),None)
    return board

def flail(board):
    move_stack = []
    while(board.check_victory() == 0):
        moves = board.get_moves()
        random.shuffle(moves)
        move = moves.pop()
        move_stack.append(move)
        move.do()
    length = len(move_stack)
    for i in range(length//2):
        move_stack.pop().undo()


def sanity_check(board):
    if(board.check_victory() != 0):
        assert(board.score() == board.eval())
        return
    
    moves = board.get_moves()
    scores = []
    for m in moves:
        m.do()
        scores.append(board.eval())
        m.undo()
    scores.sort(reverse = (board.whose_move() > 0))
    assert(board.eval() == scores[0]),str(board.eval())+"!="+str(scores[0])
    m = board.best_move()
    m.do()
    score = board.eval()
    m.undo()
    assert(score==board.eval())


for i in range(10):
    print(i)
    board = random_initial_board()
    sanity_check(board)
    flail(board)
    sanity_check(board)
    
    
