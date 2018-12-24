import numpy as np
import time

arr = np.loadtxt("mean_log_1544909414.915266.txt")

print(arr)

np.savetxt("mean_log_"+time.strftime("%Y-%m-%d-%H%M%S", time.localtime())+".txt", arr, fmt="%d")