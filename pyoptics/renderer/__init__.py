from abc import ABC, abstractmethod
from math import asin, cos, sin, dist


import numpy as np
import pygame

from ..optics2d import *

__all__ = [
    "Renderable",
    "RenderRay",
    "RenderFlat",
    "RenderSpherical",
    "RenderLens",
    "RenderScene",
]

STEEL = pygame.Color("#99a3a3")
RED = pygame.Color("#c70e20")
BLUE = pygame.Color("#23acc4")

BACKGROUND_COLOR = pygame.Color("#000000")

STEPS = 20

PYGAME_SCALE = 40
PYGAME_MIDDLE_OFFSET = (300, 300)

DEFAULT_LINE_WIDTH = 1


class Renderable(ABC):
    def __init__(self, obj, color=BLUE, width=DEFAULT_LINE_WIDTH) -> None:
        self.obj: Optic | RayEmitter = obj
        self.color = color
        self.linewidth = width

    @abstractmethod
    def render(self, scene: "RenderScene") -> None:
        raise NotImplementedError

    @abstractmethod
    def check_mouse_hover(
        self, scene: "RenderScene", mouse_pos: tuple[int, int]
    ) -> bool:
        """Return whether the mouse hovers over this object"""
        raise NotImplementedError


class RenderRay(Renderable):
    def __init__(
        self, obj: RayEmitter, color=STEEL, ray_color=RED, ray_width=2
    ) -> None:
        self.obj: RayEmitter
        super().__init__(obj, color)
        self.ray_color = ray_color
        self.ray_width = ray_width

    def render(self, scene: "RenderScene"):
        loc = tuple(scene.to_scene_coords(self.obj.location))
        points = [loc] + list(
            map(
                lambda x: tuple(scene.to_scene_coords(x)),
                self.obj.bounce_locations + [self.obj.current_ray_location],
            )
        )
        pygame.draw.circle(scene.scr, self.color, loc, scene.scale / 10)
        if len(points) >= 2:
            pygame.draw.lines(scene.scr, self.ray_color, False, points, self.ray_width)

    def check_mouse_hover(
        self, scene: "RenderScene", mouse_pos: tuple[int, int]
    ) -> bool:
        return dist(self.obj.location, scene.from_scene_coords(mouse_pos)) <= 0.1


class RenderFlat(Renderable):

    def __calculate_vec(self) -> VecArg:
        self.obj: FlatMirror
        ang = self.obj.rotation
        scale = self.obj.scale / 2
        return np.asarray((cos(ang) * scale, sin(ang) * scale))

    def render(self, scene: "RenderScene"):
        loc = self.obj.location
        vec = self.__calculate_vec()

        start = scene.to_scene_coords(loc + vec)
        end = scene.to_scene_coords(loc - vec)

        pygame.draw.line(
            scene.scr, self.color, tuple(start), tuple(end), width=self.linewidth
        )

    def check_mouse_hover(
        self, scene: "RenderScene", mouse_pos: tuple[int, int]
    ) -> bool:

        vec = self.__calculate_vec()
        mv = scene.from_scene_coords(mouse_pos) - self.obj.location

        distance = dist(self.obj.location, scene.from_scene_coords(mouse_pos))

        direction_diff = abs(np.dot(vec, mv) / np.linalg.norm(mv) / self.obj.scale) * 2

        return (
            distance <= self.obj.scale / 2 and direction_diff > 0.96
        ) or distance <= self.obj.scale / 20


class RenderSpherical(Renderable):
    def render(self, scene: "RenderScene"):
        self.obj: SphericalMirror
        rot = -self.obj.rotation
        chord = self.obj.scale

        radius = self.obj.focal * 2

        vec = (
            scene.to_scene_scale(-radius * cos(rot) - radius),
            scene.to_scene_scale(-radius * sin(rot) - radius),
        )

        loc = scene.to_scene_coords(self.obj.location) + vec

        pygame.draw.arc(
            scene.scr,
            self.color,
            pygame.Rect(
                loc[0],
                loc[1],
                scene.to_scene_scale(2 * radius),
                scene.to_scene_scale(2 * radius),
            ),
            -asin(chord / radius / 2) - rot,
            asin(chord / radius / 2) - rot,
            width=self.linewidth,
        )

    def check_mouse_hover(
        self, scene: "RenderScene", mouse_pos: tuple[int, int]
    ) -> bool:
        return (
            dist(self.obj.location, scene.from_scene_coords(mouse_pos))
            <= self.obj._max_distance  # pylint: disable=W0212 # I know what I'm doing, don't scream at me
        )


class RenderLens(Renderable):
    NotImplemented

    def render(self, scene):
        raise NotImplementedError

    def check_mouse_hover(self, scene, mouse_pos):
        raise NotImplementedError


class RenderScene:
    def __init__(
        self,
        system: OpticSystem,
        scr: pygame.Surface,
        steps: int = STEPS,
        scale: float | int = PYGAME_SCALE,
        middle: tuple[int, int] = PYGAME_MIDDLE_OFFSET,
    ) -> None:
        self.system = system
        self.scr = scr
        self.steps = steps
        self.scale = scale
        self.middle = middle

        self.object_renderers: list[Renderable] = list(
            map(self._make_renderer, system.optics + system.rays)  # type: ignore #I know what im doing
        )

    def reset(self) -> None:
        self.system.reset()

    def add(self, obj: Optic | RayEmitter) -> None:
        self.system.add(obj)
        self.object_renderers.append(self._make_renderer(obj))

    def run(self, steps: int | None = None) -> pygame.Surface:
        if steps is None:
            steps = self.steps

        self.scr.fill(BACKGROUND_COLOR)

        for _ in range(steps):
            if self.system.step():
                break

        self.render()

        return self.scr

    def step(self):
        self.system.step()
        for i in self.object_renderers:
            i.render(self)

        return self.scr

    def render(self):
        for j in self.object_renderers:
            j.render(self)

    def to_scene_coords(self, vec: VecArg) -> VecArg:
        return np.asarray(
            (
                vec[0] * self.scale + self.middle[0],
                -vec[1] * self.scale + self.middle[1],
            )
        )

    def to_scene_scale(self, val: float) -> float:
        return val * self.scale

    def from_scene_scale(self, val: float) -> float:
        return val / self.scale

    def from_scene_coords(self, loc: tuple[float, float]) -> VecArg:
        return np.asarray(
            (
                (loc[0] - self.middle[0]) / self.scale,
                -(loc[1] - self.middle[1]) / self.scale,
            )
        )

    @staticmethod
    def _make_renderer(obj):
        match obj:
            case RayEmitter():
                return RenderRay(obj)
            case FlatMirror():
                return RenderFlat(obj)
            case SphericalMirror():
                return RenderSpherical(obj)
            case Lens():
                return RenderLens(obj)
            case _:
                raise TypeError
