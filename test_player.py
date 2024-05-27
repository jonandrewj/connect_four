import player
import board
import value
import unittest
import numpy
import player

class PlayerTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_options(self):
        full = self.full_board()
        p = player.Player(board.RED, None, 0.0)
        cols, _ = p.get_options(full)
        self.assertEqual(len(cols), 0)

        simple = self.simple_board()
        p = player.Player(board.BLACK, None, 0.0)
        cols, _ =  p.get_options(simple)
        self.assertEqual(len(cols), board.COLUMNS)

        complicated = self.complicated_board()
        p = player.Player(board.RED, None, 0.0)
        cols, _ =  p.get_options(complicated)
        self.assertEqual(cols, [0, 1, 3, 4, 5])

    def test_play(self):
        network = value.ValueNetwork()

        simple = self.simple_board()
        p = player.Player(board.BLACK, network, 0.0)
        p.play(simple)
        self.assertEqual(numpy.sum(simple.grid), 1)

        complicated = self.complicated_board()
        p = player.Player(board.RED, network, 0.0)
        p.play(complicated)
        self.assertEqual(numpy.sum(complicated.grid), -2)

    def full_board(self):
        full = board.Board()
        full.grid = numpy.ones((board.COLUMNS, board.ROWS))
        return full

    def simple_board(self):
        simple = board.Board()
        simple.place(2, board.RED)
        simple.place(4, board.BLACK)
        simple.place(4, board.RED)
        simple.place(3, board.BLACK)
        return simple

    def complicated_board(self):
        complicated = board.Board()
        for _ in range(board.ROWS):
            complicated.place(2, board.BLACK)
        for _ in range(board.ROWS):
            complicated.place(6, board.RED)
        complicated.place(0, board.RED)
        complicated.place(1, board.RED)
        complicated.place(3, board.RED)
        complicated.place(4, board.BLACK)
        complicated.place(5, board.BLACK)
        return complicated