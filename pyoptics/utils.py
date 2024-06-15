from pygame import Surface

from .optics2d import FlatMirror, Lens, OpticSystem, RayEmitter, SphericalMirror
from .renderer import RenderScene

from math import radians

class ConfigError(Exception):
    ...

def scene_from_cfg(path: str, scr: Surface, steps = 1, scale = 40., middle=(300, 300)) -> RenderScene:
    with open(path, "r") as f:
        
        optics: list[FlatMirror|SphericalMirror|Lens] = []
        rays: list[RayEmitter] = []
        for line in f.readlines():
            line = line.strip()
            
            # remove comments
            if "#" in line:
                line = line[:line.index("#")]
            
            if line.isspace():
                continue
            
            elems = line.split(",")
            obj_type = elems[0].strip()
            obj_args = tuple(map(lambda x: float(x.strip()), elems[1:]))
            l = len(obj_args)
            match obj_type:
                case "F":
                    if l!=4:
                        raise ConfigError(f"A FlatMirror instance needs 4 arguments, not {l}")
                    optics.append(FlatMirror((obj_args[0], obj_args[1]), radians(obj_args[2]), obj_args[3] ))
                    
                case "S":
                    if l!=4 and l!=5:
                        raise ConfigError(f"A SphericalMirror instance needs 4 or 5 arguments, not {l}")
                    optics.append(SphericalMirror((obj_args[0], obj_args[1]), radians(obj_args[2]), *obj_args[3:]))
                    
                case "L":
                    if l!=4 and l!=5 and l!=6:
                        raise ConfigError(f"A Lens instance needs 4, 5 or 6 arguments, not {l}")
                    optics.append(Lens((obj_args[0], obj_args[1]), radians(obj_args[2]), *obj_args[3:]))
                    
                case "R" | "E":
                    if l!=3:
                        raise ConfigError(f"A RayEmitter instance needs 3 arguments, not {l}")
                    rays.append(RayEmitter((obj_args[0], obj_args[1]), radians(obj_args[2])))
            
        system = OpticSystem(optics, rays)
        
        return RenderScene(system, scr, steps, scale, middle)
        