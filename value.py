import keras
from keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from keras.models import Sequential, load_model
import board
import numpy
import os
import random
import pickle
import time

def load_from_file(path):
    model = load_model(path)
    return ValueNetwork(model)

class ValueNetwork:
    def __init__(self, model=None):
        self.has_x_data = False
        self.x_data = None
        self.y_data = None

        if model == None:
            self.model = keras.Sequential()
            self.model.add(Conv2D(48, 
                kernel_size=(3, 3), 
                activation='sigmoid',
                input_shape=(board.COLUMNS, board.ROWS, 1), 
                kernel_initializer='random_uniform',
                bias_initializer='random_uniform'))
            self.model.add(MaxPooling2D(pool_size=(2, 2), strides=(1, 1)))
            self.model.add(Conv2D(64, 
                kernel_size=(3, 3), 
                activation='sigmoid', 
                kernel_initializer='random_uniform',
                bias_initializer='random_uniform'))
            #self.model.add(MaxPooling2D(pool_size=(2, 2)))
            self.model.add(Flatten())
            self.model.add(Dense(120, 
                activation='tanh', 
                kernel_initializer='random_uniform',
                bias_initializer='random_uniform'))
            self.model.add(Dense(1, 
                activation='tanh', 
                kernel_initializer='random_uniform',
                bias_initializer='random_uniform'))
            self.model.compile(loss=keras.losses.mean_squared_error,
                optimizer=keras.optimizers.Adam())
        else:
            self.model = model

    def train(self, x, y):
        x = x[..., numpy.newaxis]
        if not self.has_x_data:
            self.x_data = x
            self.y_data = y
            self.has_x_data = True
        else:
            self.x_data = numpy.append(self.x_data, x, axis=0)
            self.y_data = numpy.append(self.y_data, y, axis=0)
        self.model.train_on_batch(x, y)

    def predict(self, x):
        x = x[..., numpy.newaxis]
        return self.model.predict_on_batch(x)

    def get_weights(self):
        return self.model.get_weights()

    def set_weights(self, weights):
        self.model.set_weights(weights)

    def fit(self):
        if self.has_x_data:
            self.model.fit(self.x_data, self.y_data)

    def fit_all(self, path):
        generator = DataGenerator(path)
        self.model.fit_generator(generator=generator, epochs=1)

    def save_model(self, path):
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.model.save(path)

    def save_data(self, path):
        if self.has_x_data:
            if not os.path.exists(path):
                os.makedirs(path)
            
            filename = str(int(time.time() * 1000))
            dump_path = os.path.join(path, filename)

            with open(dump_path, 'wb') as dump_file:
                pickle.dump({'x_data': self.x_data, 'y_data': self.y_data}, dump_file)

            

class DataGenerator(keras.utils.Sequence):
    def __init__(self, path):
        self.files = [path+'/'+filename for filename in os.listdir(path)]
        random.shuffle(self.files)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        filename = self.files[index]
        with open(filename, 'rb') as read_file:
            data = pickle.load(read_file)
            return data['x_data'], data['y_data']
        
        