"""Mide FPS de simulacion (sin dibujar) secuencial vs paralelo."""
import multiprocessing as mp
import time

from parallel import update_parallel
from state import Events, make_initial_state
from update import update_sequential

FRAMES = 60
DT = 1 / 60
EVENTS = Events(target=(500.0, 350.0))
SIZES = (1000, 3000, 5000)


def run(step, state, frames=FRAMES):
    """Aplica 'step' repetidamente y devuelve los FPS logrados."""
    start = time.perf_counter()
    for _ in range(frames):
        state = step(state)
    return frames / (time.perf_counter() - start)


def main():
    cores = mp.cpu_count()
    n_workers = cores
    print(f"Nucleos detectados: {cores} | workers: {n_workers} | "
          f"particion: {n_workers} segmentos contiguos de tamano ~N/{n_workers}")
    print(f"{'Entidades':>10} | {'Secuencial (FPS)':>17} | {'Paralelo (FPS)':>15}")
    print("-" * 49)

    with mp.Pool(processes=n_workers) as pool:
        pool.map(abs, range(n_workers))  # calentamiento: arranca los procesos
        for n in SIZES:
            s0 = make_initial_state(n)
            seq = run(lambda s: update_sequential(s, EVENTS, DT), s0)
            par = run(lambda s: update_parallel(s, EVENTS, DT, pool, n_workers), s0)
            print(f"{n:>10,} | {seq:>17.1f} | {par:>15.1f}")


if __name__ == "__main__":
    main()