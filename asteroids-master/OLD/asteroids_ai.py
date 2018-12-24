# imports -------------------------------------------------
import tensorflow as tf
from keras import models
from keras import layers
import numpy as np
import os


# class definition ----------------------------------------
class AsteroidsAI(object):
    def __init__(self):
        self.pop_size = 0
        pass

    def create_pop(self, pop_size):
        self.pop_size = pop_size

    def train(self, score):
        """
        target = something

        self.model.train(inputs, expectyedoutputs?, batch_size=1, epochs=1, verbose=1)"""
        pass

    def get_values(self):
        # scoop
        pass
