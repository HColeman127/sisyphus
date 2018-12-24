# imports -------------------------------------------------
import tensorflow as tf
from keras import models
from keras import layers
import numpy as np


# class definition ----------------------------------------
class AsteroidsAI(object):
    def __init__(self, weights):
        self.input_size = 11
        self.hidden_size = 10
        self.output_size = 4

        # create graph
        self.model = models.Sequential()
        self.model.add(layers.InputLayer(batch_size=1, input_shape=[self.input_size]))
        self.model.add(layers.Dense(self.hidden_size))
        self.model.add(layers.Dense(self.hidden_size))
        self.model.add(layers.Dense(self.output_size, activation="sigmoid"))
        self.model.compile(optimizer=tf.train.GradientDescentOptimizer(0.01), loss='mse', metrics=['mae'])

        print(self.model.summary())

        #self.model.set_weights()


    def eval(self, input_array):
        return self.model.predict(np.array([np.array(input_array)]), batch_size=1)[0]

    def get_values(self):
        print(self.model.get_weights())
