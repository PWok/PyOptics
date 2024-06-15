import argparse

import pygame
from pyoptics.renderer import *
from pyoptics.optics2d import *

from pyoptics.utils import scene_from_cfg


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Path to a configuration file", default=None)
parser.add_argument(
    "-r",
    "--resolution",
    help="Resolution of the rendered window",
    nargs=2,
    type=int,
    default=(600, 600),
)
parser.add_argument(
    "-s", "--scale", help="Scale of the simulation", type=float, default=40
)

args = parser.parse_args()


pygame.init()
screen = pygame.display.set_mode(tuple(args.resolution))
screen.fill((255, 255, 255))

if args.config:
    scene = scene_from_cfg(args.config, screen, steps=10, scale=args.scale)
else:
    scene = RenderScene(OpticSystem(), screen, steps=10, scale=args.scale)

scene.run()

pygame.display.flip()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            window_loc = pygame.mouse.get_pos()
            loc = scene.from_scene_coords(window_loc)
            match (event.key):
                # step
                case pygame.K_RETURN | pygame.K_KP_ENTER | pygame.K_SPACE:
                    scene.step()
                    scene.render()
                    pygame.display.flip()

                    continue

                # add flat mirror
                case pygame.K_f:
                    scene.add(FlatMirror(loc, 0, 1))

                # add spherical mirror
                case pygame.K_s:
                    scene.add(SphericalMirror(loc, 0, 1))

                # add lens
                case pygame.K_l:
                    scene.add(Lens(loc, 0, 1))

                case pygame.K_r | pygame.K_e:
                    scene.add(RayEmitter(loc, 0))

            scene.reset()
            scene.run()
            pygame.display.flip()
