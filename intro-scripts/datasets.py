from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf


a = tf.constant(3.0, dtype=tf.float32)
b = tf.constant(4.0) # also tf.float32 implicitly
total = a + b

writer = tf.summary.FileWriter('logs')
writer.add_graph(tf.get_default_graph())

sess = tf.Session()

my_data = [
    [0, 1,],
    [2, 3,],
    [4, 5,],
    [6, 7,],
]
slices = tf.data.Dataset.from_tensor_slices(my_data) # creates a tensorflow Dataset holding each of the elements (arrays) in my_data as slices
next_item = slices.make_one_shot_iterator().get_next()

while True:
  try:
    print(sess.run(next_item))
  except tf.errors.OutOfRangeError:
    break