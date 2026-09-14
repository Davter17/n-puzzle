# Como funciona el N-Puzzle Solver

---

## 1. Que es el N-Puzzle

Es un juego con un tablero cuadrado (por ejemplo 3x3 = 9 casillas) donde hay numeros del 1 al 8 y un hueco (representado con 0). El objetivo es mover las piezas deslizandolas hasta dejarlas en orden.

```
Estado inicial:        Estado objetivo (espiral):
 3  2  6                1  2  3
 1  4  0                8  0  4
 8  7  5                7  6  5
```

Solo puedes mover una pieza que este al lado del hueco (arriba, abajo, izquierda o derecha).

---

## 2. Estructura del proyecto

```
src/
  board.py         -> Representa el tablero
  generator.py     -> Genera puzzles y comprueba si tienen solucion
  heuristics.py    -> Funciones que estiman la distancia al objetivo
  solver.py        -> Algoritmos de busqueda (A*, Greedy, Costo Uniforme)
  parser.py        -> Lee archivos de texto con puzzles
  main.py          -> Programa principal (linea de comandos)
```

---

## 3. El tablero (board.py)

La clase `Board` guarda el estado del puzzle:
- `size`: tamano del tablero (3 = 3x3)
- `tiles`: las fichas como tupla (inmutable, para poder comparar tableros)
- `_blank_pos`: donde esta el hueco (el 0)

### Movimientos posibles

El metodo `get_neighbors()` genera todos los tableros que se pueden alcanzar en un movimiento. El hueco puede moverse en 4 direcciones, pero no siempre las 4 son validas (si esta en una esquina, solo puede moverse en 2 direcciones).

### Tablero objetivo (espiral / snail)

El objetivo no es simplemente los numeros en orden. Se genera en forma de espiral:

```
3x3:                 4x4:
 1  2  3              1  2  3  4
 8  0  4             12 13 14  5
 7  6  5             11  0 15  6
                     10  9  8  7
```

Los numeros recorren el borde en sentido horario y van hacia el centro.

---

## 4. Solubilidad (generator.py)

No todos los puzzles tienen solucion. Si mezclas las piezas al azar, la mitad son imposibles.

### Como se comprueba

Se usa un calculo matematico basado en **inversiones**:

- Una **inversion** es cuando una ficha mayor aparece antes que una menor (leyendo el tablero de izquierda a derecha, arriba a abajo), ignorando el 0.

```
Ejemplo: [3, 1, 2] -> 2 inversiones: (3,1) y (3,2)
```

La formula depende del tamano:
- **Tamano impar** (3x3, 5x5): `inversiones % 2`
- **Tamano par** (4x4, 6x6): `(inversiones + fila del hueco) % 2`

Si el resultado del puzzle inicial coincide con el del objetivo, tiene solucion. Si no, es imposible.

### Generacion de puzzles

Para generar un puzzle aleatorio que SI tenga solucion:
1. Se parte del tablero objetivo
2. Se dan N movimientos aleatorios legales (deslizando piezas adyacentes al hueco)
3. Como cada movimiento es reversible, el resultado siempre es solucionable

---

## 5. Las heuristicas (heuristics.py)

Una heuristica es una funcion que **estima cuantos movimientos faltan** para llegar al objetivo. No sabe la solucion exacta, pero da una estimacion para guiar la busqueda.

### Manhattan Distance

Para cada ficha, suma la distancia horizontal + vertical hasta su posicion objetivo.

```
Ficha "5" en (2,0), objetivo en (2,2):
  |2-2| + |0-2| = 0 + 2 = 2
```

Es **admisible**: nunca sobreestima el coste real.

### Fichas mal colocadas (Misplaced)

Cuenta cuantas fichas NO estan en su posicion correcta. Mas simple pero menos precisa.

### Conflicto lineal (Linear Conflict)

Empieza con Manhattan y suma +2 por cada par de fichas que estan en la misma fila (o columna) que les corresponde, pero en orden invertido (una bloquea a la otra).

```
Fila objetivo: [1, 2, 3]
Fila actual:   [3, 1, 2]
  -> 3 bloquea a 1 y a 2 -> +4
```

Es la mas precisa de las tres.

### Comparacion

| Heuristica       | Precision | Velocidad |
|------------------|-----------|-----------|
| Misplaced        | Baja      | Lenta     |
| Manhattan        | Media     | Media     |
| Linear Conflict  | Alta      | Rapida    |

---

## 6. Los algoritmos de busqueda (solver.py)

### Concepto: el nodo

Cada estado del puzzle se representa como un nodo con:
- `board`: el tablero
- `parent`: de donde venimos (para reconstruir el camino)
- `g`: movimientos hechos hasta aqui
- `h`: estimacion de lo que falta (heuristica)
- `f = g + h`: coste total estimado

### A* (A-estrella) - el principal

```
f(n) = g(n) + h(n)
```

1. Mete el tablero inicial en una cola de prioridad (ordenada por `f` mas bajo)
2. Saca el nodo con menor `f`
3. Si es el objetivo -> reconstruye el camino y termina
4. Si no -> genera sus vecinos y los mete en la cola
5. Repite

**Garantiza la solucion optima** (minimo numero de movimientos) si la heuristica es admisible.

### Greedy (Voraz)

Solo ordena por `h` (ignora `g`). Siempre va hacia lo que "parece mas cerca".
- Rapido, pero NO garantiza la solucion mas corta.

### Costo Uniforme

Solo ordena por `g` (h = 0). Explora por capas de profundidad.
- Garantiza optimo, pero es muy lento (explora todo).

---

## 7. El parser (parser.py)

Lee un archivo de texto y lo convierte en un tablero.

### Formato del archivo

```
# Esto es un comentario (se ignora)
3              <- tamano
3 2 6          <- fila 1
1 4 0          <- fila 2
8 7 5          <- fila 3
```

### Validaciones que hace

1. El archivo existe y es legible
2. No esta vacio
3. El tamano es un numero entre 1 y 20
4. Hay suficientes filas de fichas
5. Todos los tokens son numeros
6. Hay exactamente size x size fichas
7. No hay duplicados
8. Estan todos los numeros de 0 a size^2 - 1

---

## 8. El programa principal (main.py)

### Flujo de ejecucion

```
1. Leer argumentos de linea de comandos
2. Cargar puzzle (desde archivo o generarlo)
3. Mostrar tablero inicial
4. Comprobar si es solucionable -> si no, "UNSOLVABLE"
5. Si flag -s -> solo dice "solvable" y termina
6. Elegir heuristica y algoritmo
7. Resolver con A* (o el algoritmo elegido)
8. Mostrar solucion paso a paso + estadisticas
```

### Opciones principales

| Flag | Que hace |
|------|----------|
| `-f archivo` | Cargar puzzle desde archivo |
| `-g N` | Generar puzzle aleatorio de tamano N |
| `-H heuristica` | Elegir heuristica (manhattan, misplaced, linear_conflict) |
| `-a algoritmo` | Elegir algoritmo (a_star, greedy, uniform_cost) |
| `-s` | Solo comprobar si es solucionable |
| `-w peso` | Peso de A* (1 = optimo, >1 = mas rapido pero no optimo) |

### Ejemplos de uso

```bash
# Resolver un puzzle desde archivo
python -m src.main -f puzzles/3x3.txt

# Generar y resolver un puzzle aleatorio
python -m src.main -g 4

# Con heuristica especifica
python -m src.main -f puzzles/4x4.txt -H linear_conflict

# Solo comprobar solubilidad
python -m src.main -f puzzles/3x3.txt -s
```

---

## 9. Resumen del flujo completo

```
Archivo de texto
      |
      v
  parser.py  -->  Board (tablero)
      |
      v
  generator.py  -->  Comprueba solubilidad (inversiones)
      |
      v
  heuristics.py  -->  Estima distancia al objetivo
      |
      v
  solver.py  -->  A* busca la solucion optima
      |
      v
  Lista de movimientos + estadisticas
```
