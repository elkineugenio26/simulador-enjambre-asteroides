"""Estado inmutable del juego. Todo es @dataclass(frozen=True)."""
import random
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Entity:
    x: float
    y: float
    vx: float
    vy: float
    radius: float


@dataclass(frozen=True)
class Obstacle:
    x: float
    y: float
    r: float


@dataclass(frozen=True)
class Events:
    """Entradas del usuario en este frame (posicion del mouse)."""
    target: Tuple[float, float]


@dataclass(frozen=True)
class GameState:
    entities: Tuple[Entity, ...]
    obstacles: Tuple[Obstacle, ...]
    width: int
    height: int
    frame: int = 0


def make_initial_state(n_entities, n_obstacles=40, width=1000, height=700, seed=42):
    """Construye el GameState inicial de forma declarativa (comprensiones)."""
    rng = random.Random(seed)
    entities = tuple(
        Entity(
            x=rng.uniform(0, width),
            y=rng.uniform(0, height),
            vx=rng.uniform(-60, 60),
            vy=rng.uniform(-60, 60),
            radius=rng.uniform(1.5, 3.5),
        )
        for _ in range(n_entities)
    )
    obstacles = tuple(
        Obstacle(rng.uniform(0, width), rng.uniform(0, height), rng.uniform(12, 25))
        for _ in range(n_obstacles)
    )
    return GameState(entities, obstacles, width, height)