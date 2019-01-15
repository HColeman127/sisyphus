from GameObjects_display import *


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


class MyGameDisplay(object):

    def __init__(self):
        # set up a 800 x 600 window
        self.width = 1200
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.death_distances = {"big": 90, "normal": 65, "small": 40}
        self.min_rock_distance = 350

        # pygame/display stuff
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        self.bg_color = 0, 0, 0
        self.big_font = pygame.font.SysFont(None, 100)
        self.medium_font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 25)
        self.lives_image = load_image_convert_alpha('spaceship-off.png')



        self.reset()


        # Setup a timer to refresh the display FPS times per second
        self.FPS = 60
        pygame.time.set_timer(pygame.USEREVENT, 1000 // self.FPS)

    def random_seed(self, seed=None):
        set_random_seed(seed)

    def reset(self):
        self.score = 0

        self.spaceship = Spaceship((self.width // 2, self.height // 2))
        self.missiles = []
        self.fire_time = 0

        self.rocks = []
        for i in range(4):
            self.make_rock()

        self.dead = False

        return True, 0, self.get_observations()


    def make_rock(self, size="big", pos=None):
        """Make a new rock"""

        # minimum margin when creating rocks
        margin = 200

        if pos == None:
            # no position was passed. make at a random location

            rand_x = random.randint(margin, self.width - margin)
            rand_y = random.randint(margin, self.height - margin)

            # while the co-ordinate is too close, discard it
            # and generate another one
            while distance((rand_x, rand_y), self.spaceship.position) < self.min_rock_distance:
                # choose another random co-ordinate
                rand_x = random.randint(0, self.width)
                rand_y = random.randint(0, self.height)

            temp_rock = Rock((rand_x, rand_y), size)

        else:
            # a position was given through arguments
            temp_rock = Rock(pos, size)

        # add the recently created rock the the actual rocks list
        self.rocks.append(temp_rock)

    def step(self, commands=(0, 0, 0, 0)):
        pygame.event.wait()


        if self.dead:
            self.reset()

        # fire
        if commands[0] == 1:
            if self.fire_time < 1:
                # print("FIRING!")
                # there should be a minimum of 0.15 delay between
                # firing each missile

                # fire a missile
                self.spaceship.fire()

                # reset the current fire time
                self.fire_time = 6
            else:
                # print("RECHARGING")
                self.fire_time -= 1
        # left
        if commands[1] == 1:
            self.spaceship.angle += 10
            self.spaceship.angle %= 360
        # right
        if commands[2] == 1:
            self.spaceship.angle -= 10
            self.spaceship.angle %= 360
        # thrust
        if commands[3] == 1:
            # increase the speed
            self.spaceship.velocity[0] += 0.5 * math.sin(-math.radians(self.spaceship.angle))
            self.spaceship.velocity[1] += 0.5 * -math.cos(math.radians(self.spaceship.angle))

            # max speed
            hypotenuse = math.sqrt(self.spaceship.velocity[0]**2 + self.spaceship.velocity[1]**2)
            if hypotenuse > 13:
                self.spaceship.velocity[0] = 13 * self.spaceship.velocity[0]/hypotenuse
                self.spaceship.velocity[1] = 13 * self.spaceship.velocity[1]/hypotenuse


        # if there are any missiles on the screen, process them
        if len(self.spaceship.active_missiles) > 0:
            self.missiles_physics()

        # if there are any rocks, do their physics
        if len(self.rocks) > 0:
            self.rocks_physics()

        # do the spaceship physics
        self.physics()

        # draw everything
        self.draw()

        # return
        # bool: still playing, int: score, int: velocity x, int: velocity y, int: pointing angle
        return not self.dead, self.score, self.get_observations()

    def get_observations(self):
        return [self.spaceship.velocity[0], self.spaceship.velocity[1], self.spaceship.angle] + self.get_closest_rocks(4)

    def get_closest_rocks(self, num):
        # distances of all rocks
        distances = [distance(rock.position, self.spaceship.position) for rock in self.rocks]

        # get <num> closest rocks
        rock_indices = []
        for _ in range(min(num, len(distances))):
            min_index = 0
            for i in range(len(distances)):
                if min_index in rock_indices or distances[i] < distances[min_index] and i not in rock_indices:
                    min_index = i
            rock_indices.append(min_index)

        # construct list where xi, yi is the x and y distance of the spaceship to rock i
        # of shape [xi1, yi1, xi2, yi2, xi3, yi3, xi4, yi4]
        observations = []
        for rock_index in rock_indices:
            observations.append(self.rocks[rock_index].position[0] - self.spaceship.position[0])
            observations.append(self.rocks[rock_index].position[1] - self.spaceship.position[1])

        # if there are less than <num> rocks add max distances
        for _ in range(num - len(rock_indices)):
            observations.append(self.width)
            observations.append(self.height)

        return observations

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
                            self.score += 20

                    elif rock.size == "normal":
                        # if the missile hits a medium sized rock, destroy it,
                        # make two small sized rocks and give 50 scores
                        if distance(missile.position, rock.position) < 55:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("small", (rock.position[0] + 10, rock.position[1]))
                            self.make_rock("small", (rock.position[0] - 10, rock.position[1]))
                            self.score += 50
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

                            self.score += 100

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
        pygame.display.flip()