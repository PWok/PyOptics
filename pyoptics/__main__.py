import argparse
import sys

from numpy import asarray
import pygame

import pyoptics
from pyoptics.utils import scene_from_cfg


class UIRunner:
    def __init__(self, cli_args):

        self.cli_args = cli_args

        self.initial_mouse_pos = 0, 0
        self.initial_moved_loc = asarray((0, 0))
        self.moved = None
        self.dragging = False

        pygame.init()
        self.screen = pygame.display.set_mode(tuple(cli_args.resolution))

        self.scene = self._build_scene()
        self.scene.run()

        pygame.display.flip()

    def _build_scene(self):
        if self.cli_args.config:
            return scene_from_cfg(
                self.cli_args.config,
                self.screen,
                steps=self.cli_args.steps,
                scale=self.cli_args.scale,
            )
        else:
            return pyoptics.RenderScene(
                pyoptics.OpticSystem(),
                self.screen,
                steps=self.cli_args.steps,
                scale=self.cli_args.scale,
            )

    def process_event(self, event) -> bool:
        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.KEYDOWN:
            return self.handle_keydown(event)

        # manipulating the objects
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for renderable in self.scene.object_renderers:
                if renderable.check_mouse_hover(self.scene, mouse_pos):
                    self.initial_mouse_pos = mouse_pos
                    self.initial_moved_loc = renderable.obj.location
                    self.moved = renderable
                    self.dragging = True
                    break
        # rotate      
        elif event.type == pygame.MOUSEWHEEL:
            obj = None
            mouse_pos = pygame.mouse.get_pos()
            for renderable in self.scene.object_renderers:
                if renderable.check_mouse_hover(self.scene, mouse_pos):
                    obj = renderable.obj
                    break
                
            if obj is None:
                return True
            
            obj.rotation += event.y/100

        elif event.type == pygame.MOUSEBUTTONUP:
            self.moved = None
            self.dragging = False
            self.scene.reset()
            self.scene.run()

        elif event.type == pygame.MOUSEMOTION and self.moved is not None and self.dragging:
            mouse_pos = pygame.mouse.get_pos()
            x = -self.scene.from_scene_scale(
                self.initial_mouse_pos[0] - mouse_pos[0]
            )
            y = self.scene.from_scene_scale(
                self.initial_mouse_pos[1] - mouse_pos[1]
            )

            self.moved.obj.location = self.initial_moved_loc + asarray((x, y))
            self.scene.reset()
            self.scene.run()

        return True

    def handle_keydown(self, event):
        window_loc = pygame.mouse.get_pos()
        loc = self.scene.from_scene_coords(window_loc)
        match (event.key):
            # step
            case pygame.K_RETURN | pygame.K_KP_ENTER | pygame.K_SPACE:
                self.scene.step()
                self.scene.render()
                pygame.display.flip()

                return True

            # add flat mirror
            case pygame.K_f:
                self.scene.add(pyoptics.FlatMirror(loc, 0, 1))

            # add spherical mirror
            case pygame.K_s:
                self.scene.add(pyoptics.SphericalMirror(loc, 0, 1))

            # add lens
            # case pygame.K_l:
            #     scene.add(pyoptics.Lens(loc, 0, 1, 1))

            # add emitter
            case pygame.K_e:
                self.scene.add(pyoptics.RayEmitter(loc, 0))

            # reset
            case pygame.K_r:
                del self.scene
                self.scene = self._build_scene()

            case _:
                return True

        self.scene.reset()
        self.scene.run()

        return True

    def run(self):
        self.scene.reset()
        running = True
        while running:
            for event in pygame.event.get():
                running = self.process_event(event)
                pygame.display.flip()


def main():
    # command line parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="Path to a configuration file", default=None
    )
    parser.add_argument(
        "-r",
        "--resolution",
        help="Resolution of the rendered window (width and height)",
        nargs=2,
        type=int,
        default=(600, 600),
    )
    parser.add_argument(
        "-s", "--scale", help="Scale of the simulation", type=float, default=50
    )
    parser.add_argument(
        "-S", "--steps", help="Number of steps to run", type=int, default=20
    )

    args = parser.parse_args()

    # main loop

    runner = UIRunner(args)

    runner.run()
    pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
