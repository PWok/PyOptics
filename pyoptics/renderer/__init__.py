from abc import ABC, abstractmethod
from math import asin, cos, sin, pi

import pygame

from ..optics2d import *

STEEL = pygame.Color("#99a3a3")
RED = pygame.Color("#c70e20")
BLUE = pygame.Color("#23acc4")

BACKGROUND_COLOR = pygame.Color("#000000")

STEPS = 20

PYGAME_SCALE = 40
PYGAME_MIDDLE_OFFSET = (300, 300)

DEFAULT_LINE_WIDTH = 1


def _vector_add(vec1: VecArg, vec2: VecArg) -> VecArg:
    return (vec1[0] + vec2[0], vec1[1] + vec2[1])


def _vector_mult(vec: VecArg, scalar: float | int) -> VecArg:
    return (vec[0] * scalar, vec[1] * scalar)


def _to_pygame_coords(vec: VecArg):
    return (
        vec[0] * PYGAME_SCALE + PYGAME_MIDDLE_OFFSET[0],
        -vec[1] * PYGAME_SCALE + PYGAME_MIDDLE_OFFSET[1],
    )


def _to_pygame_scale(val: float):
    return val * PYGAME_SCALE


class Renderable(ABC):
    def __init__(self, obj, color=BLUE, width=DEFAULT_LINE_WIDTH) -> None:
        self.obj = obj
        self.color = color
        self.width = width

    @abstractmethod
    def render(self, scr) -> pygame.Surface:
        raise NotImplementedError


class RenderRay(Renderable):
    def __init__(
        self, obj: RayEmitter, color=STEEL, ray_color=RED, ray_width=2
    ) -> None:
        self.obj: RayEmitter
        super().__init__(obj, color)
        self.ray_color = ray_color
        self.ray_width = ray_width

    def render(self, scr) -> pygame.Surface:
        loc = _to_pygame_coords(self.obj.location)
        points = [loc] + list(
            map(
                _to_pygame_coords,
                self.obj.bounce_locations + [self.obj.last_bounce_location],
            )
        )

        # print(self.obj.bounce_locations)
        pygame.draw.circle(scr, self.color, loc, PYGAME_SCALE / 2)
        if len(points) >= 2:
            pygame.draw.lines(scr, self.ray_color, False, points, self.ray_width)

        return scr


class RenderFlat(Renderable):
    def render(self, scr) -> pygame.Surface:
        self.obj: FlatMirror
        ang = self.obj.rotation
        scale = self.obj.scale / 2
        loc = self.obj.location

        vec = (cos(ang) * scale, sin(ang) * scale)

        start = _to_pygame_coords(_vector_add(loc, vec))
        end = _to_pygame_coords(_vector_add(loc, _vector_mult(vec, -1)))

        pygame.draw.line(scr, self.color, start, end, width=self.width)

        return scr


class RenderArc(Renderable):
    def render(self, scr) -> pygame.Surface:
        self.obj: SphericalMirror
        rot = -self.obj.rotation
        scale = self.obj.scale

        radius = self.obj.focal * 2 * scale

        vec = (
            _to_pygame_scale(-radius * cos(rot) - radius),
            _to_pygame_scale(-radius * sin(rot) - radius),
        )

        loc = _vector_add(_to_pygame_coords(tuple(self.obj.location)), vec)

        pygame.draw.arc(
            scr,
            self.color,
            pygame.Rect(
                loc[0],
                loc[1],
                _to_pygame_scale(2 * radius),
                _to_pygame_scale(2 * radius),
            ),
            -asin(0.25 / self.obj.focal) - rot,
            asin(0.25 / self.obj.focal) - rot,
            width=self.width,
        )
        return scr


class RenderLens(Renderable):
    NotImplemented

    def render(self, scr) -> pygame.Surface:
        return scr


class RenderScene:
    def __init__(self, system: OpticSystem, scr: pygame.Surface, steps=STEPS) -> None:
        self.system = system
        self.scr = scr
        self.steps = steps

        self.object_renderers: list[Renderable] = list(
            map(self._make_renderer, system.optics + system.rays)  # type: ignore #I know what im doing
        )
        
    def reset(self) -> None:
        self.system.reset()

    def add(self, obj: Optic|RayEmitter) -> None:
        self.system.add(obj)
        self.object_renderers.append(self._make_renderer(obj))

    def run(self, steps: int | None = None) -> pygame.Surface:
        if steps is None:
            steps = self.steps

        self.scr.fill(BACKGROUND_COLOR)

        for _ in range(steps):
            # print("\n\n", i)
            if self.system.step():
                break

        self.render()

        return self.scr

    def step(self):
        self.system.step()
        for i in self.object_renderers:
            i.render(self.scr)

        return self.scr

    def render(self):
        for j in self.object_renderers:
            j.render(self.scr)

    @staticmethod
    def _make_renderer(obj):
        match obj:
            case RayEmitter():
                return RenderRay(obj)
            case FlatMirror():
                return RenderFlat(obj)
            case SphericalMirror():
                return RenderArc(obj)
            case Lens():
                return RenderLens(obj)
            case _:
                raise TypeError
