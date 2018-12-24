# imports -------------------------------------------------
import tensorflow as tf
import numpy as np
import os


# class definition ----------------------------------------
class BadAI(object):
    def __init__(self, input_size=11, hidden_size=10, output_size=4):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # create graph
        self.inputs = tf.placeholder(tf.float32, [1, self.input_size])
        self.layer_1 = tf.layers.dense(self.inputs, units=self.hidden_size)
        self.layer_2 = tf.layers.dense(self.layer_1, units=self.output_size)
        self.outputs = tf.round(tf.nn.sigmoid(self.layer_2))

        # train graph
        self.inv_score = tf.Variable(0.0)
        #self.training = tf.train.GradientDescentOptimizer(0.9).minimize(self.inv_score, var_list=tf.trainable_variables())
        self.grads = tf.train.GradientDescentOptimizer(0.9).compute_gradients(self.inv_score)

        # log shape of graph
        writer = tf.summary.FileWriter('logs')
        writer.add_graph(tf.get_default_graph())

        # start running graph
        init = tf.global_variables_initializer()
        self.sess = tf.Session()
        self.sess.run(init)

    def eval(self, input_array):
        return self.sess.run(self.outputs, feed_dict={self.inputs: [input_array]})[0]

    def train(self, score):
        inv_score = 1000/(max(score, 1))
        assign_inv = self.inv_score.assign(inv_score)

        self.sess.run(assign_inv)
        #self.sess.run(self.training)

        print(self.sess.run(self.grads))

    def get_values(self):
        all_vars = self.sess.run(tf.trainable_variables())

        kernel_1 = all_vars[0]
        bias_1 = all_vars[1]
        kernel_2 = all_vars[2]
        bias_2 = all_vars[3]


        print(np.around(kernel_1, 2))
