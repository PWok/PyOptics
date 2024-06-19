from abc import ABC, abstractmethod
from locale import normalize
from math import asin, atan, copysign, cos, isclose, pi, sin, sqrt, tan
from typing import Iterable, TypeAlias, Any

import numpy as np
from numpy import asarray


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


VecArg: TypeAlias = np.ndarray[np.floating, Any]
Angle: TypeAlias = float

DirectionVec: TypeAlias = np.ndarray[np.floating, Any]

PI = pi
PI_HALF = PI / 2

BIG_NUMBER = 1000


class RayEmitter:
    def __init__(self, location, rotation) -> None:
        self.location: VecArg = asarray(location)
        self.rotation = rotation

        self.last_bounce_location: VecArg = asarray(location)
        self.last_bounce_direction: Angle = rotation

        self.bounce_locations: list[VecArg] = []

    def reset(self):
        self.last_bounce_location = self.location
        self.last_bounce_direction = self.rotation

        self.bounce_locations = []


class Optic(ABC):

    @abstractmethod
    def __init__(self) -> None:
        self.location: VecArg
        self.scale: float
        self.rotation: Angle

    @abstractmethod
    def get_bounce(self, ray: RayEmitter) -> tuple[VecArg, Angle] | None:
        """return the coordinates of the next contact of a given light ray with this Optic and the rays new direction.

        Parameters
        ----------
        ray : Ray

        Returns
        -------
        tuple[ndarray, Angle] | None
            A location-angle pair or None if the given light ray does not interact with this optic.

        """
        raise NotImplementedError


# TODO
class Lens(Optic):
    def __init__(
        self, location, rotation: Angle, scale: float, focal1=1.0, focal2=1.0
    ) -> None:
        self.location: VecArg = asarray(location)
        self.rotation = rotation
        self.scale = scale
        self.focal1 = focal1
        self.focal2 = focal2

    def get_bounce(self, ray: RayEmitter) -> tuple[VecArg, float] | None:
        return None


class FlatMirror(Optic):
    def __init__(self, location, rotation: Angle, scale: float) -> None:
        self.location = asarray(location)
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

        point = asarray((x, y))
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
        self, location, rotation: Angle, chord: float, focal: float = 1
    ) -> None:
        """
        Describe a spherical mirror by the location of its center, rotation, chord and focal length
        """
        self.__location = asarray(location)
        self.__rotation: Angle = rotation
        self.__chord_len: float = chord
        self.focal = focal

        self.__radius = self.focal * 2

        self._center_x = self.__location[0] - self.__radius * cos(self.__rotation)
        self._center_y = self.__location[1] - self.__radius * sin(self.__rotation)
        self._center = np.array((self._center_x, self._center_y))

        self._max_distance = sqrt(
            (self.__chord_len / 2) ** 2
            + (self.__radius - sqrt(self.__radius**2 - (self.__chord_len / 2) ** 2))
            ** 2
        )  # arc_angle_fourth

    @property
    def location(self) -> VecArg:
        return self.__location

    @location.setter
    def location(self, value: VecArg) -> None:
        self.__location = value

        self._center_x = self.__location[0] - self.__radius * cos(self.__rotation)
        self._center_y = self.__location[1] - self.__radius * sin(self.__rotation)
        self._center = np.array((self._center_x, self._center_y))

    @property
    def rotation(self):
        return self.__rotation

    @rotation.setter
    def rotation(self, value):
        self.__rotation = value

        self._center_x = self.__location[0] - self.__radius * cos(self.__rotation)
        self._center_y = self.__location[1] - self.__radius * sin(self.__rotation)
        self._center = np.array((self._center_x, self._center_y))

    @property
    def scale(self):
        return self.__chord_len

    @scale.setter
    def scale(self, value):
        self.__chord_len = value

        self._max_distance = sqrt(
            (self.__chord_len / 2) ** 2
            + (self.__radius - sqrt(self.__radius**2 - (self.__chord_len / 2) ** 2))
            ** 2
        )

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        self.__radius = value
        self._center_x = self.__location[0] - self.__radius * cos(self.__rotation)
        self._center_y = self.__location[1] - self.__radius * sin(self.__rotation)
        self._center = np.array((self._center_x, self._center_y))

        self._max_distance = sqrt(
            (self.__chord_len / 2) ** 2
            + (self.__radius - sqrt(self.__radius**2 - (self.__chord_len / 2) ** 2))
            ** 2
        )

    def __calculate_delta(self, prev_location, direction) -> tuple[float, float] | None:
        a, b = prev_location
        c, d = _angle_to_direction_vec(direction)
        m = self._center_x
        n = self._center_y
        r = self.__radius
        under_root = 4 * (a * c + b * d - c * m - d * n) ** 2 - 4 * (
            c**2 + d**2
        ) * (a**2 - 2 * a * m + b**2 - 2 * b * n + m**2 + n**2 - r**2)

        if under_root < 0:
            return None

        distance1 = (1 / 2 * sqrt(under_root) - a * c - b * d + c * m + d * n) / (
            c**2 + d**2
        )
        distance2 = (-1 / 2 * sqrt(under_root) - a * c - b * d + c * m + d * n) / (
            c**2 + d**2
        )

        return distance1, distance2

    def _get_intersection(
        self, prev_location: VecArg, direction: Angle
    ) -> VecArg | None:

        distances = self.__calculate_delta(prev_location, direction)
        if distances is None:
            return None

        distance1, distance2 = distances

        dir_vec = _angle_to_direction_vec(direction)

        point1 = prev_location + dir_vec * distance1
        point2 = prev_location + dir_vec * distance2

        ret1 = (
            _distance(point1, self.location) <= self._max_distance and distance1 > 0
        )
        ret2 = (
            _distance(point2, self.location) <= self._max_distance and distance2 > 0
        )

        if ret1 and ret2:
            if distance1 < distance2 or isclose(distance2, 0, abs_tol=1e-14):
                return point1
            else:
                return point2
        if ret1:
            return point1
        if ret2:
            return point2
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
            loc: VecArg = ray.last_bounce_location
            direction = ray.last_bounce_direction

            intersections = [optic.get_bounce(ray) for optic in self.optics]

            new_loc = None
            new_direction = direction
            new_distance = float("inf")

            arr_loc = asarray(loc)

            dir_vect = _angle_to_direction_vec(direction)

            for inter in intersections:
                if inter is None:

                    continue

                l = inter[0]

                dis = _distance(loc, l)

                if (
                    dis < new_distance
                    and _points_close(dir_vect, _normalize(asarray(l) - arr_loc))
                    and not (_points_close(loc, l))
                ):
                    new_loc = l
                    new_direction = inter[1]
                    new_distance = dis

            if new_loc is None:
                ray.bounce_locations.append(loc)
                ray.last_bounce_location = arr_loc + BIG_NUMBER * dir_vect
                fin += 1
                continue
            if all(loc != new_loc) or direction != new_direction:
                ray.bounce_locations.append(loc)
                ray.last_bounce_location = new_loc
                ray.last_bounce_direction = new_direction

        return fin == len(self.rays)


def _distance(point_a: VecArg, point_b: VecArg):
    return np.linalg.norm(point_a - point_b)


def _angle_to_direction_vec(ang: Angle) -> VecArg:
    return np.array((cos(ang), sin(ang)))


def _direction_vec_to_angle(direction: DirectionVec):
    if direction[1] == 0:
        return 0 if direction[0] > 0 else -pi
    if direction[0] == 0:
        return copysign(PI_HALF, direction[1])
    return _normalize_angle(
        atan(direction[1] / direction[0])
        + (copysign(pi, direction[0]) if direction[0] < 0 else 0)
    )


def _normalize(vector: VecArg) -> VecArg:
    """Returns the unit vector of the vector"""
    return vector / np.linalg.norm(vector)


def _points_close(p1: VecArg, p2: VecArg, *, rel_tol=1e-9, abs_tol=1e-12):
    return isclose(p1[0], p2[0], abs_tol=abs_tol, rel_tol=rel_tol) and isclose(
        p1[1], p2[1], abs_tol=abs_tol, rel_tol=rel_tol
    )


def _normalize_angle(ang: Angle):
    while ang > pi:
        ang -= 2 * pi

    while ang < -pi:
        ang += 2 * pi

    return ang
