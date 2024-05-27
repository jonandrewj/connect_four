import unittest
import value
import board
import numpy

class ValueTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_init(self):
        network = value.ValueNetwork()
        self.assertIsNotNone(network)
        self.assertIsNotNone(network.model)

    def test_weights(self):
        # TEST THAT WEIGHTS EXIST
        network1 = value.ValueNetwork()
        network2 = value.ValueNetwork()
        weights1 = network1.get_weights()
        weights2 = network2.get_weights()
        self.assertIsNotNone(weights1)
        self.assertIsNotNone(weights2)

        # TEST THAT TWO PREDICTIONS ARE DIFFERENT
        b = board.Board()
        b.place(3, board.BLACK)
        b.place(2, board.RED)
        b.place(2, board.BLACK)
        g = numpy.stack([b.grid])
        self.assertNotEqual(network1.predict(g), network2.predict(g))

        # TEST THAT TWO PREDICTIONS ARE THE SAME
        network2.set_weights(weights1)
        self.assertEqual(network1.predict(g), network2.predict(g))

    def test_train(self):
        # SET UP THE NETWORK
        network = value.ValueNetwork()
        b = board.Board()
        b.place(3, board.BLACK)
        b.place(2, board.RED)
        b.place(2, board.BLACK)
        g = numpy.stack([b.grid])
        first_prediction = network.predict(g)[0][0]
        
        # TRAIN; TEST THAT WE GOT A MORE ACCURATE PREDICTION
        network.train(g, [1])
        second_prediction = network.predict(g)[0][0]
        diff1 = abs(first_prediction - 1)
        diff2 = abs(second_prediction - 1)
        self.assertTrue(diff1 > diff2)

    def test_fit(self):
        # SET UP THE NETWORK
        network = value.ValueNetwork()
        b = board.Board()
        b.place(3, board.BLACK)
        b.place(2, board.RED)
        b.place(2, board.BLACK)
        g1 = numpy.stack([b.grid])
        first_prediction = network.predict(g1)[0][0]

        network.train(g1, [1])
        b.place(1, board.RED)
        g2 = numpy.stack([b.grid])
        network.train(g2, [1])
        network.fit()
        second_prediction = network.predict(g1)[0][0]
        diff1 = abs(first_prediction - 1)
        diff2 = abs(second_prediction - 1)
        self.assertTrue(diff1 > diff2)
        
        