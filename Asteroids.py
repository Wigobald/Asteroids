import pygame
import math
import random


class SpaceBody:
    def __init__(self):
        self.position = []
        self.speed = []
        self.size = 0.0
        self.rotation_speed = 0.0
        self.angle = 0.0
        # each point is defined as an offset from the center of the body
        self.pointsOffset = []
        self.points = []
        self.line_width = 1
        self.color = "white"

    def __str__(self):
        return (f"Position:[X:{self.position[0]},Y:{self.position[1]}],"
                f"Speed:{self.speed},Angle:{self.angle}")

    def update(self, game_screen: pygame.Surface, delta: float):
        """
        Run every frame.
        :param game_screen:
        :param delta:
        :return:
        """
        self.move(game_screen, delta)
        self.wrapBody(game_screen)
        self.drawModel(self.points, game_screen)
        self.wrapModel(game_screen)

    def move(self, game_screen: pygame.Surface, delta: float):
        self.position[0] += self.speed[0] * delta
        self.position[1] += self.speed[1] * delta
        self.updatePointsRealSpace()

    def wrapBody(self, game_screen):
        """
        Updates body position to wrap around the screen.
        :param game_screen:
        :return:
        """
        # horizontally
        if self.position[0] > game_screen.get_width():
            self.position[0] = 0
        if self.position[0] < 0:
            self.position[0] = game_screen.get_width()
        # vertically
        if self.position[1] > game_screen.get_height():
            self.position[1] = 0
        if self.position[1] < 0:
            self.position[1] = game_screen.get_height()

    def rotateModel(self, direction: int, delta: float):
        """
        Rotates every point that defines the model
        :param direction:
        :param delta:
        :return:
        """
        theta = direction * delta * self.rotation_speed
        for point in self.pointsOffset:
            temp = (point[0] * math.cos(theta)) - (point[1] * math.sin(theta))
            point[1] = (point[0] * math.sin(theta)) + (point[1] * math.cos(theta))
            point[0] = temp
        self.angle += theta
        if self.angle > math.tau or self.angle < 0:
            self.angle += -math.tau * sign(self.angle)
        self.updatePointsRealSpace()

    def updatePointsRealSpace(self):
        """
        Updates pointsRealSpace by adding pointsOffset to the model position.
        Should be called everytime the model is moved or rotated.
        :return:
        """
        for i in range(len(self.pointsOffset)):
            self.points[i] = [self.position[0] + self.pointsOffset[i][0], self.position[1] + self.pointsOffset[i][1]]

    def drawModel(self, points: list, game_screen: pygame.Surface, closed: bool = True):
        """
        Draws a shape defined by any number of points, by way of lines.
        Every point will be connected with a line to it's following point in the list of points.
        If closed is False, the last and first points will not be connected.
        :param points:
        :param game_screen:
        :param closed:
        :return:
        """
        for i in range(len(points) - 1):
            pygame.draw.line(game_screen, self.color, points[i], points[i + 1], self.line_width)
        if closed:
            pygame.draw.line(game_screen, self.color, points[-1], points[0], self.line_width)

    def wrapModel(self, game_screen: pygame.Surface):
        """
        Drawas additional models to achieve a seamless wrap-around effect.
        :param game_screen:
        :return:
        """
        w = game_screen.get_width()
        h = game_screen.get_height()
        newPoints = self.points
        # horizontally
        if self.position[0] + self.size > game_screen.get_width() - 10:
            for i in range(len(self.points)):
                newPoints[i] = [self.points[i][0] - w, self.points[i][1]]
            self.drawModel(newPoints, game_screen)
        if self.position[0] - self.size < 10:
            for i in range(len(self.points)):
                newPoints[i] = [self.points[i][0] + w, self.points[i][1]]
            self.drawModel(newPoints, game_screen)
        # vertically
        if self.position[1] + self.size > game_screen.get_height() - 10:
            for i in range(len(self.points)):
                newPoints[i] = [self.points[i][0], self.points[i][1] - h]
            self.drawModel(newPoints, game_screen)
        if self.position[1] - self.size < 10:
            for i in range(len(self.points)):
                newPoints[i] = [self.points[i][0], self.points[i][1] + h]
            self.drawModel(newPoints, game_screen)


class Ship(SpaceBody):
    def __init__(self, position: list, acceleration: float, rotation_speed: float, size: float, color: str = "white",
                 line_width: int = 1):
        super().__init__()
        self.position = position
        self.acceleration = acceleration
        self.speed = [0.0, 0.0]
        self.rotation_speed = rotation_speed
        self.size = size
        self.color = color
        self.line_width = line_width
        self.angle = 0
        self.pointsOffset = [
            [0.0, -size],
            [-(size / 2), (size / 2)],
            [0.0, (size / 3)],
            [(size / 2), (size / 2)],
        ]
        self.points = []
        for i in range(len(self.pointsOffset)):
            self.points.append([])
        self.updatePointsRealSpace()

    def move(self, game_screen, delta: float):
        self.position[0] += self.speed[0] * delta + (self.acceleration * delta ** 2 * 0.5)
        self.position[1] += self.speed[1] * delta + (self.acceleration * delta ** 2 * 0.5)
        self.updatePointsRealSpace()

    def thrust(self, delta: float):
        """
        Adds speed in the direction the ship is pointing.
        :param delta:
        :return:
        """
        self.speed[0] += self.acceleration * math.sin(self.angle) * delta
        self.speed[1] -= self.acceleration * math.cos(self.angle) * delta

    def shoot(self, speed: float):
        """
        Returns a Bullet object with speed in the direction the ship is pointing, on the nose of the ship.
        :param speed:
        :return:
        """
        return Bullet(self.points[0], scaleVector(rotateVector([0, -1], self.angle), speed))


class Asteroid(SpaceBody):
    def __init__(self, position: list, speed: list, max_rotation_speed: float = 1.5, size: float = 100,
                 color: str = "white", line_width: int = 1):
        super().__init__()
        self.position = position
        self.speed = speed
        self.rotation_speed = random.random() * max_rotation_speed
        self.rotation_direction = random.choice([-1, 1])
        self.acceleration = 1
        self.size = size
        self.hp = int(size / 20)
        self.color = color
        self.line_width = line_width
        self.angle = 0
        self.pointsOffset = []
        self.points = []
        pointAmount = random.randint(int(size / 10), int(size / 6))
        for i in range(pointAmount):
            self.pointsOffset.append([])
            self.points.append([])
            # populate random offset points
            self.pointsOffset[i] = scaleVector(rotateVector([0, 1], i * (math.tau / pointAmount)),
                                               random.randint(int(size / 2), int(size)))
        self.updatePointsRealSpace()

    def update(self, game_screen: pygame.Surface, delta: float):
        self.move(game_screen, delta)
        self.wrapBody(game_screen)
        self.rotateModel(self.rotation_direction, delta)
        self.drawModel(self.points, game_screen)
        self.wrapModel(game_screen)

    def hit(self):
        """
        Reduces health points by one.
        :return:
        """
        self.hp -= 1


class Bullet(SpaceBody):
    def __init__(self, position: list, speed: list, size: int = 1, color: str = "white"):
        super().__init__()
        self.position = position
        self.speed = speed
        self.size = size
        self.color = color

    def update(self, game_screen: pygame.Surface, delta: float):
        self.move(game_screen, delta)
        self.draw(game_screen)

    def draw(self, game_screen: pygame.Surface):
        pygame.draw.circle(game_screen, self.color, self.position, self.size)


def rotateVector(vector: list, angle: float) -> list[float]:
    return [(vector[0] * math.cos(angle)) - (vector[1] * math.sin(angle)),
            (vector[0] * math.sin(angle)) + (vector[1] * math.cos(angle))]


def normalizeVector(vector: list) -> list[float]:
    """
    Will raise an exepction for a null vector.
    :param vector:
    :return:
    """
    norm = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    if norm != 0:
        return [vector[0] / norm, vector[1] / norm]
    else:
        raise Exception("Dividing by zero.")


def scaleVector(vector: list, scalar: float) -> list[float]:
    return [vector[0] * scalar, vector[1] * scalar]


def distance(point1: list, point2: list, game_screen: pygame.Surface):
    """
    Returns distance between two points, accounting for screen-wrap.
    :param game_screen:
    :param point1:
    :param point2:
    :return:
    """
    distanceX = min(point2[0] - point1[0], (point1[0]) + game_screen.get_width() - point2[0])
    distanceY = min(point2[1] - point1[1], (point1[1]) + game_screen.get_height() - point2[1])
    return math.sqrt((distanceX ** 2) + (distanceY ** 2))


def sign(x: float) -> int:
    if x >= 0:
        return 1
    else:
        return -1


SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
# pygame setup
pygame.init()
pygame.display.set_caption("Asteroids")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
cooldown_tracker = 0
running = True
dt = 0

while running:
    reset = False
    random.seed()
    asteroids = [Asteroid([SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4],
                          [(random.random() - 0.5) * 100, (random.random() - 0.5) * 100]),
                 Asteroid([SCREEN_WIDTH - SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4],
                          [(random.random() - 0.5) * 100, (random.random() - 0.5) * 100])]
    ship = Ship([SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2], 200, 7, 25)
    bullets = []
    while not reset:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                reset = True
        # game state input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
            reset = True
        if keys[pygame.K_r]:
            reset = True
        if keys[pygame.K_l]:
            for a in asteroids:
                print(a.speed)
        # draw frame
        screen.fill("black")
        # player state inputs and updates
        try:
            # ship input
            if keys[pygame.K_w]:
                ship.thrust(dt)
            if keys[pygame.K_a]:
                ship.rotateModel(-1, dt)
            if keys[pygame.K_d]:
                ship.rotateModel(1, dt)
            if keys[pygame.K_SPACE]:
                cooldown_tracker += clock.get_time()
                if cooldown_tracker > 400:
                    bullets.append(ship.shoot(500))
                    cooldown_tracker = 0
            # ship update
            ship.update(screen, dt)
            # check collisions (not really)
            for a in asteroids:
                if distance(ship.position, a.position, screen) < ship.size + a.size - 50:
                    del ship
                for b in bullets:
                    if distance(a.position, b.position, screen) < a.size:
                        a.hit()
                        bullets.remove(b)
                        del b
        except NameError:
            # ship got deleted
            pass
        # update asteroids
        for a in asteroids:
            # destroy asteroids
            if a.hp <= 0:
                if a.size > 50:
                    asteroids.append(Asteroid([a.position[0] - 30, a.position[1]], scaleVector(a.speed, 4),
                                              a.rotation_speed * 2, a.size / 2))
                    asteroids.append(Asteroid([a.position[0] + 30, a.position[1]], scaleVector(a.speed, -4),
                                              a.rotation_speed * 2, a.size / 2))
                asteroids.remove(a)
                del a
                break
            a.update(screen, dt)
        # respawn asteroids
        if len(asteroids) == 0:
            asteroids = [Asteroid([ship.position[0] + SCREEN_WIDTH / 4,
                                   ship.position[1] + random.randint(-100, 100)],
                                  [(random.random() - 0.5) * 100, (random.random() - 0.5) * 100]),
                         Asteroid([ship.position[0] - SCREEN_WIDTH / 4,
                                   ship.position[1] + random.randint(-100, 100)],
                                  [(random.random() - 0.5) * 100, (random.random() - 0.5) * 100])]
        # update bullets
        for b in bullets:
            b.update(screen, dt)
        # render
        pygame.display.flip()
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick() / 1000

# quit the game
pygame.quit()
