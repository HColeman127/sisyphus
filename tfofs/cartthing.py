import gym

# Policies ----------------------------------------------

def policy_0(obs):
    ang = obs[2]

    if (ang<0):
        return 0
    else:
        return 1

def policy_1(obs):
    pos = obs[0]
    vel = obs[1]
    ang = obs[2]
    ang_vel = obs[3]

    if (ang+ang_vel+0.15*pos<0):
        return 0
    else:
        return 1



# Main Program --------------------------------------------
env = gym.make("CartPole-v0")
obs = env.reset()


for i in range(1000):
    action = policy_1(obs)
    obs, reward, done, info = env.step(action)
    env.render(mode="rgb_array")



# Exit Environment ----------------------------------------
env.close()
try:
    del env
except ImportError:
    pass