import game
import player
import sys
import os
import random
import board

class PlayerPool:
    players = []
    num_players = 10

    @staticmethod
    def get_random_opponent(color):
        PlayerPool.init_players()
        player_id = random.randint(1, PlayerPool.num_players)
        player = PlayerPool.players[player_id-1]
        player.color = color
        return player

    @staticmethod
    def init_players():
        if len(PlayerPool.players) == 0:
            for player_id in range(1, 11):
                PlayerPool.players.append(player.get_player(player_id, board.BLACK, 0.02))


def learn(learning, static, num_games):
    iters = game.StopAfterIterations(num_games)
    training_player = game.train(learning, static, iters.can_continue)
    training_player.save_data()
    training_player.fit_all_games()
    training_player.save_model()

if __name__ == '__main__':
    for p in range(1, 11):
        if not os.path.isdir("players/"+str(p)):
            training, static = game.get_players(p, 0)
            learn(training, static, 100)

    iters = 20
    if len(sys.argv) == 2:
        iters = int(sys.argv[1])

    for i in range(iters):
        p1, p2 = game.random_player_ids()
        training, static = game.get_players(p1, p2)
        learn(training, static, 100)

    #odds_or_evens = random.randint(0, 1)
    #for p in [1, 3, 5, 7, 9]:
    #    p = p + 1
    #    print('Evaluating player: ' + str(p))
    #    trainee = player.get_player(p, board.RED, random_chance=0.0)
    #    game.evaluate(trainee, num_tests=200)

