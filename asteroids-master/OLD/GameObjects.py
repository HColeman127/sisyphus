import math
import random


def distance(p, q):
    """Helper function to calculate distance between 2 points"""
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)


def set_random_seed(n):
    random.seed(n)


class GameObject(object):
    """All game objects have a position and an image"""
    def __init__(self, position, size, speed=0):
        # max speed should be 6.5
        self.size = size
        self.position = list(position[:])
        self.speed = speed

    def size(self):
        return max(self.size[0], self.size[1])

    def radius(self):
        return self.size[1]/2


class Spaceship(GameObject):

    velocity = [0, 0]

    def __init__(self, position):
        """initializing an Spaceship object given it's position"""
        super(Spaceship, self).__init__(position, [52, 90])

        self.direction = [0, -1]
        self.is_throttle_on = False
        self.angle = 0
        self.velocity[0] = 0
        self.velocity[1] = 0

        # a list to hold the missiles fired by the spaceship
        # (that are active (on the screen))
        self.active_missiles = []

    def move(self):
        """Do one frame's worth of updating for the object"""

        # calculate the direction from the angle variable

        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

    def fire(self):
        """create a new Missile and fire it!!"""

        # adjust the firing position of the missile based on the
        # angle of the spaceship.
        # adjust[] is used to help hold the position of the point
        # from where the missile should be fired. In other words,
        # for example missiles should be fired from the bottom of
        # the spaceship if it's facing down.
        adjust = [0, 0]
        adjust[0] = math.sin(-math.radians(self.angle)) * 52
        adjust[1] = -math.cos(math.radians(self.angle)) * 90

        # create a new missile using the calculated adjusted position
        new_missile = Missile((self.position[0] + adjust[0], self.position[1] + adjust[1] / 2), self.angle)
        self.active_missiles.append(new_missile)


class Missile(GameObject):
    """Resembles a missile"""

    lifeSpan = 0
    lifeMax = 20

    def __init__(self, position, angle, speed=15):
        super(Missile, self).__init__(position, [9, 9])

        self.angle = angle
        self.direction = [0, 0]
        self.speed = speed

    def move(self):
        """Move the missile towards its destination"""

        # calculate the direction from the angle variable
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        # calculate the position from the direction and speed
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed


class Rock(GameObject):
    """Resembles a rock"""

    def __init__(self, position, size, speed=10):
        """Initialize a Rock object, given its position and size"""

        # if the size is valid
        if size == "big":
            size_num = [150, 150]
        if size == "normal":
            size_num = [100, 100]
        if size == "small":
            size_num = [50, 50]

        # load the correct image from file
        str_filename = "rock-" + str(size) + ".png"
        super(Rock, self).__init__(position, size_num)
        self.size = size

        self.position = list(position)

        self.speed = speed

        # create a random movement direction vector
        if bool(random.getrandbits(1)):
            rand_x = random.random() * -1
        else:
            rand_x = random.random()

        if bool(random.getrandbits(1)):
            rand_y = random.random() * -1
        else:
            rand_y = random.random()

        self.direction = [rand_x, rand_y]

    def move(self):
        """Move the rock"""

        self.position[0] += self.direction[0] * self.speed * .4
        self.position[1] += self.direction[1] * self.speed * .4