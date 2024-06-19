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
    help="Resolution of the rendered window (width and height)",
    nargs=2,
    type=int,
    default=(600, 600),
)
parser.add_argument(
    "-s", "--scale", help="Scale of the simulation", type=float, default=40
)
parser.add_argument(
    "-S", "--steps", help="Number of steps to run", type=int, default=20
)

args = parser.parse_args()


pygame.init()
screen = pygame.display.set_mode(tuple(args.resolution))
screen.fill((255, 255, 255))

if args.config:
    scene = scene_from_cfg(args.config, screen, steps=args.steps, scale=args.scale)
else:
    scene = RenderScene(OpticSystem(), screen, steps=args.steps, scale=args.scale)

scene.run()

pygame.display.flip()



# TODO: zmienne globalne... trzeba to przerobić
moved = None
dragging = False

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

                # add emitter
                case pygame.K_e:
                    scene.add(RayEmitter(loc, 0))
                
                # reset
                case pygame.K_r:
                    del scene
                    if args.config:
                        scene = scene_from_cfg(args.config, screen, steps=args.steps, scale=args.scale)
                    else:
                        scene = RenderScene(OpticSystem(), screen, steps=args.steps, scale=args.scale)
                
                case _:
                    continue   

            scene.reset()
            scene.run()
            
        
        # manipulating the objects
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # get mouse position
            mouse_pos = pygame.mouse.get_pos()
            # get first object that this collides with
            for renderable in scene.object_renderers:
                if renderable.check_mouse_hover(scene, mouse_pos):
                    moved = renderable
                    dragging = True
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            moved = None
            dragging = False
            scene.run()
            
        elif event.type == pygame.MOUSEMOTION:
            if moved is not None and dragging:
                movement = pygame.mouse.get_rel()
                
                old_pos = scene.to_scene_coords(moved.obj.location)
                new_pos = scene.from_scene_coords((old_pos[0] + movement[0], old_pos[1]+movement[1]))
                moved.obj.location = new_pos
                
                scene.render()
        
        
    pygame.display.flip()