# FAQ - Preguntas y respuestas para evaluacion

---

## Sobre el N-Puzzle

### Que es el N-Puzzle?
Es un juego con un tablero cuadrado (por ejemplo 3x3) con numeros y un hueco. El objetivo es ordenar las piezas deslizandolas hacia el hueco.

### Por que se llama N-Puzzle?
Porque el tamano del tablero es NxN. El mas conocido es el 15-puzzle (4x4 = 16 casillas, 15 numeros + 1 hueco).

### Cual es el estado objetivo?
Los numeros en forma de espiral (snail), recorriendo el borde en sentido horario hasta el centro, donde queda el hueco (0).

### Por que en espiral y no en orden simple?
Es la convencion del proyecto. El tablero objetivo se genera rellenando el borde exterior y luego moviendose hacia adentro.

---

## Sobre la solubilidad

### Todos los puzzles tienen solucion?
No. Si mezclas las piezas al azar, exactamente la mitad de las configuraciones son imposibles de resolver.

### Como se sabe si un puzzle tiene solucion?
Se calcula el numero de **inversiones** (pares de fichas donde una mayor aparece antes que una menor, ignorando el 0).

- **Tamano impar** (3x3, 5x5): `inversiones % 2`
- **Tamano par** (4x4, 6x6): `(inversiones + fila del hueco) % 2`

Si el resultado coincide con el del tablero objetivo, tiene solucion.

### Que es una inversion?
Es un par de fichas (a, b) donde `a` aparece antes que `b` en el tablero (leyendo de izquierda a derecha, arriba a abajo) pero `a > b`.

```
Ejemplo: [3, 1, 2] -> 2 inversiones: (3,1) y (3,2)
```

### Por que funciona el calculo de inversiones?
Porque cada movimiento legal (deslizar una pieza) cambia el numero de inversiones de forma predecible. Es un **invariante matematico**: dos tableros son alcanzables entre si si y solo si tienen el mismo invariante.

### Como generas puzzles que SI tengan solucion?
Parto del tablero objetivo y doy N movimientos aleatorios legales. Como cada movimiento es reversible, el resultado siempre es solucionable.

---

## Sobre las heuristicas

### Que es una heuristica?
Es una funcion que **estima cuantos movimientos faltan** para llegar al objetivo, sin conocer la solucion exacta. Es como un "instinto" que guia la busqueda.

### Que significa que una heuristica sea "admisible"?
Que **nunca sobreestima** el coste real. Siempre devuelve un valor menor o igual al numero real de movimientos necesarios.

### Por que es importante que sea admisible?
Porque A* garantiza encontrar la solucion optima (la mas corta) solo si la heuristica es admisible. Si sobreestima, podria saltarse la solucion optima.

### Que heuristicas usas?
1. **Manhattan Distance**: suma de distancias horizontales + verticales de cada ficha a su posicion objetivo.
2. **Misplaced Tiles**: cuenta cuantas fichas no estan en su sitio.
3. **Linear Conflict**: Manhattan + penalizacion por fichas que se bloquean en la misma fila/columna.

### Cual es la mejor heuristica?
**Linear Conflict** es la mas precisa (estima mejor la distancia real), lo que hace que A* explore menos nodos y sea mas rapido.

### Que es la distancia Manhattan?
Para cada ficha, calcula `|fila_actual - fila_objetivo| + |columna_actual - columna_objetivo|`. Es la distancia si solo pudieras moverte en horizontal y vertical (como en una cuadricula de calles).

### Que es un conflicto lineal?
Cuando dos fichas estan en la misma fila (o columna) que les corresponde, pero en orden invertido. Una bloquea a la otra, lo que obliga a hacer movimientos extra. Se penaliza con +2 por cada par en conflicto.

---

## Sobre los algoritmos

### Que es A* (A-estrella)?
Es un algoritmo de busqueda que combina:
- `g(n)`: coste real desde el inicio (movimientos hechos)
- `h(n)`: estimacion de lo que falta (heuristica)
- `f(n) = g(n) + h(n)`: coste total estimado

Siempre expande el nodo con menor `f`.

### Por que A* encuentra la solucion optima?
Porque si la heuristica es admisible (nunca sobreestima), A* nunca se saltara un camino mejor. Cuando llega al objetivo, ese camino es el mas corto.

### Que diferencia hay entre A*, Greedy y Costo Uniforme?

| Algoritmo     | Funcion de prioridad | Garantiza optimo | Velocidad |
|---------------|----------------------|------------------|-----------|
| A*            | f = g + h            | Si               | Media     |
| Greedy        | f = h                | No               | Rapida    |
| Costo Uniforme| f = g                | Si               | Lenta     |

- **A***: equilibrio entre coste real y estimacion.
- **Greedy**: solo mira la heuristica, es rapido pero puede dar rodeos.
- **Costo Uniforme**: solo mira el coste acumulado, explora todo (como Dijkstra).

### Que es un nodo en el arbol de busqueda?
Es un estado del puzzle junto con su historial:
- `board`: el tablero en ese momento
- `parent`: el nodo del que venimos
- `g`: movimientos hechos hasta aqui
- `h`: estimacion de lo que falta

### Como reconstruyes la solucion?
Cada nodo guarda un puntero a su `parent`. Cuando encuentro el objetivo, sigo los punteros hacia atras hasta el inicio, y luego invierto la lista para obtener el camino desde el principio.

### Que es el open set y el closed set?
- **Open set**: cola de prioridad con los nodos pendientes de explorar (ordenados por `f`).
- **Closed set**: conjunto de nodos ya visitados (para no repetir trabajo).

En nuestro codigo usamos un diccionario `g_best` que guarda el mejor coste conocido para cada estado, lo que permite re-abrir nodos si encontramos un camino mejor.

### Que es la complejidad temporal y espacial?
- **Complejidad temporal**: numero total de nodos abiertos durante la busqueda.
- **Complejidad espacial**: maximo numero de nodos en memoria simultaneamente.

---

## Sobre el parser

### Que formato tiene el archivo de entrada?
```
# Comentario (se ignora)
3              <- tamano del tablero
3 2 6          <- fila 1
1 4 0          <- fila 2
8 7 5          <- fila 3
```

### Que validaciones hace el parser?
1. El archivo existe y es legible
2. No esta vacio (o solo tiene comentarios)
3. El tamano es un numero entre 1 y 20
4. Hay suficientes filas de fichas
5. Todos los tokens son numeros
6. Hay exactamente size x size fichas
7. No hay duplicados
8. Estan todos los numeros de 0 a size^2 - 1

### Que pasa si el archivo tiene errores?
Se lanza una excepcion `PuzzleError` con un mensaje descriptivo que se muestra por stderr.

---

## Sobre la ejecucion

### Como se ejecuta el programa?
```bash
# Resolver un puzzle desde archivo
python -m src.main -f puzzles/3x3.txt

# Generar y resolver un puzzle aleatorio
python -m src.main -g 4

# Con heuristica especifica
python -m src.main -f puzzles/3x3.txt -H linear_conflict

# Solo comprobar solubilidad
python -m src.main -f puzzles/3x3.txt -s
```

### Que significa el flag -w (weight)?
Es el peso de la heuristica en A*: `f = g + w*h`.
- `w = 1`: A* estandar, solucion optima.
- `w > 1`: da mas peso a la heuristica, es mas rapido pero NO garantiza solucion optima.

### Que pasa si el puzzle es muy grande y tarda mucho?
Puedes usar `--max-nodes N` para limitar el numero de estados que se exploran. Si se supera el limite, el programa se detiene y sugiere usar un peso mayor o un algoritmo mas rapido.

---

## Preguntas conceptuales

### Por que usas tuplas en vez de listas para guardar el tablero?
Porque las tuplas son **inmutables** en Python. Esto permite:
- Comparar tableros con `==` de forma eficiente
- Usar tableros como claves de diccionario o en conjuntos (`set`)
- Calcular un hash una sola vez y reutilizarlo

### Por que A* es mejor que una busqueda en anchura (BFS)?
Porque A* usa una heuristica para dirigir la busqueda hacia el objetivo, en vez de explorar todos los nodos por igual. Esto reduce enormemente el numero de nodos explorados.

### Que pasa si la heuristica es 0?
A* se convierte en Costo Uniforme (o Dijkstra), que explora todos los nodos por orden de coste. Es optimo pero muy lento.

### Se puede usar A* sin heuristica?
Si, pero seria equivalente a Costo Uniforme. La heuristica es lo que hace que A* sea eficiente.

### Que es una heuristica consistente?
Ademas de ser admisible, cumple que `h(n) <= coste(n -> n') + h(n')`. Esto garantiza que A* no necesita re-abrir nodos ya expandidos. Manhattan y Linear Conflict son consistentes.

### Por que Linear Conflict no es consistente?
En realidad, en nuestra implementacion Linear Conflict SI es admisible pero puede no ser consistente en algunos casos edge, por lo que permitimos re-abrir nodos si encontramos un camino mejor (usando `g_best`).

---

## Sobre el rendimiento

### Que heuristicas es mas rapida en la practica?
Linear Conflict, porque estima mejor la distancia real y A* explora menos nodos.

### Que algoritmo es mas rapido?
Greedy es el mas rapido (solo mira la heuristica), pero no garantiza la solucion mas corta.

### Se puede resolver un puzzle 17x17?
Se puede comprobar si es solucionable (con el calculo de inversiones), pero resolverlo con A* puede tardar mucho tiempo y consumir mucha memoria. Para puzzles grandes, se recomienda usar un peso mayor (`-w 1.5`) o el algoritmo Greedy.

### Cuanta memoria consume el programa?
Depende del tamano del puzzle y de cuantos nodos se exploran. Cada nodo guarda el tablero (una tupla de size^2 elementos) y un puntero al padre. Para puzzles pequenos (3x3, 4x4) el consumo es minimo. Para puzzles grandes (8x8+) puede crecer mucho.

---

## Errores comunes

### "UNSOLVABLE"
El puzzle no tiene solucion. Se detecta con el calculo de inversiones.

### "File not found"
El archivo especificado no existe.

### "Invalid token"
El archivo contiene caracteres que no son numeros (excepto comentarios con #).

### "Duplicate tile values"
Hay numeros repetidos en el tablero.

### "Missing tile values"
Faltan numeros en el rango de 0 a size^2 - 1.

### "Search aborted"
Se supero el limite de nodos abiertos (--max-nodes). Prueba con un peso mayor o un algoritmo mas rapido.
