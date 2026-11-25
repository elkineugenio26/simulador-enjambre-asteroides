"""Game loop: lee eventos -> update puro -> render."""
import multiprocessing as mp

import pygame

from parallel import update_parallel
from render import render
from state import Events, make_initial_state
from update import update_sequential

WIDTH, HEIGHT = 1000, 700
SIZES = {pygame.K_1: 1000, pygame.K_2: 3000, pygame.K_3: 5000}


def main():
    n_workers = mp.cpu_count()
    print(f"Nucleos detectados: {mp.cpu_count()} | workers configurados: {n_workers}")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont("consolas", 16)
    clock = pygame.time.Clock()

    state = make_initial_state(1000, width=WIDTH, height=HEIGHT)
    parallel_mode = True

    # El Pool se crea UNA sola vez (crearlo por frame seria carisimo).
    with mp.Pool(processes=n_workers) as pool:
        running = True
        while running:
            dt = min(clock.tick(120) / 1000.0, 0.05)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        parallel_mode = not parallel_mode
                    elif ev.key in SIZES:
                        state = make_initial_state(SIZES[ev.key], width=WIDTH, height=HEIGHT)

            events = Events(target=tuple(float(v) for v in pygame.mouse.get_pos()))

            # Nuevo estado en cada frame; el anterior nunca se modifica.
            state = (
                update_parallel(state, events, dt, pool, n_workers)
                if parallel_mode
                else update_sequential(state, events, dt)
            )

            render(screen, font, state, clock.get_fps(),
                   "PARALELO" if parallel_mode else "SECUENCIAL", n_workers)

    pygame.quit()


if __name__ == "__main__":  # obligatorio en Windows por el modo 'spawn'
    main()