"""Renderizado 2D. Es la unica capa con efectos secundarios (dibuja en pantalla)."""
import pygame

BG = (10, 12, 24)
ENTITY_COLOR = (120, 200, 255)
OBSTACLE_COLOR = (230, 90, 90)
TEXT_COLOR = (240, 240, 240)


def render(screen, font, state, fps, mode, n_workers):
    screen.fill(BG)
    for o in state.obstacles:
        pygame.draw.circle(screen, OBSTACLE_COLOR, (int(o.x), int(o.y)), int(o.r))
    for e in state.entities:
        pygame.draw.circle(screen, ENTITY_COLOR, (int(e.x), int(e.y)), max(1, int(e.radius)))
    lines = (
        f"Modo: {mode} ({n_workers} workers)" if mode == "PARALELO" else f"Modo: {mode} (1 nucleo)",
        f"Entidades: {len(state.entities)}   FPS: {fps:.1f}",
        "ESPACIO: cambiar modo | 1/2/3: 1000/3000/5000 entidades",
    )
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, TEXT_COLOR), (10, 10 + i * 20))
    pygame.display.flip()