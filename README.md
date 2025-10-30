# Advanced Chess Game - Installation and Usage Guide

## Configuration

### Backend URL Configuration

The frontend can be configured to connect to different backend servers using a `config.json` file.

#### Option 1: Using config.json (Recommended)

1. Copy the example configuration:

```bash
cp config.json.example config.json
```

2. Edit `config.json` to set your backend URL:

```json
{
  "backend_url": "http://127.0.0.1:5000"
}
```

3. Examples of different configurations:

```json
# Local development (default)
{"backend_url": "http://127.0.0.1:5000"}

# Alternative local
{"backend_url": "http://localhost:5000"}

# Local network
{"backend_url": "http://192.168.1.100:5000"}

# Production server
{"backend_url": "https://your-domain.com/api"}
```

#### Option 2: No configuration file (Default)

If no `config.json` file is found, the application will automatically use:

```
http://127.0.0.1:5000
```

#### Changing the Backend URL

You can change where the frontend connects to the backend in three ways:

1. Edit `config.json` (preferred)
2. Delete `config.json` to use the default (127.0.0.1:5000)
3. Directly edit the `API_URL` variable in `advanced_chess.html` (not recommended)

## Installation

### 1. Prerequisites

```bash
# Python 3.8+
python --version

# Pip
pip --version
```

### 2. Install Dependencies

```bash
pip install flask flask-cors python-chess requests
```

### 3. Install Stockfish

#### Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install stockfish
```

#### macOS (with Homebrew):

```bash
brew install stockfish
```

#### Windows:

1. Download from: https://stockfishchess.org/download/
2. Extract the executable
3. Update the path in `chess_backend_refactored.py`:

```python
STOCKFISH_PATH = "C:\\Path\\To\\stockfish.exe"
```

## Running the Project

### 1. Start the Backend

```bash
cd /path/to/your/project
python chess_backend_refactored.py
```

You should see:

```
============================================================
ADVANCED CHESS SERVER (REFACTORED)
============================================================
URL: http://localhost:5000

Features:
  - FEN support in all endpoints
  - Automatic position synchronization
  - Multi-engine in make_move (Stockfish, Lichess, Chess.com)
  - Analysis of ALL legal moves
  - Configurable strength level (1-20)
...
 * Running on http://127.0.0.1:5000
```

### 2. Open the Frontend

#### Option A: Simple Local Server

```bash
# In another terminal, navigate to the project folder
cd /path/to/your/project

# Start simple HTTP server
python -m http.server 8080
```

Then open: http://localhost:8080/advanced_chess.html

#### Option B: Open Directly

```bash
# Simply open the HTML file in your browser
# (Some features may not work due to CORS restrictions)
```

## How to Use

### Main Options

#### 1. Select Color

- White: You play as white (you start)
- Black: You play as black (engine starts)

#### 2. Select Engine

- **Stockfish (Backend)**: Stockfish running on Python server

  - More powerful
  - Complete analysis
  - Requires active backend

- **Stockfish.js (Local Browser)**: Stockfish running in your browser

  - Works offline
  - No backend required
  - Limited analysis

- **Lichess API**: Lichess.org engine

  - Very fast
  - Opening database
  - Requires internet

- **Chess.com API**: Chess.com engine (fallback to Stockfish)
  - Limited API, uses Stockfish as fallback

#### 3. Engine Strength

- Slide from 1 to 20
- 1 = Absolute beginner
- 20 = Grandmaster

### Main Functions

#### New Game

Starts a new game with current settings

#### Analyze Position

Analyzes current position and shows:

- Top 5 best moves
- Evaluation of each move
- Mate indicators

#### Show Captures

Shows only capture moves with their evaluation

#### Compare Engines

Compares what different engines suggest for the current position

### Automatic Features

#### Auto-Save

- Game automatically saves to localStorage
- When you reload the page, it continues where you left off

#### Evaluation Bar

- Shows current advantage
- Positive (+): White advantage
- Negative (-): Black advantage
- Updates automatically after each move

#### Live Engine Switching

- You can change engines during the game
- Next move will use the selected engine

## Troubleshooting

### Error: "Game not found"

SOLVED - The refactored backend automatically synchronizes with FEN

### Stockfish.js does not load

1. Check browser console (F12)
2. Verify your internet connection (needs to download the engine)
3. Try another browser (Chrome/Firefox recommended)
4. Alternatively, use Stockfish (Backend)

### Backend does not respond

```bash
# Verify that the backend is running
# You should see this in the terminal:
 * Running on http://127.0.0.1:5000

# Verify that port 5000 is free
netstat -an | grep 5000

# If port 5000 is occupied, you can change it:
```

**Option 1: Change backend port and update config.json**

```bash
# 1. In chess_backend_refactored.py, change the port:
app.run(debug=True, port=5001)

# 2. Update your config.json:
{
  "backend_url": "http://127.0.0.1:5001"
}
```

**Option 2: Free up port 5000**

```bash
# Find what's using port 5000
lsof -i :5000

# Stop the process
kill -9 [PID]
```

### CORS Errors

If you see CORS errors in the console:

1. Make sure the backend is running
2. Use a local HTTP server (don't open the HTML directly)
3. Verify that flask-cors is installed: `pip install flask-cors`

### Evaluation bar jumps too much

SOLVED - Now always shows from white's perspective

## Advanced Features

### Backend API

You can use the backend directly with tools like curl or Postman:

#### Create new game:

```bash
curl -X POST http://localhost:5000/new_game \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "test123",
    "color": "white",
    "engine": "stockfish",
    "engine_strength": 15
  }'
```

#### Make a move:

```bash
curl -X POST http://localhost:5000/make_move \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "test123",
    "move": "e2e4",
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "engine": "lichess"
  }'
```

#### Analyze position:

```bash
curl -X POST http://localhost:5000/analyze_position \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "test123",
    "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    "engine": "stockfish",
    "top_moves": 5,
    "depth": 20
  }'
```

## Additional Documentation

- **REFACTORING_DOCUMENTATION.md**: Technical details of the refactoring
- **CHANGES.md**: Evaluation bar fixes
- Commented code in both files (HTML and Python)

## Report Issues

If you find any problems:

1. Check the browser console (F12 -> Console)
2. Check the backend logs (terminal where Python runs)
3. Verify that all dependencies are installed
4. Read the troubleshooting documentation above

## Enjoy Playing

The game is fully functional with:

- 4 different engines
- Complete analysis
- Corrected evaluation bar
- Auto-save and auto-restore
- Live engine switching
- Responsive design (mobile and desktop)
- Automatic synchronization with backend

Good luck with your games!
