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
    """Devuelve una NUEVA entidad. Es la unidad de trabajo que se paraleliza.

    Cada nombre se asigna UNA sola vez (asignacion unica): no se reasigna ninguna
    variable local ni se muta ningun objeto. Solo se calculan valores nuevos.
    """
    forces = tuple(repulsion_from(e, o) for o in obstacles)
    fx = sum(f[0] for f in forces) + (target[0] - e.x) * ATTRACTION
    fy = sum(f[1] for f in forces) + (target[1] - e.y) * ATTRACTION

    # velocidad con amortiguamiento
    vx_free = (e.vx + fx * dt) * DAMPING
    vy_free = (e.vy + fy * dt) * DAMPING
    # limite de velocidad
    speed = sqrt(vx_free * vx_free + vy_free * vy_free) + 1e-9
    scale = min(1.0, MAX_SPEED / speed)
    vx_cap, vy_cap = vx_free * scale, vy_free * scale

    # posicion tentativa y rebote en los bordes
    nx, ny = e.x + vx_cap * dt, e.y + vy_cap * dt
    vx_final = -vx_cap if (nx < 0 or nx > width) else vx_cap
    vy_final = -vy_cap if (ny < 0 or ny > height) else vy_cap

    return replace(
        e,
        x=min(max(nx, 0.0), width),
        y=min(max(ny, 0.0), height),
        vx=vx_final,
        vy=vy_final,
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