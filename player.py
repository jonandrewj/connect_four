import value
import board
import numpy
import random
import os
import train

def get_player(player_id, color, random_chance=0.10):
    # RANDOM PLAYER
    if player_id == 0:
        return Player(color, None, 1.0, player_id)

    # HUMAN PLAYER
    if player_id == 11:
        return HumanPlayer(color)

    if player_id == 12:
        return DecentPlayer(color)

    # RETURN AN EXISTING PLAYER
    path_to_model = 'players/' + str(player_id) + '/model.h5'
    if os.path.isfile(path_to_model):
        network = value.load_from_file(path_to_model)
        return Player(color, network, random_chance, player_id)

    # CREATE A NEW PLAYER
    return Player(color, value.ValueNetwork(), random_chance, player_id)

class RolloutScore:
    def __init__(self, column, network_score, starting_board):
        self.column = column
        self.network_score = network_score
        self.starting_board = starting_board
        self.rollout_sum = 0.0
        self.rollout_games_count = 0

    def add_rollout_result(self, rollout_score):
        self.rollout_sum += rollout_score
        self.rollout_games_count += 1

    def score(self):
        discount = 0.7 if self.rollout_games_count > 15 else 0.4
        rollout_score = (self.rollout_sum / self.rollout_games_count) * discount
        return rollout_score + self.network_score

    def confidence(self):
        percent = (((self.rollout_sum / self.rollout_games_count) + 1.0) / 2.0) * 100
        return "{:10.1f}".format(percent)

class Player:
    def __init__(self, color, network, random_chance, player_id):
        self.color = color
        self.board = board
        self.network = network
        self.random_chance = random_chance
        self.player_id = player_id

    def play(self, board, human_playing=False):
        cols = board.get_playable_columns()
        if len(cols) is 0:
            raise Exception('The board is full but a player was still told to play ', board.grid)

        # WIN IF POSSIBLE
        played_col = self.in_a_row(self.color, board)
        if played_col != None:
            return played_col, True

        # BLOCK IF NEEDED
        played_col = self.in_a_row(self.color*-1, board)
        if played_col != None:
            return played_col, False

        # PLAY AT RANDOM
        if random.random() < self.random_chance:
            random_col = random.choice(cols)
            board.place(random_col, self.color)
            return random_col, False
            
        # TAKE THE BEST OPTION
        best_column = self.rollout_best_options(board, human_playing)
        board.place(best_column, self.color)
        return best_column, False

    def place_basic_best_option(self, game_board, random_chance):
        # WIN IF POSSIBLE
        played_col = self.in_a_row(self.color, game_board)
        if played_col != None:
            return played_col, True

        # BLOCK IF NEEDED
        played_col = self.in_a_row(self.color*-1, game_board)
        if played_col != None:
            return played_col, False

        # PLAY AT RANDOM
        if random.random() < random_chance:
            cols = game_board.get_playable_columns()
            played_col = random.choice(cols)
            game_board.place(played_col, self.color)
            return played_col, False

        # USE MY NETWORK
        cols, boards = self.get_options(game_board)
        values = self.network.predict(boards)
        best_column = cols[numpy.argmax(values)]
        game_board.place(best_column, self.color)
        return best_column, False

    def rollout_best_options(self, game_board, human_playing=False):
        cols = game_board.get_playable_columns()
        options = []

        for col in cols:
            game_copy = game_board.copy()
            game_copy.place(col, self.color)
            grid = numpy.stack([game_copy.get_grid(self.color)])
            network_value = self.network.predict(grid)[0][0]
            options.append(RolloutScore(col, network_value, game_copy))

        for rollout in options:
                self.rollout_endings(rollout, 20)
        
        while len(options) > 4:
            for rollout in options:
                self.rollout_endings(rollout, 5)
            options.sort(key=lambda item: item.score())
            del options[0]

        while len(options) > 1:
            for rollout in options:
                self.rollout_endings(rollout, 10)
            options.sort(key=lambda item: item.score())
            del options[0]

        if human_playing:
            print('Confidence: ' + options[0].confidence() + '%')

        return options[0].column

    def rollout_endings(self, rollout_object, num_randomizations):
        for _ in range(num_randomizations):
            game_board = rollout_object.starting_board.copy()
            opponent = train.PlayerPool.get_random_opponent(self.color*-1)
            result = self.rollout_ending(game_board, rollout_object.column, opponent)
            rollout_object.add_rollout_result(result)

    def rollout_ending(self, game_board, column, opponent):
        last_played_color = self.color
        last_played_column = column

        playable_cols = game_board.get_playable_columns()
        won = game_board.won(last_played_column, last_played_color)
        while not won and len(playable_cols) > 0:
            last_played_color *= -1
            if last_played_color == self.color:
                last_played_column, won = self.place_basic_best_option(game_board, 0.0)
            else:
                last_played_column, won = opponent.place_basic_best_option(game_board, 0.01)

            playable_cols = game_board.get_playable_columns()

        if won:
            return 1.0 if last_played_color == self.color else -1.0
        else:
            return 0.0

    def search_best_options(self, game_board):
        cols = game_board.get_playable_columns()
        options = numpy.zeros((len(cols), 1))

        for idx, col in enumerate(cols):
            col_value = self.get_move_value(game_board.copy(), col, 2)
            options[idx] = col_value

        return cols[numpy.argmax(options)]

    def get_move_value(self, game_board, column, search_depth):
        search_depth -= 1
        game_board.place(column, self.color)

        # IF I WON, THIS THIS COLUMN IS PERFECT
        if game_board.won(column, self.color):
            return 1.0

        # IF I CAN'T SEARCH ANYMORE, RETURN THE APPROXIMATE VALUE FROM THE NETWORK
        if search_depth == 0:
            grid = numpy.stack([game_board.get_grid(self.color)])
            return self.network.predict(grid)[0]

        # CHECK FOR A DRAW
        cols = game_board.get_playable_columns()
        if len(cols) == 0:
            return 0.0

        # LET A DECENT OPPONENT PLAY AGAINST ME
        col, opponent_won = self.play_decent_move(game_board, self.color*-1)
        if opponent_won:
            return -1.0

        # CHECK FOR A DRAW
        cols = game_board.get_playable_columns()
        if len(cols) == 0:
            return 0.0 

        # RECURSE AND TAKE THE AVERAGE VALUE OF THE OPTIONS
        options = numpy.zeros((len(cols), 1))
        for idx, col in enumerate(cols):
            col_value = self.get_move_value(game_board.copy(), col, search_depth)
            options[idx] = col_value

        return options.sum() / len(cols)

    def play_decent_move(self, game_board, color):
        # WIN IF POSSIBLE
        played_col = self.in_a_row(self.color, game_board)
        if played_col != None:
            return played_col, True

        # BLOCK IF NEEDED
        played_col = self.in_a_row(self.color*-1, game_board)
        if played_col != None:
            return played_col, False

        # PLAY AT RANDOM
        cols = game_board.get_playable_columns()
        played_col = random.choice(cols)
        game_board.place(played_col, self.color)
        return played_col, False

    def get_options(self, board):
        cols = board.get_playable_columns()
        boards = []
        for col in cols:
            copy = board.copy()
            copy.place(col, self.color)
            boards.append(copy.get_grid(self.color))

        if len(boards) > 0:
            boards = numpy.stack(boards)
        return cols, boards

    def save_model(self):
        path_to_model = 'players/' + str(self.player_id) + '/model.h5'
        self.network.save_model(path_to_model)

    def save_data(self):
        path_to_rounds = 'players/' + str(self.player_id) + '/rounds'
        self.network.save_data(path_to_rounds)

        max_files = 75
        files = [int(name) for name in os.listdir(path_to_rounds)]
        if len(files) > max_files:
            path_to_archive = 'players/' + str(self.player_id) + '/archive'
            if not os.path.exists(path_to_archive):
                os.makedirs(path_to_archive)
            
            files.sort()
            for to_archive in files[:len(files)-max_files]:
                cur_loc = os.path.join(path_to_rounds, str(to_archive))
                new_loc = os.path.join(path_to_archive, str(to_archive))
                os.rename(cur_loc, new_loc)

    def fit_all_games(self):
        path_to_rounds = 'players/' + str(self.player_id) + '/rounds'
        self.network.fit_all(path_to_rounds)

    def in_a_row(self, color, gameboard):
        cols = gameboard.get_playable_columns()
        for col in cols:
            row = 0
            while gameboard.grid[col][row] != 0:
                row += 1

            # DOWN
            if (row >= 3 and 
                gameboard.grid[col][row-1] == color and
                gameboard.grid[col][row-2] == color and
                gameboard.grid[col][row-3] == color):
                gameboard.place(col, self.color)
                return col

            # HORIZONTAL
            right_col = col+1
            right_count = 0
            while right_col < board.COLUMNS and gameboard.grid[right_col][row] == color:
                right_count += 1
                right_col += 1

            left_col = col-1
            left_count = 0
            while left_col >= 0 and gameboard.grid[left_col][row] == color:
                left_count += 1
                left_col -= 1

            if right_count + left_count >= 3:
                gameboard.place(col, self.color)
                return col

            # UPWARD DIAGONAL
            r_col = col+1
            r_row = row+1
            r_count = 0
            while (r_col < board.COLUMNS and
                r_row < board.ROWS and
                gameboard.grid[r_col][r_row] == color):
                r_col += 1
                r_row += 1
                r_count += 1

            l_col = col-1
            l_row = row-1
            l_count = 0
            while (l_col >= 0 and l_row >= 0 and
                gameboard.grid[l_col][l_row] == color):
                l_col -= 1
                l_row -= 1
                l_count += 1

            if r_count + l_count >= 3:
                gameboard.place(col, self.color)
                return col

            # DOWNWARD DIAGONAL
            r_col = col+1
            r_row = row-1
            r_count = 0
            while (r_col < board.COLUMNS and r_row >= 0 and
                gameboard.grid[r_col][r_row] == color):
                r_col += 1
                r_row -= 1
                r_count += 1

            l_col = col-1
            l_row = row+1
            l_count = 0
            while (l_col >= 0 and l_row < board.ROWS and
                gameboard.grid[l_col][l_row] == color):
                l_col -= 1
                l_row += 1
                l_count += 1

            if r_count + l_count >= 3:
                gameboard.place(col, self.color)
                return col

        return None


class HumanPlayer(Player):
    def __init__(self, color):
        super().__init__(color, None, 0.0, 11)

    def play(self, game_board, human_playing=False):
        for _ in range(15):
            print()

        for row in range(board.ROWS-1, -1, -1):
            for col in range(board.COLUMNS):
                if game_board.grid[col][row] == -1:
                    print('O', end=' ')
                elif game_board.grid[col][row] == 1:
                    print('X', end=' ')
                else:
                    print(' ', end=' ')
            print()
        
        for col in range(board.COLUMNS):
            print(str(col), end=' ')
        print()

        options = game_board.get_playable_columns()
        choice = None
        while choice not in options:
            print('Your Turn!', end=' ')
            answer = input()
            try:
                choice = int(answer)
            except:
                pass

        game_board.place(choice, self.color)
        won = game_board.won(choice, self.color)
        return choice, won

class DecentPlayer(Player):
    def __init__(self, color):
        super().__init__(color, None, 0.0, 12)

    def play(self, board, human_playing=False):
        return self.play_decent_move(board, self.color)

class RandomPlayer(Player):
    def __init__(self, color):
        super().__init__(color, None, 0.0, 12)

    def play(self, board, human_playing=False):
        # PLAY AT RANDOM
        cols = board.get_playable_columns()
        random_column = random.choice(cols)
        board.place(random_column, self.color)
        won = board.won(random_column, self.color)
        return random_column, won

    