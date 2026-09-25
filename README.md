# N-Puzzle Web

A web-based implementation of the classic N-Puzzle (sliding puzzle) game with an AI solver that demonstrates various search algorithms and heuristics.

## Features

- **Interactive Puzzle Board**: Play the N-Puzzle directly in your browser
- **Multiple Board Sizes**: Support for 3x3, 4x4, 5x5, and 6x6 grids
- **AI Solver**: Automatic puzzle solving using A* search algorithm
- **Multiple Heuristics**:
  - **Manhattan Distance**: Sum of horizontal and vertical distances
  - **Misplaced Tiles**: Count of tiles not in their goal position
  - **Linear Conflict**: Manhattan distance plus penalty for tiles that must pass each other
- **Customizable Speed**: Adjust animation speed from fast to slow
- **Precision vs Speed**: Control the trade-off between optimality and solving time
- **Image Upload**: Use custom images for the puzzle tiles
- **Move History**: Visual display of all moves in the solution
- **Real-time Controls**: Cancel solving at any time, adjust speed during animation

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd N-Puzzle-web
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

## How to Use

### Playing the Puzzle
- **Click** on tiles adjacent to the empty space to slide them
- **Use arrow keys** to move tiles (Up/Down/Left/Right)
- **Swap tiles** by clicking two non-adjacent tiles (first click selects, second click swaps)

### Solving the Puzzle
1. **Select board size** (3x3, 4x4, 5x5, or 6x6)
2. **Choose a heuristic** (Manhattan, Misplaced, or Linear)
3. **Adjust Precision vs Speed** slider:
   - Left (Precision): Finds optimal solution but slower
   - Right (Speed): Faster but may not find optimal solution
4. **Click "Randomizer"** to generate a random puzzle
5. **Click "Resolve"** to start the AI solver
6. **Click "Cancel"** to stop the solver at any time

### Custom Images
- Click "Load image" to upload your own image
- Crop the image to a square
- The image will be split into puzzle tiles

## Technical Details

### Algorithms
- **A* Search**: Primary algorithm using f(n) = g(n) + w * h(n)
  - g(n): Cost from start to current node
  - h(n): Heuristic estimate to goal
  - w: Weight (adjusted by Precision vs Speed slider)
- **Greedy Best-First**: Used at extreme speed settings
  - f(n) = h(n) only

### Heuristics
- **Manhattan Distance**: h(n) = sum of |x1-x2| + |y1-y2| for all tiles
- **Misplaced Tiles**: h(n) = count of tiles not in goal position
- **Linear Conflict**: h(n) = Manhattan + 2 * (number of conflicts)
  - Adds penalty when two tiles are in the same row/column but in wrong order

### Performance
- 3x3: Instant solving (optimal solution guaranteed)
- 4x4: Fast solving (up to 5M nodes explored)
- 5x5: Moderate solving (up to 2M nodes explored)
- 6x6: Challenging (up to 2M nodes explored, may timeout after 30s)

## Project Structure

```
N-Puzzle-web/
├── app.py              # Flask application server
├── engine/             # Puzzle solving engine
│   ├── board.py       # Board representation
│   ├── solver.py      # A* search algorithm
│   ├── heuristics.py  # Heuristic functions
│   └── generator.py   # Puzzle generation
├── static/            # Static files
│   ├── css/
│   │   └── style.css  # Application styles
│   ├── js/
│   │   └── app.js     # Frontend logic
│   └── img/           # Default images
├── templates/         # HTML templates
│   └── index.html     # Main page
├── requirements.txt   # Python dependencies
└── .gitignore        # Git ignore rules
```

## Dependencies

- **Flask**: Web framework
- All dependencies are listed in `requirements.txt`

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari

## License

This project is created for educational purposes.

## Credits

Created as part of the 42 curriculum N-Puzzle project.
