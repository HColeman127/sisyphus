# imports -------------------------------------------------
import tensorflow as tf
from keras import backend
from keras import models
from keras import layers
import numpy as np


# class definition ----------------------------------------
class CompGraph(object):
    INPUT_SIZE = 11
    HIDDEN_SIZE = 16
    OUTPUT_SIZE = 4
    GENOME_LENGTH = INPUT_SIZE*HIDDEN_SIZE + HIDDEN_SIZE + HIDDEN_SIZE*OUTPUT_SIZE + OUTPUT_SIZE
    #GENOME_LENGTH += HIDDEN_SIZE**2 + HIDDEN_SIZE

    def __init__(self, params):
        # clear backend
        backend.clear_session()

        # create graph
        self.model = models.Sequential()
        self.model.add(layers.InputLayer(batch_size=1, input_shape=[self.INPUT_SIZE]))
        self.model.add(layers.Dense(self.HIDDEN_SIZE, activation="sigmoid"))
        #self.model.add(layers.Dense(self.HIDDEN_SIZE, activation="sigmoid"))
        self.model.add(layers.Dense(self.OUTPUT_SIZE, activation="sigmoid"))
        self.model.compile(optimizer=tf.train.GradientDescentOptimizer(0.01), loss='mse', metrics=['mae'])

        #print(self.model.summary())

        # format graph parameters and assign to graph
        self.params = self.format_params(params)
        self.model.set_weights(self.params)

    def eval(self, input_list):
        # takes a list of input values and evaluates the graph and returns outputs
        output = self.model.predict(np.array([np.array(input_list)]), batch_size=1)[0]
        return np.round(output, 0)

    def format_params(self, params_list):
        # create numpy array out of list
        params = np.array(params_list)

        # find separation indexes based on the sizes of each graph layer
        ih_w_index = self.INPUT_SIZE * self.HIDDEN_SIZE
        ih_b_index = ih_w_index + self.HIDDEN_SIZE
        #hh_w_index = ih_b_index + self.HIDDEN_SIZE ** 2
        #hh_b_index = hh_w_index + self.HIDDEN_SIZE
        ho_w_index = ih_b_index + self.HIDDEN_SIZE * self.OUTPUT_SIZE
        ho_b_index = ho_w_index + self.OUTPUT_SIZE

        # create a 2d array for each set of weights and a 1d graph for each set of biases
        ih_w = params[:ih_w_index].reshape((self.INPUT_SIZE, self.HIDDEN_SIZE))
        ih_b = params[ih_w_index:ih_b_index]
        #hh_w = params[ih_b_index:hh_w_index].reshape((self.HIDDEN_SIZE, self.HIDDEN_SIZE))
        #hh_b = params[hh_w_index:hh_b_index]
        ho_w = params[ih_b_index:ho_w_index].reshape((self.HIDDEN_SIZE, self.OUTPUT_SIZE))
        ho_b = params[ho_w_index:ho_b_index]

        # return all weights and biases as a single numpy array
        return np.array([ih_w, ih_b, ho_w, ho_b])
