# N-Puzzle

![Python](https://img.shields.io/badge/Python-3.8+-blue)

Un solucionador del clásico juego **N-Puzzle** (también conocido como *15-puzzle* o *juego del 15*). El programa recibe un tablero desordenado y encuentra la secuencia óptima de movimientos para resolverlo usando el algoritmo **A\*** con heurísticas personalizables.

---

## Tabla de contenidos

1. [¿Qué es el N-Puzzle?](#1-qué-es-el-n-puzzle)
2. [Estructura del proyecto](#2-estructura-del-proyecto)
3. [Paso 1: El tablero (`board.py`)](#3-paso-1-el-tablero-boardpy)
4. [Paso 2: ¿Se puede resolver? (`generator.py`)](#4-paso-2-se-puede-resolver-generatorpy)
5. [Paso 3: Las heurísticas (`heuristics.py`)](#5-paso-3-las-heurísticas-heuristicspy)
6. [Paso 4: El solucionador (`solver.py`)](#6-paso-4-el-solucionador-solverpy)
7. [Paso 5: Leer archivos de puzzle (`parser.py`)](#7-paso-5-leer-archivos-de-puzzle-parserpy)
8. [Paso 6: El programa principal (`main.py`)](#8-paso-6-el-programa-principal-mainpy)
9. [Paso 7: Los tests (`tests/test_npuzzle.py`)](#9-paso-7-los-tests-teststest_npuzzlepy)
10. [Cómo ejecutar el proyecto](#10-cómo-ejecutar-el-proyecto)
11. [Glosario de conceptos clave](#11-glosario-de-conceptos-clave)

---

## 1. ¿Qué es el N-Puzzle?

Imagina un tablero cuadrado con casillas numeradas y **un hueco vacío**. El objetivo es deslizar las piezas para ordenarlas. Solo puedes mover una pieza adyacente al hueco (arriba, abajo, izquierda, derecha) para que ocupe el espacio vacío.

```
Estado inicial (3x3):       Estado objetivo (3x3):
┌───┬───┬───┐              ┌───┬───┬───┐
│ 3 │ 2 │ 6 │              │ 1 │ 2 │ 3 │
├───┼───┼───┤              ├───┼───┼───┤
│ 1 │ 4 │   │              │ 8 │   │ 4 │
├───┼───┼───┤              ├───┼───┼───┤
│ 8 │ 7 │ 5 │              │ 7 │ 6 │ 5 │
└───┴───┴───┘              └───┴───┴───┘

¿Cómo llegar del desorden al orden?
→ El programa lo calcula automáticamente.
```

El objetivo estándar usa una **espiral (snail)** que recorre el borde del tablero en sentido horario hasta llegar al centro, donde se sitúa el hueco (0).

---

## 2. Estructura del proyecto

```
n-puzzle/
├── Makefile                  ← Comandos rápidos (make run, make test)
├── README.md                 ← Este archivo
├── puzzles/                  ← Archivos de puzzles de ejemplo
│   ├── 3x3-1.txt
│   ├── 4x4-1.txt
│   └── solvable-3x3.txt
├── src/                      ← Código fuente
│   ├── __init__.py           ← Hace que src/ sea un paquete Python
│   ├── board.py              ← Representación del tablero
│   ├── generator.py          ← Generación de puzzles y verificación de solubilidad
│   ├── heuristics.py         ← Funciones heurísticas (estimación de distancia al objetivo)
│   ├── main.py               ← Punto de entrada del programa
│   ├── parser.py             ← Lector de archivos de puzzle
│   └── solver.py             ← Algoritmos de búsqueda (A*, Greedy, Costo Uniforme)
└── tests/
    └── test_npuzzle.py        ← Tests unitarios
```

---

## 3. Paso 1: El tablero (`board.py`)

El corazón del programa. La clase `Board` representa **un estado del puzzle** en un momento dado.

### ¿Qué guarda un Board?

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `size` | `int` | Tamaño del tablero (3 = 3x3, 4 = 4x4...) |
| `tiles` | `tuple` | Las fichas en orden, de izquierda a derecha y de arriba a abajo |
| `_blank_pos` | `int` | Índice (posición dentro de la tupla) donde está el hueco (0) |
| `_hash` | `int` | Hash precalculado (para usar Boards en conjuntos y diccionarios) |

**¿Por qué una tupla y no una lista?** Porque las tuplas en Python son **inmutables** (no se pueden modificar). Esto permite que dos tableros iguales tengan el mismo hash y se puedan usar como claves de diccionario o almacenarse en conjuntos (`set`), lo cual es fundamental para el algoritmo de búsqueda.

### Ejemplo visual

```python
# Este tablero:
#   1  2  3
#   8  0  4
#   7  6  5
board = Board(3, [1, 2, 3, 8, 0, 4, 7, 6, 5])
```

Se almacena como `tiles = (1, 2, 3, 8, 0, 4, 7, 6, 5)`. El `0` está en el índice 4 (segunda fila, segunda columna).

### Métodos principales

#### `get_neighbors()`
Genera todos los tableros alcanzables en **un solo movimiento**. El hueco puede moverse en 4 direcciones, pero no siempre las 4 son válidas (si el hueco está en un borde, no puede moverse hacia afuera).

```python
# Si el hueco está en el centro (índice 4 en un 3x3):
# Puede moverse: arriba (swap con índice 1), abajo (7),
#                izquierda (3), derecha (5) → 4 vecinos

# Si el hueco está en la esquina superior izquierda (índice 0):
# Solo puede moverse: abajo (3) y derecha (1) → 2 vecinos
```

Las comprobaciones de límites se hacen con aritmética modular:
- `pos >= n` → puede moverse arriba
- `pos < n*n - n` → puede moverse abajo
- `pos % n != 0` → puede moverse izquierda (no está en la columna 0)
- `pos % n != n - 1` → puede moverse derecha (no está en la última columna)

#### `generate_goal(size)`
Método **estático** que genera el tablero objetivo en forma de **espiral (snail)**:

```
Para size=3:            Para size=4:
 1  2  3                1  2  3  4
 8  0  4               12 13 14  5
 7  6  5               11  0 15  6
                       10  9  8  7
```

El algoritmo rellena el borde exterior con números crecientes (arriba →, derecha ↓, abajo ←, izquierda ↑) y luego se mueve un nivel hacia adentro, repitiendo hasta llenar todo.

#### `display()`
Imprime el tablero de forma legible:
```
 1  2  3
 8  0  4
 7  6  5
```

---

## 4. Paso 2: ¿Se puede resolver? (`generator.py`)

**No todos los puzzles tienen solución.** Si mezclas las piezas al azar, exactamente la mitad de las configuraciones son imposibles de resolver.

### El invariante de paridad

La solubilidad se determina con un **invariante matemático**:

#### `_count_inversions(tiles)`
Una **inversión** es un par de fichas `(a, b)` donde `a` aparece antes que `b` en el tablero pero `a > b`. Por ejemplo, en `[3, 1, 2]` hay 2 inversiones: `(3,1)` y `(3,2)`.

#### `_invariant(board)`
- **Tablero impar** (3x3, 5x5...): `invariante = inversiones % 2` (par o impar)
- **Tablero par** (4x4, 6x6...): `invariante = (inversiones + fila_del_hueco) % 2`

Dos tableros del mismo tamaño son **alcanzables entre sí** si y solo si tienen el mismo invariante.

```python
# Ejemplo: ¿Es solvable un tablero 3x3?
# 1. Contar inversiones (ignorando el 0)
# 2. Como 3 es impar: invariante = inversiones % 2
# 3. Comparar con el invariante del tablero objetivo
# 4. Si coinciden → ¡tiene solución!
```

#### `generate_puzzle(size)`
Genera un puzzle aleatorio **garantizando que sea solucionable**: baraja las fichas al azar en un bucle y comprueba `is_solvable()` hasta que el invariante coincida.

---

## 5. Paso 3: Las heurísticas (`heuristics.py`)

Una **heurística** es una función que **estima cuántos movimientos faltan** para llegar al objetivo, sin saber la solución exacta. Es el "instinto" que guía al algoritmo.

Cuanto mejor sea la estimación (sin pasarse), más rápido encontrará la solución.

### Heurística 1: Distancia Manhattan (`manhattan_distance`)

Para cada ficha, calcula cuántas casillas horizontales + verticales le faltan para llegar a su posición objetivo.

```
Ejemplo: ficha "5" en posición (2,0), objetivo en (2,2)
→ |2-2| + |0-2| = 0 + 2 = 2 movimientos de distancia
```

**Propiedad**: Es **admisible** (nunca sobreestima) y **consistente** → garantiza solución óptima con A\*.

### Heurística 2: Fichas mal colocadas (`misplaced_tiles`)

Simplemente cuenta cuántas fichas NO están en su posición correcta.

```
Si 4 fichas están fuera de sitio → estimación = 4
```

Más simple pero menos precisa que Manhattan.

### Heurística 3: Conflicto lineal (`linear_conflict`)

Empieza con la distancia Manhattan y le **suma 2** por cada par de fichas que están en la misma fila (o columna) que les corresponde, pero en orden invertido: una bloquea a la otra.

```
Fila objetivo: [1, 2, 3]
Fila actual:   [3, 1, 2]
→ 3 está antes que 1 pero debería ir después → conflicto (+2)
→ 3 está antes que 2 pero debería ir después → conflicto (+2)
→ Total: manhattan + 4
```

Es la más informativa de las tres (más precisa) y también es admisible.

### Tabla comparativa

| Heurística | Precisión | Velocidad | Garantiza óptimo |
|------------|-----------|-----------|:-----------------:|
| Misplaced  | Baja      | Lenta     | Sí |
| Manhattan  | Media     | Media     | Sí |
| Linear Conflict | Alta | Rápida | Sí |

---

## 6. Paso 4: El solucionador (`solver.py`)

Aquí está la **inteligencia** del programa. Implementa tres algoritmos de búsqueda.

### Concepto previo: ¿qué es un nodo?

La clase `Node` representa un **estado en el árbol de búsqueda**:

| Atributo | Significado |
|----------|-------------|
| `board` | El tablero en este momento |
| `parent` | El nodo del que venimos (para reconstruir el camino) |
| `g` | **Coste acumulado** desde el inicio (cuántos movimientos llevamos) |
| `h` | **Valor heurístico** (estimación de lo que falta) |
| `f` | `g + h` (coste total estimado del camino) |

### Algoritmo 1: A\* (A-estrella) — `a_star`

El algoritmo **estrella** del proyecto. Combina lo mejor de dos mundos:

```
f(n) = g(n) + h(n)
  │      │      │
  │      │      └── Estimación de lo que falta (heurística)
  │      └── Movimientos que ya hemos hecho (coste real)
  └── Coste total estimado de la solución pasando por este nodo
```

**Funcionamiento:**
1. Meter el tablero inicial en una cola de prioridad (ordenada por `f` más bajo)
2. Sacar el nodo con menor `f`
3. Si es el objetivo → ¡resuelto! Reconstruir el camino hacia atrás
4. Si no → marcar como visitado (`closed_set`) y generar sus vecinos
5. Para cada vecino: si no se ha visitado antes (o se ha llegado por un camino más corto), añadirlo a la cola
6. Volver al paso 2

**Garantiza la solución óptima** (mínimo número de movimientos) siempre que la heurística sea admisible.

### Algoritmo 2: Greedy (Voraz) — `greedy`

Ordena los nodos **solo por `h`** (ignorando `g`). Siempre se mueve hacia lo que "parece más cerca" del objetivo.

- **Ventaja**: Puede ser rapidísimo
- **Desventaja**: NO garantiza la solución más corta (puede dar muchos rodeos)

### Algoritmo 3: Costo Uniforme — `uniform_cost`

Ordena los nodos **solo por `g`** (coste acumulado, `h = 0`). Explora por "capas" de profundidad creciente.

- Es básicamente el algoritmo de Dijkstra
- Garantiza óptimo pero es **extremadamente lento** para puzzles grandes (explora todo)

### ¿Cómo reconstruye la solución?

La función `reconstruct_path(node)` toma el nodo objetivo y va subiendo por los punteros `parent` hasta llegar al inicio. Luego invierte la lista para obtener el camino desde el principio hasta el final.

### ¿Qué significan las estadísticas?

| Estadística | Significado |
|-------------|-------------|
| `time_complexity` | Total de nodos abiertos durante la búsqueda |
| `size_complexity` | Máximo número de nodos en memoria simultáneamente |
| `moves` | Número de movimientos de la solución encontrada |

---

## 7. Paso 5: Leer archivos de puzzle (`parser.py`)

Convierte un archivo de texto en un tablero.

### Formato del archivo
```
# Esto es un comentario (se ignora)
3          ← tamaño del tablero
3 2 6      ← primera fila
1 4 0      ← segunda fila  (# también se ignoran comentarios en línea)
8 7 5      ← tercera fila
```

### ¿Qué hace el parser?
1. Intenta abrir el archivo y **distingue el tipo de error**:
   - `FileNotFoundError` → `"File not found: '...'"`
   - `PermissionError` → `"Permission denied: '...'"`
   - Otros errores de I/O → mensaje descriptivo
2. Elimina comentarios (todo lo que va después de `#`)
3. Limpia líneas vacías. Si no queda contenido → error `"File is empty or contains only comments"`
4. La primera línea no vacía es el tamaño. Si no es un número entero ≥ 2 → error descriptivo
5. El resto de líneas contienen números. Si algún token no es numérico → error indicando el nº de línea
6. Valida que haya exactamente `size × size` números → si no, indica la diferencia
7. Valida que **no haya duplicados** → lista los valores repetidos
8. Valida que estén **todos los números** de `0` a `size² - 1` → lista los faltantes
9. Valida que no haya **valores fuera de rango** → lista los inválidos
10. Si todo es correcto, devuelve un `Board`

Todos los errores se lanzan como `PuzzleError` (excepción personalizada) con un mensaje descriptivo que se muestra al usuario por stderr.

---

## 8. Paso 6: El programa principal (`main.py`)

Punto de entrada que conecta todas las piezas mediante línea de comandos.

```
python -m src.main -f puzzles/3x3-1.txt -H manhattan -a a_star
                   │                      │            │
                   │                      │            └── Algoritmo
                   │                      └── Heurística
                   └── Archivo de entrada
```

### Flujo de ejecución

```
1. Leer argumentos ──→ ¿Archivo (-f)? ──sí──→ parser.parse_input() [con validación completa]
        │                                    └── Si hay error → mensaje descriptivo en stderr + exit(1)
        └─→ ¿Generar (-g)? ──sí──→ generator.generate_puzzle()

2. Mostrar tablero inicial

3. ¿Es solucionable? ──no──→ "UNSOLVABLE" (fin)

4. ¿Flag -s? ──sí──→ "This puzzle is solvable" (fin)

5. Seleccionar heurística y algoritmo → solver.solve()

6. Mostrar solución paso a paso + estadísticas + tiempo
```

### Opciones de línea de comandos

| Flag | Descripción | Ejemplo |
|------|-------------|---------|
| `-f`, `--file` | Archivo con el puzzle | `-f puzzles/3x3-1.txt` |
| `-g`, `--generate` | Generar puzzle aleatorio de tamaño N | `-g 4` |
| `-H`, `--heuristic` | Heurística: `manhattan`, `misplaced`, `linear_conflict` | `-H linear_conflict` |
| `-a`, `--algorithm` | Algoritmo: `a_star`, `greedy`, `uniform_cost` | `-a greedy` |
| `-s`, `--solvable` | Solo comprobar si es solucionable (no resolver) | `-s` |

---

## 9. Paso 7: Los tests (`tests/test_npuzzle.py`)

Verifican que cada parte del código funciona correctamente.

### TestBoard — ¿Funciona bien el tablero?
- El objetivo 3x3 y 4x4 tienen la forma espiral correcta
- Un tablero con el hueco en el centro genera 4 vecinos
- Dos tableros iguales son considerados el mismo objeto

### TestSolvability — ¿Detecta bien la solubilidad?
- El tablero objetivo siempre es solucionable
- 20 puzzles aleatorios son todos solucionables
- Un puzzle concreto del enunciado es correctamente identificado
- Puzzles solucionables realmente se resuelven con A\*

### TestHeuristics — ¿Las heurísticas son correctas?
- En el estado objetivo, las 3 heurísticas devuelven 0
- A un movimiento del objetivo, Manhattan devuelve 1
- Las 3 heurísticas están registradas en el diccionario `HEURISTICS`
- Las heurísticas son admisibles (no sobreestiman el coste real)

### TestParser — ¿Lee bien los archivos?
- Lee correctamente el archivo de ejemplo y obtiene el tamaño esperado
- Lanza `PuzzleError` para archivos que no existen (con mensaje descriptivo)

### TestSolver — ¿Resuelve correctamente?
- Un puzzle ya resuelto devuelve 0 movimientos
- Los tres algoritmos (A\*, Greedy, Costo Uniforme) encuentran solución

---

## 10. Cómo ejecutar el proyecto

### Requisitos

- Python 3.8 o superior
- Nada más — **no necesita instalar dependencias externas**

### Comandos rápidos (Makefile)

```bash
# Resolver un puzzle desde archivo (A* con Manhattan por defecto)
make run ARGS="-f puzzles/3x3-1.txt"

# Generar y resolver un puzzle aleatorio 4x4 con Linear Conflict
make run ARGS="-g 4 -H linear_conflict"

# Solo comprobar si un puzzle es solucionable
make run ARGS="-f puzzles/3x3-1.txt -s"

# Usar el algoritmo voraz (greedy)
make run ARGS="-f puzzles/3x3-1.txt -a greedy -H misplaced"

# Ejecutar todos los tests
make test

# Limpiar archivos temporales
make clean
```

### Sin Makefile (Windows / comandos directos)

```powershell
# Resolver un puzzle
python -m src.main -f puzzles/3x3-1.txt

# Con heurística específica
python -m src.main -f puzzles/4x4-1.txt -H linear_conflict -a a_star

# Generar puzzle aleatorio
python -m src.main -g 3

# Ejecutar tests
python -m pytest tests/ -v
```

---

## 11. Glosario de conceptos clave

| Término | Explicación |
|---------|-------------|
| **N-Puzzle** | Juego de deslizar piezas numeradas en un tablero cuadrado con un hueco |
| **Heurística** | Función que estima la distancia al objetivo. Guía la búsqueda sin conocer la solución |
| **Heurística admisible** | Aquella que **nunca sobreestima** el coste real. Necesaria para que A\* encuentre la solución óptima |
| **Heurística consistente** | Además de admisible, cumple que `h(n) ≤ coste(n→n') + h(n')`. Garantiza que A\* no re-expanda nodos |
| **A\*** | Algoritmo de búsqueda que combina coste real (`g`) + heurística (`h`). Encuentra la solución óptima si la heurística es admisible |
| **Greedy** | Algoritmo voraz que solo mira la heurística (`h`). Rápido pero no garantiza optimalidad |
| **Costo Uniforme** | Algoritmo que solo mira el coste acumulado (`g`). Equivalente a Dijkstra. Óptimo pero muy lento |
| **Inversión** | Par de fichas `(a,b)` donde `a` está antes que `b` pero `a > b` |
| **Invariante de paridad** | Fórmula matemática que determina si un puzzle es resoluble |
| **Distancia Manhattan** | Suma de diferencias absolutas en fila y columna entre posición actual y objetivo: `|x1-x2| + |y1-y2|` |
| **Conflicto lineal** | Dos fichas en la misma fila/columna que se bloquean mutuamente por estar en orden inverso |
| **Snail (espiral)** | Patrón del tablero objetivo: los números recorren el borde en espiral hacia el centro |
| **Nodo** | Un estado del puzzle junto con su historial (padre, coste, heurística) en el árbol de búsqueda |
| **Open set** | Cola de prioridad con los nodos pendientes de explorar |
| **Closed set** | Conjunto de nodos ya visitados (para no repetir trabajo) |
