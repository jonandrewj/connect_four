import unittest
import value
import game
import board
import numpy
import player

class GameTests(unittest.TestCase):
    def test_simulate(self):
        outcomes = set()
        all_outcomes = set(['black wins', 'red wins', 'draw'])
        simulations = 0
        while simulations < 10 and outcomes != all_outcomes:
            simulations += 1
            outcome = self.simulate_one_game()
            outcomes.add(outcome)

    def simulate_one_game(self):
        b = board.Board()
        n1 = value.ValueNetwork()
        n2 = value.ValueNetwork()
        p1 = player.Player(board.RED, n1, 0.1)
        p2 = player.Player(board.BLACK, n2, 0.1)
        winner, reds, blacks = game.simulate(b, p1, p2)
        if winner == board.BLACK:
            self.assertEqual(numpy.sum(b.grid), len(blacks)-len(reds))
            return 'black wins'
        elif winner == board.RED:
            self.assertEqual(numpy.sum(b.grid), len(blacks)-len(reds))
            return 'red wins'
        else:
            self.assertEqual(numpy.sum(b.grid), len(blacks)-len(reds))
            self.assertEqual(numpy.sum(b.grid), 0)
            self.assertEqual(len(blacks), len(reds))
            self.assertFalse((b.grid == 0).any())
            return 'draw'

    def test_trainer(self):
        iterstopper = game.StopAfterIterations(1500)
        training_network = value.ValueNetwork()
        training_player = player.Player(board.RED, training_network, 0.05)
        random_player = player.Player(board.BLACK, None, 1.0)
        training_player = game.train(training_player, random_player, iterstopper.can_continue)
        win_ratio, loss_ratio = game.score_player(training_player, random_player, 500)
        print('Win Ratio: ', win_ratio)
        print('Loss Ratio: ', loss_ratio)
        self.assertTrue(win_ratio > 0.80)

                   