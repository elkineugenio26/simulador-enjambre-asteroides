"""Segmentacion, mapeo paralelo y consolidacion con multiprocessing."""
from dataclasses import replace
from itertools import chain
from math import ceil

from state import Events, GameState
from update import update_chunk


def split(seq, n_parts):
    """Segmentacion: divide una tupla en n_parts partes contiguas y casi iguales."""
    size = max(1, ceil(len(seq) / n_parts))
    return tuple(seq[i:i + size] for i in range(0, len(seq), size))


def update_parallel(state: GameState, events: Events, dt: float, pool, n_workers: int) -> GameState:
    """update(state, events, dt) -> GameState, version paralela.

    1. Segmentacion: partir state.entities en n_workers segmentos.
    2. Mapeo paralelo: pool.map bloquea hasta que TODOS los workers terminan.
    3. Consolidacion: aplanar los resultados en una nueva tupla inmutable.
    """
    tasks = tuple(
        (chunk, dt, state.width, state.height, events.target, state.obstacles)
        for chunk in split(state.entities, n_workers)
    )
    results = pool.map(update_chunk, tasks)
    new_entities = tuple(chain.from_iterable(results))
    return replace(state, entities=new_entities, frame=state.frame + 1)