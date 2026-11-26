# simulador-enjambre-asteroides
Simulador 2D de enjambre/asteroides con multiprocessing y programación funcional (GameState inmutable)
## Estrategia de partición

En cada frame, `update_parallel` (en `parallel.py`) hace tres pasos:

1. **Segmentación.** `split(state.entities, n_workers)` parte la tupla de entidades en
   segmentos **contiguos** de tamaño `ceil(N / workers)`. Con 5,000 entidades y 16 workers
   salen 16 segmentos de 313 entidades (el último un poco más corto). Se usa partición
   contigua porque cada entidad se calcula de forma independiente (no depende de las demás),
   así que el reparto es parejo y se conserva el orden original.
2. **Mapeo paralelo.** Cada segmento viaja a un proceso hijo junto con los datos de solo
   lectura (`dt`, tamaño del mundo, objetivo y obstáculos). `pool.map(update_chunk, tasks)`
   ejecuta la función pura `update_chunk` en cada worker y **bloquea hasta que todos terminan**,
   que es la sincronización del pipeline.
3. **Consolidación.** Los resultados se aplanan en una nueva tupla
   (`tuple(chain.from_iterable(results))`) y se construye un `GameState` nuevo con
   `dataclasses.replace`. El estado anterior nunca se modifica.

### ¿Por qué el `Pool` se crea una sola vez?

Crear procesos es caro (en Windows se usa *spawn*, que arranca un intérprete de Python nuevo
por proceso). Si se creara un `Pool` en cada frame, el costo de arrancar procesos sería mayor
que el cálculo. Por eso `main.py` y `benchmark.py` crean el `Pool` una sola vez y lo reutilizan.

### Costo de serialización (pickle)

Los procesos no comparten memoria: cada segmento de entidades se **serializa** (pickle) para
enviarlo al worker y los resultados se serializan de vuelta. Ese costo crece con el número de
entidades pero **no se paraleliza**, y por eso la mejora no es de `N` veces con `N` núcleos.
Con pocas entidades el costo de comunicación pesa más; con más entidades hay más cálculo por
byte enviado y la mejora relativa crece.

### ¿Por qué `mp.cpu_count()` cuenta más núcleos de los físicos?

`cpu_count()` devuelve procesadores lógicos (hilos). Una CPU de 8 núcleos con
hyperthreading reporta 16.