from math import asin, cos, radians, sin

import pygame


class Shape:
    def __init__(self, optics_object) -> None:
        pass


pygame.init()
screen = pygame.display.set_mode((400, 600))
running = True

screen.fill((255, 255, 255))
pygame.draw.polygon(
    screen,
    (0, 200, 250),
    ((100, 100), (200, 100), (200, 200), (300, 200), (300, 300), (100, 300)),
    2,
)

FOCAL = 0.25
LOCATION = (200, 300)
pygame.draw.circle(screen, (0, 0, 0), LOCATION, 5)
RADIUS = FOCAL * 2
ROTATION = radians(180)
SIZE = 1

ABS_RADIUS = abs(RADIUS)

PYGAME_SCALE = 100

SCALING = PYGAME_SCALE * SIZE

pygame.draw.arc(
    screen,
    (200, 0, 0),
    pygame.Rect(
        LOCATION[0] - RADIUS * (SCALING * cos(ROTATION)) - SCALING * ABS_RADIUS,
        LOCATION[1] - RADIUS * (SCALING * sin(ROTATION)) - SCALING * ABS_RADIUS,
        ABS_RADIUS * 2 * SCALING,
        ABS_RADIUS * 2 * SCALING,
    ),
    -asin(0.5 / (SIZE * RADIUS)) - ROTATION,
    asin(0.5 / (SIZE * RADIUS)) - ROTATION,
)
pygame.display.flip()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
