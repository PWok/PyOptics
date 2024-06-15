import pygame
from pyoptics.renderer import *


pygame.init()
screen = pygame.display.set_mode((600, 600))

running = True

screen.fill((255, 255, 255))


optics = [
        FlatMirror((4, 0), -pi/8, 1),
        FlatMirror((0, 5), pi/2, 10),
        FlatMirror((-2.5, 1.75), -pi/6, 2),
        FlatMirror((0, -5), pi/2, 10),
        FlatMirror((5, 0), 0, 10),
        FlatMirror((-5, 0), 0, 10),
        SphericalMirror((3, 0), 0, 2, 0.25),
        SphericalMirror((-3, 0), 0, 2, 1),
]
rays = [RayEmitter((0, 0), pi/117)]

system = OpticSystem(optics, rays)

scene = RenderScene(system, screen)

scene.run(1)

pygame.display.flip()



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key==pygame.K_RETURN or pygame.K_KP_ENTER or pygame.K_SPACE:
                scene.step()
                scene.render()
                pygame.display.flip()
