import unittest
import board

class BoardTests(unittest.TestCase):
    def setUp(self):
        self.board = board.Board()

    def test_init(self):
        self.assertEqual(self.board.grid.shape, (board.COLUMNS, board.ROWS))
        self.assertEqual(self.board.grid[3][4], 0.0)

    def test_place(self):
        res = self.board.place(0, board.BLACK)
        self.assertIsNone(res)
        self.board.place(0, board.RED)
        self.board.place(0, board.BLACK)
        self.board.place(0, board.RED)
        self.board.place(0, board.BLACK)
        self.board.place(0, board.RED)
        res = self.board.place(0, board.BLACK)
        self.assertIn('Cant play in this column because it is full', res)
        self.assertEqual(self.board.grid[0][3], board.RED)
        self.assertEqual(self.board.grid[0][4], board.BLACK)
        self.assertEqual(self.board.grid[0][5], board.RED)
        #with self.assertRaises(ValueError):
        #    self.board.place(7, board.RED)
        #with self.assertRaises(ValueError):
        #    self.board.place(-1, board.RED)

    def test_winner(self):
        # NO WINNER AT THIS SPOT YET
        res = self.board.winner(0, 3)
        self.assertEqual(res, None)

        # 4 VERTICAL 
        for _ in range(4):
            self.board.place(0, board.BLACK)
        res = self.board.winner(0, 3)
        self.assertEqual(res, board.BLACK)

        # 4 HORIZONTAL
        for row in range(1, 5):
            self.board.place(row, board.RED)
        res = self.board.winner(1, 0)
        self.assertEqual(res, board.RED)

        # DIAGONAL UPWARDS
        self.board = board.Board()
        for _ in range(3):
            self.board.place(6, board.BLACK)
        self.board.place(6, board.RED)
        for _ in range(2):
            self.board.place(5, board.BLACK)
        self.board.place(5, board.RED)
        self.board.place(4, board.BLACK)
        self.board.place(4, board.RED)
        self.board.place(3, board.RED)
        res = self.board.winner(3, 0)
        self.assertEqual(res, board.RED)

        # DIAGONAL DOWNWARDS
        self.board = board.Board()
        for _ in range(3):
            self.board.place(0, board.RED)
        self.board.place(0, board.BLACK)
        for _ in range(2):
            self.board.place(1, board.RED)
        self.board.place(1, board.BLACK)
        self.board.place(2, board.RED)
        self.board.place(2, board.BLACK)
        self.board.place(3, board.BLACK)
        res = self.board.winner(0, 3)
        self.assertEqual(res, board.BLACK)

        # ONLY 3 IN A ROW
        res = self.board.winner(0, 0)
        self.assertEqual(res, None)

    def test_finished(self):
        # GAME JUST STARTED
        res = self.board.finished()
        self.assertEqual(res, None)

        # BLACK HAS 4 IN A ROW
        for _ in range(3):
            self.board.place(0, board.RED)
        self.board.place(0, board.BLACK)
        for _ in range(2):
            self.board.place(1, board.RED)
        self.board.place(1, board.BLACK)
        self.board.place(2, board.RED)
        self.board.place(2, board.BLACK)
        self.board.place(3, board.BLACK)
        res = self.board.finished()
        self.assertEqual(res, board.BLACK)

        # DRAW
        self.board = board.Board()
        for col in range(board.COLUMNS):
            first_color = board.BLACK if col % 2 == 0 else board.RED
            for _ in range(3):
                self.board.place(col, first_color)
            for _ in range(3):
                self.board.place(col, -first_color)
        res = self.board.finished()
        self.assertEqual(res, 0)
        

    def test_copy(self):
        self.board.place(3, board.BLACK)
        self.board.place(3, board.RED)
        copy = self.board.copy()
        self.assertEqual(copy.grid[3][0], board.BLACK)
        self.assertEqual(copy.grid[3][1], board.RED)

    def test_get_board(self):
        self.board.place(3, board.BLACK)
        self.board.place(3, board.RED)
        g1 = self.board.get_grid(board.BLACK)
        self.assertEqual(g1[3][0], board.BLACK)

        g2 = self.board.get_grid(board.RED)
        self.assertEqual(g2[3][0], board.RED)


        


        

