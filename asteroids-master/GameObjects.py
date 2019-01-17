import math
import os
import random
import pygame


def set_random_seed(n):
    random.seed(n)


def load_image_convert_alpha(filename):
    """Load an image with the given filename from the images directory"""
    return pygame.image.load(os.path.join('images', filename)).convert_alpha()


def load_sound(filename):
    """Load a sound with the given filename from the sounds directory"""
    return pygame.mixer.Sound(os.path.join('sounds', filename))


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


class GameObject(object):
    """All game objects have a position and an image"""
    def __init__(self, position, image=None, speed=0, display=None):
        # max speed should be 6.5
        self.image = image
        self.position = list(position[:])
        self.speed = speed
        self.display = display

    def draw_on(self, screen):
        draw_centered(self.image, screen, self.position)

    def size(self):
        return max(self.image.get_height(), self.image.get_width())

    def radius(self):
        return self.image.get_width()/2


class Spaceship(GameObject):

    velocity = [0, 0]

    def __init__(self, position, display):
        """initializing an Spaceship object given it's position"""
        if display:
            super(Spaceship, self).__init__(position, load_image_convert_alpha('spaceship-off.png'), display=True)
        else:
            super(Spaceship, self).__init__(position, display=False)

        if self.display:
            self.image_on = load_image_convert_alpha('spaceship-on.png')
        self.direction = [0, -1]
        self.is_throttle_on = False
        self.angle = 0
        self.velocity[0] = 0
        self.velocity[1] = 0

        # a list to hold the missiles fired by the spaceship
        # (that are active (on the screen))
        self.active_missiles = []

    def draw_on(self, screen):
        """Draw the spaceship on the screen"""

        # select the image, based on the fact that spaceship is accelerating
        # or not
        if self.is_throttle_on:
            new_image, rect = rotate_center(self.image_on, self.image_on.get_rect(), self.angle)
        else:
            new_image, rect = rotate_center(self.image, self.image.get_rect(), self.angle)

        draw_centered(new_image, screen, self.position)

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
        new_missile = Missile((self.position[0] + adjust[0], self.position[1] + adjust[1] / 2),
                              self.angle, display=self.display)
        self.active_missiles.append(new_missile)


class Missile(GameObject):
    """Resembles a missile"""

    lifeSpan = 0
    lifeMax = 20

    def __init__(self, position, angle, speed=15, display=None):
        if display:
            super(Missile, self).__init__(position, load_image_convert_alpha('missile.png'), display=True)
        else:
            super(Missile, self).__init__(position, display=False)

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

    def __init__(self, position, size, speed=10, display=None):
        """Initialize a Rock object, given its position and size"""

        # if the size is valid
        if size in {"big", "normal", "small"}:

            # load the correct image from file
            str_filename = "rock-" + str(size) + ".png"
            if display:
                super(Rock, self).__init__(position, load_image_convert_alpha(str_filename), display=True)
            else:
                super(Rock, self).__init__(position, display=False)

            self.size = size

        else:
            # the size is not pre-defined
            return None

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
