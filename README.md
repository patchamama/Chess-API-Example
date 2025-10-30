# Advanced Chess Game - Installation and Usage Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [API Documentation (Swagger UI)](#api-documentation-swagger-ui)
- [How to Use](#how-to-use)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)
- [Additional Documentation](#additional-documentation)

---

## Getting Started

### Prerequisites

Before starting, ensure you have:

- **Python 3.8+** installed
- **Git** installed
- **Stockfish chess engine** ([Download here](https://stockfishchess.org/download/))
- A modern web browser (Chrome, Firefox, Safari, or Edge)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/advanced-chess-game.git
cd advanced-chess-game
```

### 2. Create Python Virtual Environment

Creating a virtual environment isolates your project dependencies from your system Python installation.

#### On Windows:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt, indicating the virtual environment is active.

### 3. Install Dependencies

With your virtual environment activated:

```bash
# Upgrade pip to the latest version
pip install --upgrade pip

# Install all required packages from requirements.txt
pip install -r requirements.txt
```

#### Requirements.txt contents:

```txt
flask==3.0.0
flask-cors==4.0.0
flask-swagger-ui==4.11.1
python-chess==1.10.0
requests==2.31.0
```

If you don't have a `requirements.txt` file, install packages manually:

```bash
pip install flask flask-cors flask-swagger-ui python-chess requests
```

### 4. Install Stockfish

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
2. Extract the executable to a known location
3. Update the path in `chess_server_with_swagger.py`:

```python
STOCKFISH_PATH = "C:\\Path\\To\\stockfish.exe"
```

#### Verify Stockfish Installation:

```bash
# Test Stockfish is accessible
stockfish  # Should open Stockfish UCI interface
# Type 'quit' to exit
```

---

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
// Local development (default)
{"backend_url": "http://127.0.0.1:5000"}

// Alternative local
{"backend_url": "http://localhost:5000"}

// Local network
{"backend_url": "http://192.168.1.100:5000"}

// Production server
{"backend_url": "https://your-domain.com/api"}
```

#### Option 2: No configuration file (Default)

If no `config.json` file is found, the application will automatically use:

```
http://127.0.0.1:5000
```

#### Changing the Backend URL

You can change where the frontend connects to the backend in three ways:

1. **Edit `config.json`** (preferred)
2. **Delete `config.json`** to use the default (127.0.0.1:5000)
3. **Directly edit** the `API_URL` variable in `advanced_chess.html` (not recommended)

### Stockfish Path Configuration

Edit the `STOCKFISH_PATH` variable in `chess_server_with_swagger.py`:

```python
# For Linux/macOS (usually works as-is)
STOCKFISH_PATH = "stockfish"

# For Windows (adjust to your installation path)
STOCKFISH_PATH = "C:\\Program Files\\Stockfish\\stockfish.exe"

# For macOS with Homebrew
STOCKFISH_PATH = "/usr/local/bin/stockfish"
```

---

## Running the Project

### 1. Start the Backend Server

```bash
# Make sure your virtual environment is activated
# You should see (venv) in your prompt

# Navigate to project directory
cd /path/to/advanced-chess-game

# Run the backend server
python chess_server_with_swagger.py
```

You should see:

```
============================================================
ADVANCED CHESS SERVER (WITH SWAGGER UI)
============================================================
API URL: http://localhost:5000
Swagger UI: http://localhost:5000/api/docs
OpenAPI Spec: http://localhost:5000/api/swagger.json

Features:
  - FEN support in all endpoints
  - Automatic position synchronization
  - Multi-engine in make_move (Stockfish, Lichess, Chess.com)
  - Analysis of ALL legal moves
  - Configurable strength level (1-20)
  - Interactive Swagger UI for testing

Endpoints:
  POST /new_game - New game (supports FEN)
  POST /make_move - Move with selected engine
  POST /sync_position - Synchronize position with FEN
  POST /analyze_position - Complete analysis (supports FEN)
  POST /set_engine_strength - Adjust strength (supports FEN)
  GET  /get_capture_moves - Captures only (supports FEN)
  GET  /legal_moves - Legal moves (supports FEN)
  POST /compare_engines - Compare engines (supports FEN)

Quick Start:
  1. Install dependencies: pip install flask-swagger-ui
  2. Visit http://localhost:5000/api/docs to test the API
  3. Try the endpoints directly from the Swagger interface
============================================================
 * Running on http://127.0.0.1:5000
```

### 2. Open the Frontend

#### Option A: Simple Local Server (Recommended)

```bash
# In another terminal, navigate to the project folder
cd /path/to/advanced-chess-game

# Start simple HTTP server
python -m http.server 8080
```

Then open your browser and navigate to:

```
http://localhost:8080/advanced_chess.html
```

#### Option B: Open Directly

```bash
# Simply open the HTML file in your browser
# Note: Some features may not work due to CORS restrictions
```

Double-click on `advanced_chess.html` or open it through your browser's File menu.

---

## API Documentation (Swagger UI)

### New Feature: Interactive API Documentation

The backend now includes **Swagger UI**, providing an interactive interface to test and explore all API endpoints directly from your browser!

#### Accessing Swagger UI

1. **Start the backend server** (if not already running)
2. **Open your browser** and navigate to:
   ```
   http://localhost:5000/api/docs
   ```

#### Features of Swagger UI

- **Interactive Testing**: Try all endpoints directly from the browser
- **Request/Response Examples**: See example data for all endpoints
- **Schema Validation**: Automatic parameter validation
- **Organized Documentation**: Endpoints grouped by category:
  - **Game Management** - Create and manage chess games
  - **Moves** - Make moves and get legal moves
  - **Analysis** - Position analysis and evaluations
  - **Configuration** - Engine settings and strength

#### How to Use Swagger UI

1. **Browse Endpoints**: Click on any endpoint to expand it
2. **Try It Out**: Click the "Try it out" button
3. **Edit Parameters**: Modify the request body or parameters as needed
4. **Execute**: Click "Execute" to send the request
5. **View Response**: See the response data, status code, and headers below

#### Example: Testing a New Game

1. Go to http://localhost:5000/api/docs
2. Find `POST /new_game` under "Game Management"
3. Click "Try it out"
4. Edit the request body:
   ```json
   {
     "game_id": "test_game",
     "color": "white",
     "engine": "stockfish",
     "engine_strength": 15
   }
   ```
5. Click "Execute"
6. View the response with game details

#### OpenAPI Specification

The complete API specification is available at:

```
http://localhost:5000/api/swagger.json
```

This JSON file can be imported into tools like:

- Postman
- Insomnia
- OpenAPI Generator
- Any OpenAPI-compatible tool

---

## How to Use

### Main Options

#### 1. Select Color

- **White**: You play as white (you start)
- **Black**: You play as black (engine starts)

#### 2. Select Engine

- **Stockfish (Backend)**: Stockfish running on Python server

  - Most powerful analysis
  - Complete move evaluation
  - Configurable strength (1-20)
  - Requires active backend server

- **Stockfish.js (Local Browser)**: Stockfish running in your browser

  - Works offline
  - No backend required
  - Privacy-friendly (no data sent)
  - Limited analysis depth

- **Lichess API**: Lichess.org cloud engine

  - Very fast responses
  - Uses opening book database
  - High-quality analysis
  - Requires internet connection
  - Rate-limited

- **Chess.com API**: Chess.com engine
  - Limited public API
  - Currently uses Stockfish as fallback
  - Requires backend server

#### 3. Engine Strength

- **Slider**: Adjust from 1 to 20
- **1-5**: Beginner level (makes mistakes)
- **6-10**: Intermediate level
- **11-15**: Advanced level
- **16-20**: Expert/Master level (very strong)

### Main Functions

#### New Game

Starts a fresh game with your current settings:

- Chosen color
- Selected engine
- Current strength level

#### Analyze Position

Analyzes the current board position and displays:

- **Top 5 best moves** with evaluations
- **Centipawn scores** for each move
- **Mate indicators** if checkmate is possible
- **Piece movements** (from-to squares)

#### Show Captures

Displays only the capture moves available with:

- Move notation (UCI format)
- Evaluation score
- Pieces involved

#### Compare Engines

Compares recommendations from multiple engines:

- **Stockfish** suggestion
- **Lichess** suggestion
- Evaluations from each
- Top 3 moves from each engine

### Automatic Features

#### Auto-Save

- Game automatically saves to `localStorage`
- On page reload, continues from where you left off
- Preserves:
  - Board position
  - Move history
  - Engine settings
  - Player color

#### Evaluation Bar

- Shows current position advantage
- **Green (Positive)**: White has advantage
- **Red (Negative)**: Black has advantage
- **Numbers**: Centipawn evaluation
  - +100 = One pawn advantage for white
  - -100 = One pawn advantage for black
- Updates automatically after each move
- Always shown from white's perspective

#### Live Engine Switching

- Change engines at any time during the game
- Next AI move uses the newly selected engine
- No need to restart the game
- Position is automatically synchronized

#### Move Highlighting

- **Yellow**: Your last move
- **Green**: Legal move destinations
- **Red**: Captures available

---

## Troubleshooting

### Virtual Environment Issues

#### "venv command not found"

**Solution:**

```bash
# Make sure Python is installed
python --version

# Try with python3
python3 -m venv venv

# On Ubuntu/Debian, you might need
sudo apt-get install python3-venv
```

#### "Cannot activate virtual environment"

**Windows:**

```bash
# If you get execution policy error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
venv\Scripts\activate
```

**macOS/Linux:**

```bash
# Make sure the activate script is executable
chmod +x venv/bin/activate
source venv/bin/activate
```

### Backend Issues

#### Error: "Game not found"

**SOLVED** - The refactored backend automatically synchronizes with FEN. This error should no longer occur.

If you still see it:

1. Make sure you're using `chess_server_with_swagger.py`
2. Check that the backend is running
3. Verify the game_id matches between frontend and backend

#### Stockfish Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'stockfish'`

**Solution:**

1. Verify Stockfish is installed:

   ```bash
   which stockfish  # macOS/Linux
   where stockfish  # Windows
   ```

2. Update `STOCKFISH_PATH` in `chess_server_with_swagger.py`:

   ```python
   # Windows
   STOCKFISH_PATH = "C:\\Program Files\\Stockfish\\stockfish.exe"

   # macOS (Homebrew)
   STOCKFISH_PATH = "/usr/local/bin/stockfish"

   # Linux
   STOCKFISH_PATH = "/usr/games/stockfish"
   ```

3. Test Stockfish directly:
   ```bash
   stockfish
   # Should open UCI interface
   # Type 'quit' to exit
   ```

#### Backend Does Not Respond

```bash
# 1. Verify that the backend is running
# You should see this in the terminal:
 * Running on http://127.0.0.1:5000

# 2. Check if another process is using port 5000
```

**On macOS/Linux:**

```bash
lsof -i :5000
```

**On Windows:**

```bash
netstat -ano | findstr :5000
```

**Solution Options:**

**Option 1: Change backend port and update config.json**

```python
# 1. In chess_server_with_swagger.py, change the port:
app.run(debug=True, port=5001)
```

```json
// 2. Update your config.json:
{
  "backend_url": "http://127.0.0.1:5001"
}
```

**Option 2: Free up port 5000**

```bash
# macOS/Linux: Find and kill the process
lsof -i :5000
kill -9 [PID]

# Windows: Find and kill the process
netstat -ano | findstr :5000
taskkill /PID [PID] /F
```

### Frontend Issues

#### Stockfish.js Does Not Load

**Symptoms:**

- Browser-based Stockfish doesn't work
- Console shows loading errors

**Solutions:**

1. **Check browser console** (F12 -> Console tab)
2. **Verify internet connection** (Stockfish.js needs to download)
3. **Try another browser** (Chrome/Firefox recommended)
4. **Clear browser cache** and reload
5. **Use Stockfish (Backend)** as alternative

#### CORS Errors

If you see CORS errors in the browser console:

```
Access to fetch at 'http://localhost:5000/...' has been blocked by CORS policy
```

**Solutions:**

1. **Make sure the backend is running** with flask-cors installed
2. **Use a local HTTP server** (don't open HTML file directly):
   ```bash
   python -m http.server 8080
   ```
3. **Verify flask-cors is installed**:
   ```bash
   pip install flask-cors
   ```
4. **Check CORS configuration** in `chess_server_with_swagger.py`:
   ```python
   from flask_cors import CORS
   CORS(app)  # Should be present
   ```

#### Evaluation Bar Jumps

**SOLVED** - The evaluation bar now consistently shows from white's perspective.

If it still seems incorrect:

1. Refresh the page
2. Start a new game
3. Check browser console for errors

#### Page Does Not Load Properly

**Solutions:**

1. **Clear browser cache**:

   - Chrome: Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)
   - Select "Cached images and files"
   - Click "Clear data"

2. **Check JavaScript errors**:

   - Open browser console (F12)
   - Look for red error messages
   - Report any errors found

3. **Verify all files are present**:
   ```bash
   ls -la
   # Should see:
   # - advanced_chess.html
   # - chess_server_with_swagger.py
   # - config.json (optional)
   ```

### API Testing Issues

#### Swagger UI Not Accessible

**Error:** Cannot access http://localhost:5000/api/docs

**Solutions:**

1. **Verify backend is running**:

   ```bash
   # Should see the startup message
   # Including: "Swagger UI: http://localhost:5000/api/docs"
   ```

2. **Check flask-swagger-ui is installed**:

   ```bash
   pip install flask-swagger-ui
   ```

3. **Try accessing the base URL**:

   ```
   http://localhost:5000/
   # Should return JSON with API information
   ```

4. **Check for port conflicts** (see Backend Does Not Respond section)

---

## Advanced Features

### Backend API Direct Usage

You can interact with the backend API directly using tools like cURL, Postman, or programming languages.

#### Using cURL

**Create new game:**

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

**Make a move:**

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

**Analyze position:**

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

**Compare engines:**

```bash
curl -X POST http://localhost:5000/compare_engines \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "test123"
  }'
```

**Set engine strength:**

```bash
curl -X POST http://localhost:5000/set_engine_strength \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "test123",
    "strength": 10
  }'
```

**Get capture moves:**

```bash
curl -X GET "http://localhost:5000/get_capture_moves?game_id=test123&engine=stockfish"
```

**Get legal moves:**

```bash
curl -X GET "http://localhost:5000/legal_moves?game_id=test123&square=e2"
```

#### Using Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Create a new game
response = requests.post(f"{BASE_URL}/new_game", json={
    "game_id": "python_game",
    "color": "white",
    "engine": "stockfish",
    "engine_strength": 18
})
game_data = response.json()
print(f"Game created: {game_data['game_id']}")
print(f"Starting FEN: {game_data['fen']}")

# Make a move
response = requests.post(f"{BASE_URL}/make_move", json={
    "game_id": "python_game",
    "move": "e2e4",
    "engine": "stockfish"
})
move_data = response.json()
print(f"\nYour move: {move_data['player_move']}")
print(f"AI response: {move_data['ai_move']}")
print(f"New position: {move_data['fen']}")

# Analyze the position
response = requests.post(f"{BASE_URL}/analyze_position", json={
    "game_id": "python_game",
    "engine": "stockfish",
    "top_moves": 5
})
analysis = response.json()
print(f"\nBest move: {analysis['best_move']}")
print(f"Position evaluation: {analysis['position_evaluation']} centipawns")

# Compare engines
response = requests.post(f"{BASE_URL}/compare_engines", json={
    "game_id": "python_game"
})
comparison = response.json()
print("\nEngine comparison:")
print(f"Stockfish suggests: {comparison['stockfish']['best_move']}")
print(f"Lichess suggests: {comparison['lichess']['best_move']}")
```

#### Using JavaScript (Frontend)

```javascript
const BASE_URL = 'http://localhost:5000'

// Create a new game
async function createGame() {
  const response = await fetch(`${BASE_URL}/new_game`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      game_id: 'js_game',
      color: 'white',
      engine: 'lichess',
      engine_strength: 15,
    }),
  })
  const data = await response.json()
  console.log('Game created:', data)
  return data
}

// Make a move
async function makeMove(gameId, move) {
  const response = await fetch(`${BASE_URL}/make_move`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      game_id: gameId,
      move: move,
      engine: 'stockfish',
    }),
  })
  const data = await response.json()
  console.log('Move made:', data)
  return data
}

// Usage
createGame()
  .then((gameData) => {
    return makeMove(gameData.game_id, 'e2e4')
  })
  .then((moveData) => {
    console.log('Player move:', moveData.player_move)
    console.log('AI move:', moveData.ai_move)
  })
```

### Custom Position (FEN)

Start a game from any position using FEN notation:

```bash
curl -X POST http://localhost:5000/new_game \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "custom_position",
    "color": "white",
    "engine": "stockfish",
    "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
  }'
```

This is useful for:

- Practicing specific positions
- Analyzing famous games
- Testing tactical puzzles
- Training endgames

### All Available Endpoints

| Method | Endpoint               | Description                    |
| ------ | ---------------------- | ------------------------------ |
| POST   | `/new_game`            | Create a new game              |
| POST   | `/make_move`           | Make a player move             |
| POST   | `/sync_position`       | Synchronize board position     |
| POST   | `/analyze_position`    | Get complete position analysis |
| POST   | `/set_engine_strength` | Change engine difficulty       |
| GET    | `/get_capture_moves`   | Get only capture moves         |
| GET    | `/legal_moves`         | Get legal moves for a square   |
| POST   | `/compare_engines`     | Compare different engines      |
| GET    | `/`                    | API information                |
| GET    | `/api/docs`            | Swagger UI documentation       |
| GET    | `/api/swagger.json`    | OpenAPI specification          |

---

## Additional Documentation

- **REFACTORING_DOCUMENTATION.md**: Technical details of the backend refactoring
- **CHANGES.md**: Evaluation bar fixes and improvements
- **Inline comments**: Both HTML and Python files are thoroughly commented

---

## Report Issues

If you encounter any problems:

1. **Check the browser console** (F12 -> Console tab)
2. **Check the backend logs** (terminal where Python is running)
3. **Verify all dependencies are installed**:
   ```bash
   pip list | grep -E "flask|chess|requests"
   ```
4. **Read the troubleshooting section** above
5. **Test with Swagger UI** (http://localhost:5000/api/docs)
6. **Create a GitHub issue** with:
   - Error messages
   - Steps to reproduce
   - Browser/OS information
   - Backend logs

---

## Features Summary

The game is fully functional with:

- **4 different chess engines**

  - Stockfish (backend)
  - Stockfish.js (browser)
  - Lichess API
  - Chess.com fallback

- **Complete position analysis**

  - Top moves evaluation
  - Capture moves filtering
  - Multi-engine comparison

- **Corrected evaluation bar**

  - Always from white's perspective
  - Accurate centipawn display

- **Auto-save and auto-restore**

  - Survives page reloads
  - localStorage persistence

- **Live engine switching**

  - Change engines mid-game
  - No restart required

- **Responsive design**

  - Works on mobile and desktop
  - Touch-friendly interface

- **Automatic synchronization**

  - FEN-based position sync
  - No "game not found" errors

- **Interactive API documentation**

  - Swagger UI interface
  - Test endpoints in browser
  - Complete API examples

- **Configurable engine strength**
  - 20 difficulty levels
  - From beginner to master

---

## Learning Resources

### Understanding Chess Notation

- **UCI Format**: e2e4 (from square to square)
- **SAN Format**: e4 (standard algebraic notation)
- **FEN**: Complete board position in text format

### Understanding Evaluations

- **Centipawns**: 100 centipawns = 1 pawn advantage
- **Positive**: White is better
- **Negative**: Black is better
- **Mate in N**: Forced checkmate in N moves

### Chess Engine Information

- **Stockfish**: Open-source, strongest chess engine
- **Lichess**: Cloud-based, uses Stockfish with opening books
- **Engine Strength**: Lower values make human-like mistakes

---

## Next Steps

Now that you have everything set up:

1. **Start the backend server**
2. **Open the frontend** in your browser
3. **Explore Swagger UI** at http://localhost:5000/api/docs
4. **Play your first game**
5. **Try different engines** and strength levels
6. **Analyze positions** to improve your chess
7. **Experiment with the API** using cURL or code

---

## Enjoy Playing!

Good luck with your games and happy coding!

If you enjoy this project, consider:

- Starring the repository on GitHub
- Reporting bugs you find
- Suggesting new features
- Contributing improvements

---

**Made with care for chess enthusiasts**
