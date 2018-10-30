# imports -------------------------------------------------
import sys
import pygame
from MyGame import MyGame

# variables -----------------------------------------------
game = MyGame()
running = True
commands = [0, 0, 0, 0]     # [shoot, left, right, throttle] commands for a step are integers, should only be 1 or 0
obs = []        # returned by game.step and are the observations or input for the neural net

# tensorflow ----------------------------------------------

# main loop -----------------------------------------------
while running:
    obs = game.step(commands)

    commands = [0, 0, 0, 0]
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        commands[0] = 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        commands[2] = 1
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        commands[1] = 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        commands[3] = 1


# quit game -----------------------------------------------
pygame.quit()
sys.exit()
