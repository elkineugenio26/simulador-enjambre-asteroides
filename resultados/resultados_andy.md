# Resultados de benchmark - Andy Ruiz

## Hardware de prueba

- Procesador: Intel i7 9700k
- Nucleos detectados por `mp.cpu_count()`: 8 (procesadores logicos)
- Workers configurados: 8 (igual a los nucleos detectados)
- RAM: 16 GB
- Sistema operativo: Windows 11
- Python: 3.15.2

## Resultado de `python benchmark.py`

| Cantidad de Entidades | Secuencial (1 nucleo) | Paralelo (8 nucleos) |
|---|---|---|
| 1,000 entidades | 49.2 FPS | 112.9 FPS |
| 3,000 entidades | 17.4 FPS | 72.1 FPS |
| 5,000 entidades | 10.5 FPS | 43.5 FPS |

Estrategia de particion: 8 segmentos contiguos de tamano ~N/8.

Salida completa de la terminal:

    Nucleos detectados: 8 | workers: 8 | particion: 8 segmentos contiguos de tamano ~N/8

    TABLA 1: secuencial vs paralelo
     Entidades |  Secuencial (FPS) |  Paralelo (FPS)
    -------------------------------------------------
         1,000 |              49.2 |           112.9
         3,000 |              17.4 |            72.1
         5,000 |              10.5 |            43.5

    TABLA 2: FPS segun numero de workers (5,000 entidades)
     Workers |      FPS
    --------------------
           1 |      7.6
           2 |     15.0
           4 |     27.2
           8 |     43.4

    Mejor configuracion: 8 workers (43.4 FPS)

## Observaciones

- El paralelo fue mas rapido que el secuencial en las tres cargas: con 1,000 entidades
  paso de 49.2 a 112.9 FPS (~2.3x), con 3,000 de 17.4 a 72.1 FPS (~4.1x) y con 5,000
  de 10.5 a 43.5 FPS (~4.1x).
- La mejora es menor con 1,000 entidades porque hay poco calculo por frame. Cada frame
  hay que serializar (pickle) las entidades, enviarlas a los procesos hijos y traer los
  resultados de vuelta. Ese costo de comunicacion es casi fijo y pesa mas cuando el
  calculo es pequeno. Con 3,000 y 5,000 entidades hay mas trabajo por cada dato enviado
  y el paralelo aprovecha mejor los nucleos.
- Con 8 workers no se llega a 8 veces mas rapido (de 7.6 a 43.4 FPS, unas 5.7 veces)
  por tres razones: la serializacion entre procesos no se paraleliza, la segmentacion y
  la consolidacion de resultados las hace un solo proceso, y pool.map espera al worker
  mas lento antes de seguir.
- Al duplicar los workers los FPS casi se duplican de 1 a 2 (7.6 a 15.0) y de 2 a 4
  (15.0 a 27.2), pero la ganancia se reduce de 4 a 8 (27.2 a 43.4). Cada worker extra
  aporta menos porque aumenta el costo de comunicacion y los nucleos detectados son
  procesadores logicos (hilos), no necesariamente nucleos fisicos.
- La mejor configuracion fue usar los 8 workers (43.4 FPS con 5,000 entidades).