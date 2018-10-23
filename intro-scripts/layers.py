
import tensorflow as tf
sess = tf.Session()

# set up the linear model
x = tf.placeholder(tf.float32, shape=[None, 3])
linear_model = tf.layers.Dense(units=1)
y = linear_model(x)

# iniitalize variables
init = tf.global_variables_initializer()
sess.run(init)

writer = tf.summary.FileWriter('logs')
writer.add_graph(tf.get_default_graph())

print(sess.run(y, {x: [[1, 2, 3],[1, 2, 3]]}))
print(sess.run(y, {x: [[1, 2, 3],[1, 2, 3]]}))
