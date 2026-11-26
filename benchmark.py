"""Mide FPS de simulacion (sin dibujar).

Tabla 1: secuencial vs paralelo (todos los nucleos) con 1,000 / 3,000 / 5,000 entidades.
Tabla 2: efecto del numero de workers con 5,000 entidades.
"""
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


def fps_parallel(state, n_workers):
    """FPS del modo paralelo usando exactamente n_workers procesos."""
    with mp.Pool(processes=n_workers) as pool:
        pool.map(abs, range(n_workers))  # calentamiento: arranca los procesos
        return run(lambda s: update_parallel(s, EVENTS, DT, pool, n_workers), state)


def worker_counts(cores):
    """1, 2, 4, 8... hasta los nucleos detectados (sin repetir)."""
    base = tuple(w for w in (1, 2, 4, 8) if w < cores)
    return base + (cores,)


def main():
    cores = mp.cpu_count()
    print(f"Nucleos detectados: {cores} | workers: {cores} | "
          f"particion: {cores} segmentos contiguos de tamano ~N/{cores}")

    print("\nTABLA 1: secuencial vs paralelo")
    print(f"{'Entidades':>10} | {'Secuencial (FPS)':>17} | {'Paralelo (FPS)':>15}")
    print("-" * 49)
    for n in SIZES:
        s0 = make_initial_state(n)
        seq = run(lambda s: update_sequential(s, EVENTS, DT), s0)
        par = fps_parallel(s0, cores)
        print(f"{n:>10,} | {seq:>17.1f} | {par:>15.1f}")

    print("\nTABLA 2: FPS segun numero de workers (5,000 entidades)")
    print(f"{'Workers':>8} | {'FPS':>8}")
    print("-" * 20)
    s5k = make_initial_state(5000)
    resultados = tuple((w, fps_parallel(s5k, w)) for w in worker_counts(cores))
    for w, fps in resultados:
        print(f"{w:>8} | {fps:>8.1f}")
    mejor = max(resultados, key=lambda r: r[1])
    print(f"\nMejor configuracion: {mejor[0]} workers ({mejor[1]:.1f} FPS)")


if __name__ == "__main__":
    main()