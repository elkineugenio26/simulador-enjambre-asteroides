"""Renderizado 2D. Es la unica capa con efectos secundarios (dibuja en pantalla).
Solo LEE el estado; nunca lo modifica."""
from math import sqrt

import pygame

BG = (10, 12, 24)
OBSTACLE_COLOR = (230, 90, 90)
TEXT_COLOR = (240, 240, 240)
PAUSE_COLOR = (255, 210, 80)
MAX_SPEED = 220.0  # mismo valor que MAX_SPEED en update.py


def speed_color(e):
    """Funcion pura: velocidad de la entidad -> color (azul lento, rojo rapido)."""
    t = min(1.0, sqrt(e.vx * e.vx + e.vy * e.vy) / MAX_SPEED)
    return (int(60 + 195 * t), int(150 - 90 * t), int(255 - 205 * t))


def hud_lines(state, fps, mode, n_workers, paused):
    """Funcion pura: construye las lineas de texto del HUD."""
    modo = f"PARALELO ({n_workers} workers)" if mode == "PARALELO" else "SECUENCIAL (1 nucleo)"
    return (
        f"Modo: {modo}",
        f"Entidades: {len(state.entities)}",
        f"FPS: {fps:.1f}   Frame: {state.frame}",
        "ESPACIO: modo | P: pausa | 1/2/3: 1000/3000/5000 entidades",
    ) + (("*** PAUSADO ***",) if paused else ())


def render(screen, font, state, fps, mode, n_workers, paused=False):
    screen.fill(BG)
    for o in state.obstacles:
        pygame.draw.circle(screen, OBSTACLE_COLOR, (int(o.x), int(o.y)), int(o.r))
    for e in state.entities:
        pygame.draw.circle(screen, speed_color(e), (int(e.x), int(e.y)), max(1, int(e.radius)))
    for i, line in enumerate(hud_lines(state, fps, mode, n_workers, paused)):
        color = PAUSE_COLOR if line.startswith("***") else TEXT_COLOR
        screen.blit(font.render(line, True, color), (10, 10 + i * 20))
    pygame.display.flip()