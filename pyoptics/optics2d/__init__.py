from abc import ABC, abstractmethod
from math import asin, atan, cos, pi, sin, sqrt, tan
from typing import TypeAlias

import numpy as np


VecArg: TypeAlias = np.ndarray | tuple[float, float]
Angle: TypeAlias = float

DirectionVec: TypeAlias = np.ndarray


PI_HALF = pi / 2


class RayEmitter:
    def __init__(self, location, rotation) -> None:
        self.location = np.array(location)
        self.rotation = rotation
        
        self.last_bounce_location: np.ndarray = np.array(location)
        self.last_bounce_direction: Angle = rotation

        self.bounce_locations: list[np.ndarray] = []


class Optic(ABC):
    @abstractmethod
    def get_bounce(self, ray: RayEmitter) -> tuple[np.ndarray, Angle] | None:
        """return the coordinates of the next contact of a given light ray with this Optic and the rays new direction.

        Parameters
        ----------
        ray : Ray

        Returns
        -------
        tuple[np.ndarray, Angle] | None
            A location-angle pair or None if the given light ray does not interact with this optic. 
            
        """
        raise NotImplementedError


# TODO
class Lens(Optic):
    pass


class FlatMirror(Optic):
    def __init__(self, location: VecArg, rotation: Angle, scale: float) -> None:
        self.location = location
        self.rotation = rotation
        self.scale = scale

    def _get_intersection(
        self, prev_location: VecArg, direction: Angle
    ) -> VecArg | None:

        vec = _angle_to_direction_vec(direction)
        # TODO
        return None

    def get_bounce(self, ray) -> tuple[np.ndarray, float] | None:
        pass


class SphericalMirror(Optic):
    def __init__(
        self, location: VecArg, rotation: Angle, scale: float, focal: float = 0
    ) -> None:
        """
        Describe a spherical mirror by the location of its center, rotation, scale and focal length
        """
        # TODO getters, setters - property
        self.location: np.ndarray = np.array(location)
        self.rotation: Angle = rotation
        self.scale: float = scale
        self.focal = focal

        self._radius = self.focal * 2 * self.scale

        self._center_x = self.location[0] - self._radius * cos(self.rotation)
        self._center_y = self.location[1] - self._radius * sin(self.rotation)
        self._center = np.array((self._center_x, self._center_y))

        self._arc_angle_half = asin(0.5 / self._radius)
        self._max_distance = (
            2 * self._radius * cos(self._arc_angle_half / 2)
        )  # arc_angle_fourth

    def _get_intersection(
        self, prev_location: VecArg, direction: Angle
    ) -> VecArg | None:
        a, b = prev_location
        c, d = _angle_to_direction_vec(direction)
        m = self._center_x
        n = self._center_y
        r = self._radius
        under_root = (4 * (a * c + b * d - c * m - d * n)**2 -
                      4 * (c**2 + d**2) *
                      (a**2 - 2 * a * m + b**2 - 2 * b * n + m**2 + n**2 - r**2)
                    )
        if under_root < 0:
            return None

        t1 = (1 / 2 * sqrt(under_root) - a * c - b * d + c * m + d * n) / (c**2 + d**2)
        t2 = (-1 / 2 * sqrt(under_root) - a * c - b * d + c * m + d * n) / (c**2 + d**2)

        # print(t1, t2) # XXX debuuuuuuuuuuug

        # FIXME intersection with circle is correct
        # But im unsure about the intersection with an arc
        p1 = np.array((a + t1 * c, b + t1 * d))
        p2 = np.array((a + t2 * c, b + t2 * d))

        ret1 = _distance(p1, self.location) <= self._max_distance and t1 > 0
        ret2 = _distance(p2, self.location) <= self._max_distance and t2 > 0

        if ret1 and ret2:
            if t1 < t2:
                return p1
            else:
                return p2
        if ret1:
            return p1
        if ret2:
            return p2

        return None

    def get_bounce(self, ray: RayEmitter) -> tuple[np.ndarray, Angle] | None:
        prev_location = ray.last_bounce_location
        direction = ray.last_bounce_direction
        p_inter = self._get_intersection(prev_location, direction)
        if p_inter is None:
            return None

        # XXX English is hard
        radius_vec = p_inter - self._center

        # TODO odbić kąt padania symetrycznie względem `radius_vec` i pomnożyć przez -1
        return None


class OpticSystem:
    def __init__(self) -> None:
        self.optics: list[Optic] = []
        self.rays: list[RayEmitter] = []

    def step(self) -> bool:
        """
        Progress the simulation.

        Returns
        -------
        bool
            True if nothing changed and the simulation should end, False otherwise.
        """
        fin = True
        for ray in self.rays:
            loc = ray.last_bounce_location
            direction = ray.last_bounce_direction
            intersections = [optic.get_bounce(ray) for optic in self.optics]

            new_loc = loc
            new_direction = direction
            new_distance = float("inf")

            for inter in intersections:
                if inter is None:
                    continue

                l = inter[0]
                dis = _distance(loc, l)
                if dis < new_distance:
                    new_loc = l
                    new_direction = inter[1]
                    new_distance = dis

            if loc != new_loc or direction != new_direction:
                ray.bounce_locations.append(loc)
                ray.last_bounce_location = new_loc
                ray.last_bounce_direction = new_direction

                fin = False

        return fin


def _distance(point_a: np.ndarray, point_b: np.ndarray):
    return np.linalg.norm(point_a - point_b)


def _angle_to_direction_vec(ang: Angle) -> np.ndarray:
    return np.array((cos(ang), sin(ang)))


def _direction_vec_to_angle(direction: DirectionVec):
    if direction[0] == 0:
        return PI_HALF
    return atan(direction[1] / direction[0])


def _normalize(vector: np.ndarray) -> np.ndarray:
    """Returns the unit vector of the vector"""
    return vector / np.linalg.norm(vector)


def _perpendicular(vector: np.ndarray) -> np.ndarray:
    return np.array(vector[1], -vector[0])


def _angle_between(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """Returns the angle in radians between vectors 'v1' and 'v2'. Shamelessly stolen from
    https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249
    becuase im here to write code not do linear algebra
    """
    v1_u = _normalize(v1)
    v2_u = _normalize(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


mir = SphericalMirror((2, 2), 0, 1, 2)
print(mir._get_intersection((-2, 0), atan(1 / 2)))
