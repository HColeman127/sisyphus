# imports -------------------------------------------------
import sys
import pygame
import time
from MyGame import MyGame

# variables -----------------------------------------------
game = MyGame()
running = True
commands = [0, 0, 0, 0]     # [shoot, left, right, throttle] commands for a step are integers, should only be 1 or 0
obs = []        # returned by game.step and are the observations or input for the neural net

# tensorflow ----------------------------------------------

# main loop -----------------------------------------------
while running:
    time.sleep(.05)
    obs = game.step(commands)




# quit game -----------------------------------------------
pygame.quit()
sys.exit()
