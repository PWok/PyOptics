from abc import ABC, abstractmethod
from locale import normalize
from math import asin, atan, copysign, cos, isclose, pi, sin, sqrt, tan
from typing import Iterable, TypeAlias

import numpy as np

__all__ = [
    "RayEmitter",
    "Optic",
    "Lens",
    "FlatMirror",
    "SphericalMirror",
    "OpticSystem",
    "VecArg",
    "Angle",
]


VecArg: TypeAlias = tuple[float, float]
Angle: TypeAlias = float

DirectionVec: TypeAlias = np.ndarray

PI = pi
PI_HALF = PI / 2

BIG_NUMBER = 1000


class RayEmitter:
    def __init__(self, location: VecArg, rotation) -> None:
        self.location = location
        self.rotation = rotation

        self.last_bounce_location: VecArg = location
        self.last_bounce_direction: Angle = rotation

        self.bounce_locations: list[VecArg] = []

    def reset(self):
        self.last_bounce_location = self.location
        self.last_bounce_direction = self.rotation

        self.bounce_locations = []


class Optic(ABC):
    @abstractmethod
    def get_bounce(self, ray: RayEmitter) -> tuple[VecArg, Angle] | None:
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
    def __init__(
        self, location: VecArg, rotation: Angle, scale: float, focal1=1.0, focal2=1.0
    ) -> None:
        self.location = location
        self.rotation = rotation
        self.scale = scale
        self.focal1 = focal1
        self.focal2 = focal2

    def get_bounce(self, ray: RayEmitter) -> tuple[tuple[float, float], float] | None:
        return None


class FlatMirror(Optic):
    def __init__(self, location: VecArg, rotation: Angle, scale: float) -> None:
        self.location = location
        self.rotation = rotation - PI_HALF
        self.scale = scale

    def _get_intersection(
        self, prev_location: VecArg, direction: Angle
    ) -> VecArg | None:

        self_a = tan(self.rotation)
        ray_a = tan(direction)

        self_b = self.location[1] - self_a * self.location[0]
        ray_b = prev_location[1] - ray_a * prev_location[0]

        d = np.linalg.det(((self_a, 1), (ray_a, 1)))
        if d == 0:
            return None

        dx = -np.linalg.det(((self_b, 1), (ray_b, 1)))
        dy = np.linalg.det(((self_a, self_b), (ray_a, ray_b)))

        x = dx / d
        y = dy / d

        point = (x, y)
        if _distance(point, self.location) > self.scale / 2:
            return None

        return point

    def get_bounce(self, ray) -> tuple[VecArg, float] | None:
        point = self._get_intersection(
            ray.last_bounce_location, ray.last_bounce_direction
        )

        if point is None:
            return None

        alpha = ray.last_bounce_direction
        beta = self.rotation

        rot = 2 * beta - alpha

        rot = _normalize_angle(rot)

        return point, rot


class SphericalMirror(Optic):
    def __init__(
        self, location: VecArg, rotation: Angle, scale: float, focal: float = 1
    ) -> None:
        """
        Describe a spherical mirror by the location of its center, rotation, scale and focal length
        """
        self.location: np.ndarray = np.array(location)
        self.rotation: Angle = rotation
        self.scale: float = scale
        self.focal = focal

        self._radius = self.focal * 2 * self.scale

        self._center_x = self.location[0] - self._radius * cos(self.rotation)
        self._center_y = self.location[1] - self._radius * sin(self.rotation)
        self._center = np.array((self._center_x, self._center_y))

        self._arc_angle_half = asin(0.5 / self._radius)
        self._max_distance = sqrt(
            1 + (self._radius - sqrt(self._radius**2 - 1)) ** 2
        )  # arc_angle_fourth

    def _get_intersection(
        self, prev_location: VecArg, direction: Angle
    ) -> VecArg | None:
        a, b = prev_location
        c, d = _angle_to_direction_vec(direction)
        m = self._center_x
        n = self._center_y
        r = self._radius
        under_root = 4 * (a * c + b * d - c * m - d * n) ** 2 - 4 * (
            c**2 + d**2
        ) * (a**2 - 2 * a * m + b**2 - 2 * b * n + m**2 + n**2 - r**2)
        if under_root < 0:
            return None

        t1 = (1 / 2 * sqrt(under_root) - a * c - b * d + c * m + d * n) / (c**2 + d**2)
        t2 = (-1 / 2 * sqrt(under_root) - a * c - b * d + c * m + d * n) / (c**2 + d**2)

        p1 = (a + t1 * c, b + t1 * d)
        p2 = (a + t2 * c, b + t2 * d)

        ret1 = _distance(p1, self.location) <= self._max_distance and t1 > 0
        ret2 = _distance(p2, self.location) <= self._max_distance and t2 > 0

        if ret1 and ret2:
            if t1 < t2 or isclose(t2, 0, abs_tol=1e-14):
                return p1
            else:
                return p2
        if ret1:
            return p1
        if ret2:
            return p2
        return None

    def get_bounce(self, ray: RayEmitter) -> tuple[VecArg, Angle] | None:
        prev_location = ray.last_bounce_location
        dir_angle = ray.last_bounce_direction
        p_inter = self._get_intersection(prev_location, dir_angle)
        if p_inter is None:
            return None

        radius_vec = _normalize(p_inter - self._center)

        dir_vec = _angle_to_direction_vec(dir_angle)
        # check if pointing in the same direction
        if np.dot(radius_vec, dir_vec) < 0:
            radius_vec = -radius_vec

        ang = _direction_vec_to_angle(dir_vec - 2 * radius_vec)
        return (p_inter, ang)


class OpticSystem:
    def __init__(
        self,
        optics: Iterable[Optic] | None = None,
        rays: Iterable[RayEmitter] | None = None,
    ) -> None:
        if optics is None:
            optics = []
        if rays is None:
            rays = []

        self.optics: list[Optic] = list(optics)
        self.rays: list[RayEmitter] = list(rays)

    def reset(self) -> None:
        for i in self.rays:
            i.reset()

    def add(self, obj: Optic | RayEmitter):
        if isinstance(obj, Optic):
            self.optics.append(obj)
        else:
            self.rays.append(obj)

    def step(self) -> bool:
        """
        Progress the simulation.

        Returns
        -------
        bool
            True if nothing changed and the simulation should end, False otherwise.
        """
        fin = 0

        # TODO this is awful. REDO all of this
        for ray in self.rays:
            loc = ray.last_bounce_location
            direction = ray.last_bounce_direction

            intersections = [optic.get_bounce(ray) for optic in self.optics]

            new_loc = None
            new_direction = direction
            new_distance = float("inf")

            arr_loc = np.asarray(loc)

            dir_vect = _angle_to_direction_vec(direction)

            for inter in intersections:
                if inter is None:
                    continue

                l = inter[0]

                dis = _distance(loc, l)
                if (
                    dis < new_distance
                    and _points_close(dir_vect, _normalize(np.asarray(l) - arr_loc))
                    and not (_points_close(loc, l))
                ):
                    new_loc = l
                    new_direction = inter[1]
                    new_distance = dis

            if new_loc is None:
                ray.bounce_locations.append(loc)
                ray.last_bounce_location = tuple(arr_loc + BIG_NUMBER * dir_vect)
                fin +=1
                continue
            if loc != new_loc or direction != new_direction:
                ray.bounce_locations.append(loc)
                ray.last_bounce_location = new_loc
                ray.last_bounce_direction = new_direction

        print(fin)
        return fin==len(self.rays)


def _distance(point_a: VecArg | np.ndarray, point_b: VecArg | np.ndarray):
    return np.linalg.norm(np.asarray(point_a) - np.asarray(point_b))


def _angle_to_direction_vec(ang: Angle) -> np.ndarray:
    return np.array((cos(ang), sin(ang)))


def _arr_to_VecArg(arr: np.ndarray) -> tuple[float, float]:
    return (arr[0], arr[1])


def _direction_vec_to_angle(direction: DirectionVec):
    if direction[1] == 0:
        return 0 if direction[0] > 0 else -pi
    if direction[0] == 0:
        return copysign(PI_HALF, direction[1])
    return _normalize_angle(
        atan(direction[1] / direction[0])
        + (copysign(pi, direction[0]) if direction[0] < 0 else 0)
    )


def _normalize(vector: np.ndarray) -> np.ndarray:
    """Returns the unit vector of the vector"""
    return vector / np.linalg.norm(vector)


def _perpendicular(vector: np.ndarray) -> np.ndarray:
    return np.array(vector[1], -vector[0])


def _points_close(
    p1: VecArg | np.ndarray, p2: VecArg | np.ndarray, *, rel_tol=1e-9, abs_tol=1e-12
):
    return isclose(p1[0], p2[0], abs_tol=abs_tol, rel_tol=rel_tol) and isclose(
        p1[1], p2[1], abs_tol=abs_tol, rel_tol=rel_tol
    )


def _angle_between(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """Returns the angle in radians between vectors 'v1' and 'v2'. Shamelessly stolen from
    https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249
    becuase im here to write code not do linear algebra
    """
    v1_u = _normalize(v1)
    v2_u = _normalize(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def _normalize_angle(ang: Angle):
    while ang > pi:
        ang -= 2 * pi

    while ang < -pi:
        ang += 2 * pi

    return ang
