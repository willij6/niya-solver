from analyzer import tile, Position, black, red
from analyzer import player_piece, Move, trial_run, loc
import unittest


# Goals for my unit tests:
# * Write examples of how the code should work
# * Sanity check that the code runs and returns sane answers in simple cases
#
# I agree with the motivation of TDD, if not the strict version of it

# TODO: make the tests clearer and easier to read!

class TestPosition(unittest.TestCase):


    def setUp(self):
        pieces = [[tile(i,j) for i in range(4)] for j in range(4)]
        self.pieces = pieces

    
    # check that the data is recalled correctly
    def test_data_storage(self):
        pieces = self.pieces
        board = Position(pieces,red(),None)
        self.assertEqual(red(),board.whose_move())
        for i in range(4):
            for j in range(4):
                self.assertEqual(pieces[i][j],board.get_piece(i,j))
        p = pieces[2][3]
        for i in range(4):
            for j in range(4):
                pieces[i][j] = None
        self.assertEqual(p,board.get_piece(2,3))


    def test_non_victory(self):
        pieces = self.pieces
        board = Position(pieces,red(),None)
        self.assertEqual(board.check_victory(),0)

    def test_configuration_victory(self):
        pieces = self.pieces
        # check a 2x2 block in the middle
        for i in range(1,3):
            for j in range(1,3):
                pieces[i][j] = player_piece(red())
        board = Position(pieces,black(),None)
        self.assertEqual(board.check_victory(),red())
        # now change the board so that black wins and red doesn't
        for i in range(4):
            pieces[i][i] = player_piece(black())
        # check that data is stored correctly
        self.assertEqual(board.check_victory(),red())
        # now check for real
        board = Position(pieces,black(),None)
        self.assertEqual(board.check_victory(),black())




        
    def test_victory_values_distinct(self):
        self.assertNotEqual(red(),black())
        self.assertNotEqual(0,red())
        self.assertNotEqual(0,black())

    def test_victory_via_no_moves(self):
        # make a board full of the same tile
        pieces = [[tile(0,0) for i in range(4)] for j in range(4)]
        # set the Previous Tile to something incompatible
        board = Position(pieces,black(),
                                  tile(1,1))
        # black to move, so red wins
        self.assertEqual(board.check_victory(),red())
        # now reverse the roles and check again
        board = Position(pieces,red(),
                                  tile(1,1))
        self.assertEqual(board.check_victory(),black())
        


    def test_perimeter_moves_at_start(self):
        pieces = self.pieces
        board = Position(pieces,black(),None)
        moves = board.get_moves()
        self.assertEqual(len(moves),4*4-2*2)
        for m in moves:
            (i,j) = m.get_location()
            self.assertTrue(i == 0 or i == 3 or j == 0 or j == 3)

    def test_moves_with_previous(self):
        pieces = self.pieces
        board = Position(pieces,black(),tile(0,0))
        # all the pieces close to tile(0,0)
        analogous = [tile(i,0) for i in range(4)] + \
                    [tile(0,i) for i in range(4)]
        moves = board.get_moves()
        self.assertGreater(len(moves),0)
        for move in moves:
            (i,j) = move.get_location()
            self.assertIn(pieces[i][j],analogous)

    def test_doing_and_undoing(self):
        pieces = self.pieces
        board = Position(pieces,black(),None)
        move = Move(board,loc(0,0))
        move.do()
        self.assertEqual(board.get_piece(0,0),
                         player_piece(black()))
        self.assertNotEqual(board.get_piece(0,0),pieces[0][0])
        self.assertEqual(board.whose_move(),red())
        self.assertEqual(board.previous_piece,pieces[0][0])
        moves = board.get_moves()
        self.assertEqual(len(moves),3+3)
        move.undo()
        self.assertEqual(board.get_piece(0,0),pieces[0][0])
        self.assertEqual(board.previous_piece,None)
        self.assertEqual(board.whose_move(),black())
        moves = board.get_moves()
        self.assertEqual(len(moves),4*4-2*2)
        

    def test_tile_count_via_moves(self):
        board = Position(self.pieces,black(),None)
        self.assertEqual(board.tile_count,4*4)
        move1 = board.get_moves().pop()
        move1.do()
        move2 = board.get_moves().pop()
        move2.do()
        self.assertEqual(board.tile_count,4*4-2)
        move2.undo()
        self.assertEqual(board.tile_count,4*4-1)
        move1.undo()
        self.assertEqual(board.tile_count,4*4)

    def test_tile_count_midgame(self):
        board = Position(self.pieces,black(),None)
        nMoves = 3
        # do 3 random moves
        for i in range(nMoves):
            board.get_moves().pop().do()
        pieces = [[None for i in range(4)] for j in range(4)]
        for i in range(4):
            for j in range(4):
                pieces[i][j] = board.get_piece(i,j)
        board = Position(pieces,board.whose_move(),
                                  board.previous_piece)
        self.assertEqual(board.tile_count,4*4-nMoves)

        

    def test_trial_run(self):
        # see if it runs without crashing...
        trial_run()
        # is this a bad sort of test?
        # There are no asserts,
        # and it takes forever to run
        
