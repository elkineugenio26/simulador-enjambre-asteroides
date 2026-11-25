"""Funciones puras de actualizacion. Ninguna muta su entrada."""
from dataclasses import replace
from math import sqrt
from typing import Tuple

from state import Entity, Events, GameState, Obstacle

ATTRACTION = 0.8      # fuerza hacia el mouse
REPULSION = 9000.0    # fuerza de rechazo de los obstaculos
MAX_SPEED = 220.0
DAMPING = 0.995


def repulsion_from(e: Entity, o: Obstacle) -> Tuple[float, float]:
    """Fuerza que un obstaculo ejerce sobre una entidad (pura)."""
    dx, dy = e.x - o.x, e.y - o.y
    d2 = dx * dx + dy * dy + 1e-6
    reach = (o.r + e.radius + 60.0) ** 2
    d = sqrt(d2)
    strength = REPULSION / d2 if d2 < reach else 0.0
    return (dx / d * strength, dy / d * strength)


def step_entity(e: Entity, dt, width, height, target, obstacles) -> Entity:
    """Devuelve una NUEVA entidad. Es la unidad de trabajo que se paraleliza."""
    forces = tuple(repulsion_from(e, o) for o in obstacles)
    fx = sum(f[0] for f in forces) + (target[0] - e.x) * ATTRACTION
    fy = sum(f[1] for f in forces) + (target[1] - e.y) * ATTRACTION

    vx = (e.vx + fx * dt) * DAMPING
    vy = (e.vy + fy * dt) * DAMPING
    speed = sqrt(vx * vx + vy * vy) + 1e-9
    scale = min(1.0, MAX_SPEED / speed)
    vx, vy = vx * scale, vy * scale

    nx, ny = e.x + vx * dt, e.y + vy * dt
    vx = -vx if (nx < 0 or nx > width) else vx
    vy = -vy if (ny < 0 or ny > height) else vy
    return replace(
        e,
        x=min(max(nx, 0.0), width),
        y=min(max(ny, 0.0), height),
        vx=vx,
        vy=vy,
    )


def update_chunk(task):
    """Funcion pura que ejecuta cada worker sobre su segmento.
    Debe estar a nivel de modulo para poder serializarse (pickle)."""
    chunk, dt, width, height, target, obstacles = task
    return tuple(step_entity(e, dt, width, height, target, obstacles) for e in chunk)


def update_sequential(state: GameState, events: Events, dt: float) -> GameState:
    """update(state, events, dt) -> GameState, version 1 nucleo."""
    new_entities = update_chunk(
        (state.entities, dt, state.width, state.height, events.target, state.obstacles)
    )
    return replace(state, entities=new_entities, frame=state.frame + 1)