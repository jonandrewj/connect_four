import board
import player
import value
import numpy
import signal
import random
import sys

def simulate(game_board, first_player, second_player):
    first_boards = []
    second_boards = []

    firsts_turn = True
    if random.random() > 0.5:
        firsts_turn = False

    human_playing = False
    if first_player.player_id == 11 or second_player.player_id == 11:
        human_playing = True

    winner = None
    while winner == None:
        if firsts_turn:
            _, won = first_player.play(game_board, human_playing)
            first_boards.append(game_board.get_grid(first_player.color))
            if won:
                winner = first_player.color
        else:
            _, won = second_player.play(game_board, human_playing)
            second_boards.append(game_board.get_grid(second_player.color))
            if won:
                winner = second_player.color
            
        firsts_turn = not firsts_turn
        if len(game_board.get_playable_columns()) == 0:
            winner = 0 if winner == None else winner

    if first_player.player_id == 11 and first_player.color == winner:
        print('You Win!')
    if second_player.player_id == 11 and second_player.color == winner:
        print('You Win!')

    return winner, first_boards, second_boards

def trainable_scores(length, value):
    scores = numpy.zeros((length, 1))
    score = value
    for i in range(length-1, -1, -1):
        scores[i][0] = score
        score = score * 0.90
    return scores

def train(training_player, static_player, continue_function):
    while continue_function():
        b = board.Board()
        winner, training_moves, static_moves = simulate(b, training_player, static_player)

        training_score = 0
        static_score = 0
        if winner == training_player.color:
            training_score = 1.0
            static_score = -1.0
        elif winner == static_player.color:
            static_score = 1.0
            training_score = -1.0
            pass

        training_player.network.train(numpy.stack(training_moves), trainable_scores(len(training_moves), training_score))
        training_player.network.train(numpy.stack(static_moves), trainable_scores(len(static_moves), static_score))
        #print(b.grid)
        #print()

    #training_player.network.fit()
    return training_player

def score_player(player1, player2, num_tests):
    wins = 0
    losses = 0
    for _ in range(num_tests):
        b = board.Board()
        winner, _, _ = simulate(b, player1, player2)
        if winner == board.RED:
            wins += 1
        if winner == board.BLACK:
            losses += 1

    return wins/num_tests, losses/num_tests

class SignalHandler:
    def __init__(self):
        self.cancelled = False
        signal.signal(signal.SIGINT, self.handler)

    def can_continue(self):
        return not self.cancelled

    def handler(self, sig, frame):
        self.cancelled = True

class StopAfterIterations:
    def __init__(self, max):
        self.max = max
        self.count = 0

    def can_continue(self):
        self.count += 1
        return self.count < self.max

def random_player_ids():
    num_players = 10
    training_id = random.randint(1, num_players)
    static_id = random.randint(1, num_players)
    while training_id == static_id:
        static_id = random.randint(1, num_players)
    return training_id, static_id

def get_player_ids(argv):
    # TRAIN TWO RANDOM PLAYERS
    if len(sys.argv) == 1:
        return random_player_ids()

    # TRAIN THE TWO SPECIFIED PLAYERS
    if len(sys.argv) == 3:
        training_id = int(sys.argv[1])
        static_id = int(sys.argv[2])
        return training_id, static_id

def get_players(p1_id, p2_id, random_chance=0.5):
    return player.get_player(p1_id, board.RED, random_chance=random_chance), player.get_player(p2_id, board.BLACK, random_chance=random_chance)

def evaluate(training_player, num_tests=2000):
    decent_player = player.DecentPlayer(training_player.color*-1)
    win_ratio, loss_ratio = score_player(training_player, decent_player, num_tests)
    print('Win Ratio: ', win_ratio, end='\t')
    print('Loss Ratio: ', loss_ratio)

if __name__ == '__main__':
    training_id, static_id = get_player_ids(sys.argv)
    training_player, static_player = get_players(training_id, static_id, 0.0)

    print('Training player ' + str(training_id) + ' against player ' + str(static_id))
    iters = StopAfterIterations(100)
    training_player = train(training_player, static_player, iters.can_continue)
    training_player.save_data()
    training_player.fit_all_games()
    training_player.save_model()

    print('Testing player ' + str(training_id) + ' against player ' + str(static_id))
    win_ratio, loss_ratio = score_player(training_player, static_player, 500)
    print('Win Ratio: ', win_ratio)
    print('Loss Ratio: ', loss_ratio)

    evaluate(training_player)


 