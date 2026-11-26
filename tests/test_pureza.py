"""Tests de pureza funcional. Ejecutar con: python -m pytest"""
import os
import sys
from dataclasses import FrozenInstanceError

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state import Entity, Events, GameState, make_initial_state
from update import step_entity, update_sequential

EV = Events(target=(500.0, 350.0))


def test_gamestate_es_inmutable():
    s = make_initial_state(5)
    with pytest.raises(FrozenInstanceError):
        s.frame = 99


def test_entity_es_inmutable():
    e = make_initial_state(1).entities[0]
    with pytest.raises(FrozenInstanceError):
        e.x = 123.0


def test_entities_es_tupla_y_no_lista():
    """Una tupla no se puede modificar; una lista si."""
    s = make_initial_state(5)
    assert isinstance(s.entities, tuple)
    assert isinstance(s.obstacles, tuple)


def test_update_no_muta_el_estado_de_entrada():
    s = make_initial_state(200)
    entidades_antes = tuple(s.entities)
    frame_antes = s.frame
    nuevo = update_sequential(s, EV, 0.016)
    assert s.entities == entidades_antes
    assert s.frame == frame_antes
    assert nuevo is not s
    assert nuevo.frame == frame_antes + 1


def test_update_devuelve_nuevas_entidades():
    s = make_initial_state(50)
    nuevo = update_sequential(s, EV, 0.016)
    assert all(a is not b for a, b in zip(s.entities, nuevo.entities))
    assert nuevo.entities != s.entities


def test_step_entity_devuelve_una_entidad_nueva():
    s = make_initial_state(1)
    e = s.entities[0]
    copia = Entity(e.x, e.y, e.vx, e.vy, e.radius)
    nueva = step_entity(e, 0.016, s.width, s.height, EV.target, s.obstacles)
    assert nueva is not e
    assert e == copia  # la original quedo intacta


def test_update_es_determinista():
    """Mismas entradas -> misma salida (propiedad de una funcion pura)."""
    s = make_initial_state(100)
    assert update_sequential(s, EV, 0.016) == update_sequential(s, EV, 0.016)


def test_entidades_siguen_dentro_del_mundo():
    s = make_initial_state(300)
    for _ in range(30):
        s = update_sequential(s, EV, 0.016)
    assert all(0 <= e.x <= s.width and 0 <= e.y <= s.height for e in s.entities)


def test_obstaculos_no_cambian_en_update():
    s = make_initial_state(50)
    nuevo = update_sequential(s, EV, 0.016)
    assert nuevo.obstacles == s.obstacles
    assert isinstance(nuevo, GameState)