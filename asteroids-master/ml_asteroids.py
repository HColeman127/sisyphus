# imports -------------------------------------------------
import sys
import pygame
import time
import tensorflow as tf
from MyGame import MyGame

# variables -----------------------------------------------
"""game = MyGame()
running = True
commands = [0, 0, 0, 0]     # [shoot, left, right, throttle] commands for a step are integers, should only be 1 or 0
obs = [] """       # returned by game.step and are the observations or input for the neural net

# tensorflow ----------------------------------------------
x = tf.placeholder(tf.float32, [number of input sets, number of input neurons])
y = tf.layers.dense(x, units=number of oiutput neurons)
#y = linear_model(x)

init = tf.global_variables_initializer()

writer = tf.summary.FileWriter('logs')
writer.add_graph(tf.get_default_graph())

sess = tf.Session()
sess.run(init)

print(sess.run(y, feed_dict={x: [[1], [2], [3], [4]]}))

# main loop -----------------------------------------------
"""while running:
    time.sleep(.05)
    obs = game.step(commands)
"""



# quit game -----------------------------------------------
pygame.quit()
sys.exit()
