"""Tests de la parte paralela. Ejecutar con: python -m pytest"""
import multiprocessing as mp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parallel import split, update_parallel
from state import Events, make_initial_state
from update import update_sequential

EV = Events(target=(500.0, 350.0))


def test_parallel_igual_a_secuencial():
    """El resultado paralelo debe ser IDENTICO al secuencial."""
    s = make_initial_state(500)
    with mp.Pool(2) as pool:
        par = update_parallel(s, EV, 0.016, pool, 2)
    assert par == update_sequential(s, EV, 0.016)


def test_no_muta_el_estado_original():
    """El estado de entrada no cambia tras actualizar."""
    s = make_initial_state(200)
    copia_entities = tuple(s.entities)
    with mp.Pool(2) as pool:
        nuevo = update_parallel(s, EV, 0.016, pool, 2)
    assert s.entities == copia_entities
    assert s.frame == 0 and nuevo.frame == 1
    assert nuevo is not s


def test_split_conserva_todas_las_entidades_y_el_orden():
    datos = tuple(range(103))
    for n_parts in (1, 2, 4, 7, 16):
        partes = split(datos, n_parts)
        assert tuple(x for p in partes for x in p) == datos
        assert len(partes) <= n_parts


def test_varios_frames_paralelo_igual_a_secuencial():
    """Tras 5 frames seguidos sigue siendo igual (no se acumulan diferencias)."""
    seq = par = make_initial_state(300)
    with mp.Pool(2) as pool:
        for _ in range(5):
            seq = update_sequential(seq, EV, 0.016)
            par = update_parallel(par, EV, 0.016, pool, 2)
    assert seq == par