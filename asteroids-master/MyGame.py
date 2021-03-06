from GameObjects import *
import numpy as np


def load_image_convert_alpha(filename):
    """Load an image with the given filename from the images directory"""
    return pygame.image.load(os.path.join('images', filename)).convert_alpha()


def draw_centered(surface1, surface2, position):
    """Draw surface1 onto surface2 with center at position"""
    rect = surface1.get_rect()
    rect = rect.move(position[0]-rect.width//2, position[1]-rect.height//2)
    surface2.blit(surface1, rect)


def rotate_center(image, rect, angle):
        """rotate the given image around its center & return an image & rect"""
        rotate_image = pygame.transform.rotate(image, angle)
        rotate_rect = rotate_image.get_rect(center=rect.center)
        return rotate_image, rotate_rect


def distance(p, q):
    """Helper function to calculate distance between 2 points"""
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)


class MyGame(object):

    def __init__(self, display):
        # set up a 800 x 600 window
        self.width = 1200
        self.height = 900
        self.death_distances = {"big": 90, "normal": 65, "small": 40}
        self.min_rock_distance = 100
        self.display = display

        # pygame/display stuff
        if self.display:
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.mixer.init()
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.init()
            self.bg_color = 0, 0, 0
            self.big_font = pygame.font.SysFont(None, 100)
            self.medium_font = pygame.font.SysFont(None, 50)
            self.small_font = pygame.font.SysFont(None, 25)
            self.lives_image = load_image_convert_alpha('spaceship-off.png')
            self.blip_image = load_image_convert_alpha('blip.png')

            # Setup a timer to refresh the display FPS times per second
            self.FPS = 60

        self.reset()

    def random_seed(self, seed=None):
        set_random_seed(seed)

    def reset(self):
        self.spaceship = Spaceship((self.width // 2, self.height // 2), display=self.display)
        self.missiles = []
        self.fire_time = 0
        self.score = 0
        self.shots = 0
        self.hits = 0

        self.rocks = []
        self.make_rock(pos=(self.width/2, self.height/4))
        for i in range(5):
            self.make_rock()

        self.dead = False

        return True, 0, self.get_observations()

    def make_rock(self, size="big", pos=None):
        """Make a new rock"""

        # minimum margin when creating rocks
        margin = 200

        if pos is None:
            # no position was passed. make at a random location

            rand_x = random.randint(margin, self.width - margin)
            rand_y = random.randint(margin, self.height - margin)

            # while the co-ordinate is too close, discard it
            # and generate another one
            while distance((rand_x, rand_y), self.spaceship.position) < self.min_rock_distance:
                # choose another random co-ordinate
                rand_x = random.randint(0, self.width)
                rand_y = random.randint(0, self.height)

            temp_rock = Rock((rand_x, rand_y), size, display=self.display)

        else:
            # a position was given through arguments
            temp_rock = Rock(pos, size, display=self.display)

        # add the recently created rock the the actual rocks list
        self.rocks.append(temp_rock)

    def step(self, commands=(0, 0, 0, 0)):
        if self.display:
            pygame.event.pump()
            #pygame.time.wait(round(1000/self.FPS))

        if self.display and False:
            commands = [0, 0, 0, 0]
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                commands[0] = 1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                commands[1] = 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                commands[2] = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                commands[3] = 1

        if self.dead:
            self.reset()

        # left
        if commands[0] == 1:
            self.spaceship.angle += 10
            self.spaceship.angle %= 360
        # right
        if commands[1] == 1:
            self.spaceship.angle -= 10
            self.spaceship.angle %= 360
        # thrust
        if commands[2] == 1:
        #if True:
            # increase the speed
            self.spaceship.velocity[0] += 0.5 * math.sin(-math.radians(self.spaceship.angle))
            self.spaceship.velocity[1] += 0.5 * -math.cos(math.radians(self.spaceship.angle))

            # max speed
            hypotenuse = math.sqrt(self.spaceship.velocity[0]**2 + self.spaceship.velocity[1]**2)
            if hypotenuse > 13:
                self.spaceship.velocity[0] = 13 * self.spaceship.velocity[0]/hypotenuse
                self.spaceship.velocity[1] = 13 * self.spaceship.velocity[1]/hypotenuse
                # fire
        if commands[3] == 1:
            if self.fire_time < 1:
            #if True:
                # print("FIRING!")
                # there should be a minimum of 0.15 delay between
                # firing each missile

                # fire a missile
                self.spaceship.fire()
                self.shots += 1

                # reset the current fire time
                self.fire_time = 20
            else:
                # print("RECHARGING")
                self.fire_time -= 1

        # if there are any missiles on the screen, process them
        if len(self.spaceship.active_missiles) > 0:
            self.missiles_physics()

        # if there are any rocks, do their physics
        if len(self.rocks) > 0:
            self.rocks_physics()

        # do the spaceship physics
        self.physics()

        if self.display:
            # draw everything
            self.draw()
            command_text = self.medium_font.render(str(commands), True, (0, 155, 0))
            draw_centered(command_text, self.screen,
                          (command_text.get_width(), self.height - command_text.get_height()))

        # return
        # bool: still playing, int: score, int: velocity x, int: velocity y, int: pointing angle
        return not self.dead, self.score, self.hits, self.shots, self.get_observations()

    def get_observations(self):
        obs = self.get_distances()

        # flip display because get_distances draws lines
        if self.display:
            pygame.display.flip()

        return obs

    def get_distances(self):
        rays = 8
        ang_step = 2*math.pi/rays

        # ship info
        ship_x, ship_y = self.spaceship.position
        ship_angle = math.radians((-90 - self.spaceship.angle) % 360)

        # ray info
        angles = []
        for i in range(rays):
            angles.append(i*ang_step + ship_angle)
            if angles[-1] >= 2*math.pi:
                angles[-1] -= 2*math.pi
        distances = [1000 for _ in range(rays)]

        for rock in self.rocks:
            # get the rock position relative to ship
            rock_x, rock_y = rock.position
            rock_rx = rock_x - ship_x
            rock_ry = rock_y - ship_y

            # loop around screen
            if rock_rx > self.width/2:
                rock_rx -= self.width
            elif rock_rx < -self.width/2:
                rock_rx += self.width

            if rock_ry > self.height/2:
                rock_ry -= self.height
            if rock_ry < -self.height/2:
                rock_ry += self.height

            # get rock angle with origin at ship
            rock_angle = math.atan2(rock_ry, rock_rx)
            if rock_angle < 0:
                rock_angle += 2*math.pi
            if rock_angle > (2*math.pi - ang_step/2):
                rock_angle -= 2*math.pi

            # find which angle index the found angle is closest to
            least_index = 0
            for i in range(rays):
                if abs(angles[i] - rock_angle) < abs(angles[least_index] - rock_angle):
                    least_index = i

            # check rays to the left and right as well
            for index in range(least_index-1, least_index+2):
                index = index % rays
                # distance between centers
                a = math.sqrt(rock_rx**2 + rock_ry**2)
                b = rock.radius
                B = abs(angles[index] - rock_angle)

                # find value under radical in equation
                radicand = (a**2)*(math.cos(B)**2 - 1) + b**2

                if radicand >= 0:
                    term_1 = a * math.cos(B)
                    term_2 = math.sqrt(radicand)

                    sum_1 = term_1+term_2
                    sum_2 = term_1-term_2

                    # find the min sum that is greater than zero
                    if sum_1 >= 0:
                        if sum_2 >= 0:
                            value = min(sum_1, sum_2)
                        else:
                            value = sum_1
                    else:
                        value = sum_2

                    if value < distances[index]:
                        distances[index] = value
                else:
                    pass

        if self.display and False:
            for i in range(rays):
                x = distances[i] * math.cos(angles[i])
                y = distances[i] * math.sin(angles[i])

                pygame.draw.line(self.screen, pygame.Color(255, 255, 255, 100),
                                 (ship_x, ship_y), (ship_x+x, ship_y+y))

        obs = [1/dist for dist in distances]
        return obs

    def physics(self):
        # call the move function of the object
        self.spaceship.move()

        # loop space
        self.spaceship.position[0] %= self.width
        self.spaceship.position[1] %= self.height

    def missiles_physics(self):
        """Do all the physics of missiles"""

        # if there are any active missiles
        if len(self.spaceship.active_missiles) > 0:
            for missile in self.spaceship.active_missiles:
                # move the missile
                missile.move()
                missile.lifeSpan += 1
                if missile.lifeSpan > missile.lifeMax:
                    self.spaceship.active_missiles.remove(missile)

                # loop space
                missile.position[0] %= self.width
                missile.position[1] %= self.height

                # check the collision with each rock
                for rock in self.rocks:

                    if rock.size == "big":
                        # if the missile hits a big rock, destroy it,
                        # make two medium sized rocks and give 20 scores
                        if distance(missile.position, rock.position) < 80:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("normal", (rock.position[0] + 10, rock.position[1]))
                            self.make_rock("normal", (rock.position[0] - 10, rock.position[1]))
                            self.score += 1
                            self.hits += 1

                    elif rock.size == "normal":
                        # if the missile hits a medium sized rock, destroy it,
                        # make two small sized rocks and give 50 scores
                        if distance(missile.position, rock.position) < 55:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("small", (rock.position[0] + 10, rock.position[1]))
                            self.make_rock("small", (rock.position[0] - 10, rock.position[1]))
                            self.score += 1
                            self.hits += 1
                    else:
                        # if the missile hits a small rock, destroy it,
                        # make one big rock if there are less than 10 rocks
                        # on the screen, and give 100 scores
                        if distance(missile.position, rock.position) < 30:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)

                            if len(self.rocks) < 10:
                                self.make_rock()

                            self.score += 1
                            self.hits += 1

    def rocks_physics(self):
        """Move the rocks if there are any"""

        # if there are any rocks
        if len(self.rocks) > 0:

            for rock in self.rocks:
                # move the rock
                rock.move()

                # loop space
                rock.position[0] %= self.width
                rock.position[1] %= self.height

                # if the rock hits the spaceship, die once
                if distance(rock.position, self.spaceship.position) < self.death_distances[rock.size]:
                    self.dead = True

    def draw(self):
        """Update the display"""
        # everything we draw now is to a buffer that is not displayed
        self.screen.fill(self.bg_color)

        # draw the spaceship
        self.spaceship.draw_on(self.screen)

        # if there are any active missiles draw them
        if len(self.spaceship.active_missiles) > 0:
            for missile in self.spaceship.active_missiles:
                missile.draw_on(self.screen)

        # draw the rocks
        if len(self.rocks) > 0:
            for rock in self.rocks:
                rock.draw_on(self.screen)

        # create and display the text for score
        scores_text = self.medium_font.render(str(self.score), True, (0, 155, 0))
        draw_centered(scores_text, self.screen, (self.width - scores_text.get_width(), scores_text.get_height() + 10))

        # flip buffers so that everything we have drawn gets displayed
        # pygame.display.flip()
