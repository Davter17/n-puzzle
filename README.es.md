# N-Puzzle Web

Una implementación web del clásico juego N-Puzzle (puzzle deslizante) con un resolvedor de IA que demuestra varios algoritmos de búsqueda y heurísticas.

## Características

- **Tablero Interactivo**: Juega el N-Puzzle directamente en tu navegador
- **Múltiples Tamaños**: Soporte para tableros 3x3, 4x4, 5x5 y 6x6
- **Resolvedor IA**: Resolución automática del puzzle usando algoritmo A*
- **Múltiples Heurísticas**:
  - **Distancia Manhattan**: Suma de distancias horizontales y verticales
  - **Piezas Fuera de Lugar**: Conteo de piezas no en su posición objetivo
  - **Conflicto Lineal**: Distancia Manhattan más penalización por piezas que deben cruzarse
- **Velocidad Personalizable**: Ajusta la velocidad de animación de rápido a lento
- **Precisión vs Velocidad**: Controla el equilibrio entre optimalidad y tiempo de resolución
- **Subida de Imágenes**: Usa imágenes personalizadas para las piezas del puzzle
- **Historial de Movimientos**: Visualización de todos los movimientos en la solución
- **Controles en Tiempo Real**: Cancela la resolución en cualquier momento, ajusta la velocidad durante la animación

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Configuración

1. Clona el repositorio:
```bash
git clone https://github.com/Davter17/n-puzzle.git N-Puzzle
cd N-Puzzle
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv venv
```

3. Activa el entorno virtual:
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución de la Aplicación

Inicia el servidor de desarrollo Flask:
```bash
python app.py
```

Abre tu navegador y navega a:
```
http://localhost:5000
```

## Cómo Usar

### Jugando el Puzzle
- **Haz clic** en las piezas adyacentes al espacio vacío para deslizarlas
- **Usa las teclas de dirección** para mover piezas (Arriba/Abajo/Izquierda/Derecha)
- **Intercambia piezas** haciendo clic en dos piezas no adyacentes (primer clic selecciona, segundo clic intercambia)

### Resolviendo el Puzzle
1. **Selecciona el tamaño del tablero** (3x3, 4x4, 5x5 o 6x6)
2. **Elige una heurística** (Manhattan, Fuera de Lugar o Lineal)
3. **Ajusta el slider Precisión vs Velocidad**:
   - Izquierda (Precisión): Encuentra solución óptima pero más lento
   - Derecha (Velocidad): Más rápido pero puede no encontrar solución óptima
4. **Haz clic en "Randomizer"** para generar un puzzle aleatorio
5. **Haz clic en "Resolve"** para iniciar el resolvedor IA
6. **Haz clic en "Cancel"** para detener el resolvedor en cualquier momento

### Imágenes Personalizadas
- Haz clic en "Load image" para subir tu propia imagen
- Recorta la imagen a un cuadrado
- La imagen se dividirá en piezas del puzzle

## Detalles Técnicos

### Algoritmos
- **Búsqueda A***: Algoritmo principal usando f(n) = g(n) + w * h(n)
  - g(n): Costo desde el inicio al nodo actual
  - h(n): Estimación heurística al objetivo
  - w: Peso (ajustado por el slider Precisión vs Velocidad)
- **Greedy Best-First**: Usado en configuraciones extremas de velocidad
  - f(n) = h(n) solamente

### Heurísticas
- **Distancia Manhattan**: h(n) = suma de |x1-x2| + |y1-y2| para todas las piezas
- **Piezas Fuera de Lugar**: h(n) = conteo de piezas no en posición objetivo
- **Conflicto Lineal**: h(n) = Manhattan + 2 * (número de conflictos)
  - Agrega penalización cuando dos piezas están en la misma fila/columna pero en orden incorrecto

### Rendimiento
- 3x3: Resolución instantánea (solución óptima garantizada)
- 4x4: Resolución rápida (hasta 5M nodos explorados)
- 5x5: Resolución moderada (hasta 2M nodos explorados)
- 6x6: Desafiante (hasta 2M nodos explorados, puede agotar tiempo después de 30s)

## Estructura del Proyecto

```
N-Puzzle-web/
├── app.py              # Servidor de aplicación Flask
├── engine/             # Motor de resolución del puzzle
│   ├── board.py       # Representación del tablero
│   ├── solver.py      # Algoritmo de búsqueda A*
│   ├── heuristics.py  # Funciones heurísticas
│   └── generator.py   # Generación del puzzle
├── static/            # Archivos estáticos
│   ├── css/
│   │   └── style.css  # Estilos de la aplicación
│   ├── js/
│   │   └── app.js     # Lógica del frontend
│   └── img/           # Imágenes predeterminadas
├── templates/         # Plantillas HTML
│   └── index.html     # Página principal
├── requirements.txt   # Dependencias de Python
└── .gitignore        # Reglas de git ignore
```

## Dependencias

- **Flask**: Framework web
- Todas las dependencias están listadas en `requirements.txt`

## Compatibilidad con Navegadores

- Chrome/Edge (recomendado)
- Firefox
- Safari

## Licencia

Este proyecto fue creado con fines educativos.

## Créditos

Creado como parte del proyecto N-Puzzle del currículo de 42.
