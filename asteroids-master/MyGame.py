from __future__ import division
from GameObjects import *


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
        return rotate_image,rotate_rect


def distance(p, q):
    """Helper function to calculate distance between 2 points"""
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)


class MyGame(object):

    # defining and initializing game states
    PLAYING, GAME_OVER, STARTING = range(3)

    # defining custom events
    REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT + 3)

    def __init__(self):
        """Initialize a new game"""
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        # set up a 800 x 600 window
        self.width = 1200
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))

        # use a black background
        self.bg_color = 0, 0, 0

        # get the default system font (with different sizes of 100, 50, 25)
        self.big_font = pygame.font.SysFont(None, 100)
        self.medium_font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 25)

        # load a spaceship image (only used to display number of lives)
        self.lives_image = load_image_convert_alpha('spaceship-off.png')

        # Setup a timer to refresh the display FPS times per second
        self.FPS = 30
        pygame.time.set_timer(self.REFRESH, 1000 // self.FPS)

        # a dictionary of death distances of different rock sizes
        self.death_distances = {"big": 90, "normal": 65, "small": 40}

        # display the welcome screen
        # self.do_welcome()
        self.do_init()
        self.start()
        # used to monitor missile firing time
        # to prevent firing too many missiles in a short time
        self.fire_time = 0

    def do_init(self):
        """This function is called in the beginning or when
        the game is restarted."""

        # holds the rocks
        self.rocks = []

        # minimum distance from spaceship when making rocks
        # this changes based on difficulty as the time passes
        self.min_rock_distance = 350

        # starting the game
        self.start()


        # create 4 big rocks
        for i in range(4):
            self.make_rock()

        # initialize the number of lives and the score
        self.score = 0

        # counter used to help count seconds
        self.counter = 0


    def start(self):
        """Start the game by creating the spaceship object"""
        self.spaceship = Spaceship((self.width // 2, self.height // 2))
        self.missiles = []

        # set the state to PLAYING
        self.state = MyGame.PLAYING

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
            while distance((rand_x, rand_y), self.spaceship.position) < \
                    self.min_rock_distance:
                # choose another random co-ordinate
                rand_x = random.randint(0, self.width)
                rand_y = random.randint(0, self.height)

            temp_rock = Rock((rand_x, rand_y), size)

        else:
            # a position was given through arguments
            temp_rock = Rock(pos, size)

        # add the recently created rock the the actual rocks list
        self.rocks.append(temp_rock)


    # command[0] is the shoot command
    # command[1] is the left command
    # command[2] is the right command
    # command[3] is the throttle command
    def step(self, commands):

        if commands[0] == 1:
            if self.fire_time < 1:
                # there should be a minimum of 0.15 delay between
                # firing each missile

                # fire a missile
                self.spaceship.fire()

                # reset the current fire time
                self.fire_time = 6
            else:
                self.fire_time -= 1

        # ----------- the big kahuna --------------
        if self.state == MyGame.PLAYING:
            # if the game is going on

            if commands[2] == 1:
                self.spaceship.angle -= 10
                self.spaceship.angle %= 360

            if commands[1] == 1:
                self.spaceship.angle += 10
                self.spaceship.angle %= 360

            if commands[4] == 1:
                # if "w" or "up arrow" is pressed,
                # we should accelerate
                self.spaceship.is_throttle_on = True

                # increase the speed
                self.spaceship.velocity[0] += 0.5 * math.sin(-math.radians(self.spaceship.angle))
                self.spaceship.velocity[1] += 0.5 * -math.cos(math.radians(self.spaceship.angle))

                if self.spaceship.velocity[0] > 9:
                    self.spaceship.velocity[0] = 9
                elif self.spaceship.velocity[0] < -9:
                    self.spaceship.velocity[0] = -9
                if self.spaceship.velocity[1] > 9:
                    self.spaceship.velocity[1] = 9
                elif self.spaceship.velocity[1] < -9:
                    self.spaceship.velocity[1] = -9


            else:
                # if the throttle key ("d" or "up")
                # is not pressed, slow down
                if self.spaceship.speed > 0:
                    self.spaceship.velocity[0] -= 0.1
                    self.spaceship.velocity[1] -= 0.1
                self.spaceship.is_throttle_on = False

            # if there are any missiles on the screen, process them
            if len(self.spaceship.active_missiles) > 0:
                self.missiles_physics()

            # if there are any rocks, do their physics
            if len(self.rocks) > 0:
                self.rocks_physics()

            # do the spaceship physics
            self.physics()

            # --------- end of great turkey ------------

        # draw everything
        self.draw()  ## <--- the big money right here to toggle display output.
        print("step")

    """
    def run(self):
        running = True
        while running:
            event = pygame.event.wait()

            # player is asking to quit
            if event.type == pygame.QUIT:
                running = False
                print("quit")

            # time to draw a new frame
            elif event.type == MyGame.REFRESH:

                keys = pygame.key.get_pressed()

                if keys[pygame.K_SPACE]:
                    if self.fire_time < 1:
                        # there should be a minimum of 0.15 delay between
                        # firing each missile

                        # fire a missile
                        self.spaceship.fire()

                        # reset the current fire time
                        self.fire_time = 6
                    else:
                        self.fire_time -= 1

                # ----------- the big kahuna --------------
                if self.state == MyGame.PLAYING:
                    # if the game is going on

                    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        # when pressing "d" or "right arrow" rotate
                        # the spaceship clockwise by 10 degrees
                        self.spaceship.angle -= 10
                        self.spaceship.angle %= 360

                    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        # when pressing "d" or "right arrow" rotate
                        # the spaceship counter clockwise by 10 degrees
                        self.spaceship.angle += 10
                        self.spaceship.angle %= 360

                    if keys[pygame.K_UP] or keys[pygame.K_w]:
                        # if "w" or "up arrow" is pressed,
                        # we should accelerate
                        self.spaceship.is_throttle_on = True

                        # increase the speed
                        self.spaceship.velocity[0] += 0.5 * math.sin(-math.radians(self.spaceship.angle))
                        self.spaceship.velocity[1] += 0.5 * -math.cos(math.radians(self.spaceship.angle))

                        if self.spaceship.velocity[0] > 9:
                            self.spaceship.velocity[0] = 9
                        elif self.spaceship.velocity[0] < -9:
                            self.spaceship.velocity[0] = -9
                        if self.spaceship.velocity[1] > 9:
                            self.spaceship.velocity[1] = 9
                        elif self.spaceship.velocity[1] < -9:
                            self.spaceship.velocity[1] = -9


                    else:
                        # if the throttle key ("d" or "up")
                        # is not pressed, slow down
                        if self.spaceship.speed > 0:
                            self.spaceship.velocity[0] -= 0.1
                            self.spaceship.velocity[1] -= 0.1
                        self.spaceship.is_throttle_on = False

                    # if there are any missiles on the screen, process them
                    if len(self.spaceship.active_missiles) > 0:
                        self.missiles_physics()

                    # if there are any rocks, do their physics
                    if len(self.rocks) > 0:
                        self.rocks_physics()

                    # do the spaceship physics
                    self.physics()

                    # --------- end of great turkey ------------

                # draw everything
                self.draw() ## <--- the big money right here to toggle display output.
                # print("step")

            # resume after losing a life
            elif event.type == MyGame.START:
                pygame.time.set_timer(MyGame.START, 0)  # turn the timer off
                if self.lives < 1:
                    self.game_over()
                else:
                    self.rocks = []
                    # make 4 rocks
                    for i in range(4):
                        self.make_rock()
                    # start again
                    self.start()
                print("lost life,", self.lives, "remaining")

            # switch from game over screen to new game
            elif event.type == MyGame.RESTART:
                pygame.time.set_timer(MyGame.RESTART, 0)  # turn the timer off
                self.state = MyGame.STARTING
                print("game is over")

            # start a new game
                self.do_init()

            else:
                pass  # an event type we don't handle
        """

    def game_over(self):
        """Losing a life"""
        self.state = MyGame.GAME_OVER
        pygame.time.set_timer(MyGame.RESTART, 1)

    def die(self):
        self.spaceship.velocity[0] = 0
        self.spaceship.velocity[1] = 0
        pygame.time.set_timer(MyGame.START, 1)

    def physics(self):
        """Do spaceship physics here"""

        if self.state == MyGame.PLAYING:
            # call the move function of the object
            self.spaceship.move()

            if self.spaceship.position[0] < 0:
                self.spaceship.position[0] = self.width
            elif self.spaceship.position[0] > self.width:
                self.spaceship.position[0] = 0

            if self.spaceship.position[1] < 0:
                self.spaceship.position[1] = self.height
            elif self.spaceship.position[1] > self.height:
                self.spaceship.position[1] = 0

            """Note that this is a good place to make the spaceship
            bounce for example, when it hits the walls (sides of screen)
            or make it not move out of screen when it reaches the borders.
            Due to lack of time, I can't implement any of them, but they are
            not hard to do at all."""

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

                if missile.position[0] < 0:
                    missile.position[0] = self.width
                elif missile.position[0] > self.width:
                    missile.position[0] = 0

                if missile.position[1] < 0:
                    missile.position[1] = self.height
                elif missile.position[1] > self.height:
                    missile.position[1] = 0

                # check the collision with each rock
                for rock in self.rocks:


                    if rock.size == "big":
                        # if the missile hits a big rock, destroy it,
                        # make two medium sized rocks and give 20 scores
                        if distance(missile.position, rock.position) < 80:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("normal", \
                                           (rock.position[0] + 10, rock.position[1]))
                            self.make_rock("normal", \
                                           (rock.position[0] - 10, rock.position[1]))
                            self.score += 20

                    elif rock.size == "normal":
                        # if the missile hits a medium sized rock, destroy it,
                        # make two small sized rocks and give 50 scores
                        if distance(missile.position, rock.position) < 55:
                            self.rocks.remove(rock)
                            if missile in self.spaceship.active_missiles:
                                self.spaceship.active_missiles.remove(missile)
                            self.make_rock("small", \
                                           (rock.position[0] + 10, rock.position[1]))
                            self.make_rock("small", \
                                           (rock.position[0] - 10, rock.position[1]))
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

                if rock.position[0] < 0:
                    rock.position[0] = self.width
                elif rock.position[0] > self.width:
                    rock.position[0] = 0

                if rock.position[1] < 0:
                    rock.position[1] = self.height
                elif rock.position[1] > self.height:
                    rock.position[1] = 0

                # if the rock hits the spaceship, die once
                if distance(rock.position, self.spaceship.position) < \
                        self.death_distances[rock.size]:
                    self.die()

                # if the rock goes out of screen and there are less than
                # 10 rocks on the screen, create a new rock with the same size
                elif distance(rock.position, (self.width / 2, self.height / 2)) > \
                        math.sqrt((self.width / 2) ** 2 + (self.height / 2) ** 2):

                    #self.rocks.remove(rock)
                    if len(self.rocks) < 10:
                        self.make_rock(rock.size)

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

        # if we are in game play mode
        if self.state == MyGame.PLAYING:

            # increment the counter by 1
            self.counter += 1

            if self.counter == 20 * self.FPS:
                # time to increase difficulty (20 secs without dying)

                if len(self.rocks) < 15:  # keeping it sane
                    # add a new rock
                    self.make_rock()

                # decrease the minimum rock creation distance
                if self.min_rock_distance < 200:
                    self.min_rock_distance -= 50

                # set the counter back to zero
                self.counter = 0

        # create and display the text for score
        scores_text = self.medium_font.render(str(self.score), \
                                              True, (0, 155, 0))
        draw_centered(scores_text, self.screen, \
                      (self.width - scores_text.get_width(), scores_text.get_height() + \
                       10))

        # if the game is over, display the game over text
        if self.state == MyGame.GAME_OVER or self.state == MyGame.STARTING:
            draw_centered(self.gameover_text, self.screen, \
                          (self.width // 2, self.height // 2))


        # flip buffers so that everything we have drawn gets displayed
        pygame.display.flip()
