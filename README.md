# Chess API Backend

This is a Flask-based API for playing chess against a computer opponent (Stockfish), analyzing chess positions, and getting move recommendations. It also provides integration with Lichess and Chess.com APIs for analysis.

## Installation

To use this API, you'll need to have python3 3 and Stockfish installed on your system.

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/patchamama/Chess-API-Example.git
    cd Chess-API-Example
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

    _(On Windows, use `venv\Scripts\activate`)_

3.  **Install the dependencies:**

    ```bash
    pip3 install -r requirements.txt
    ```

4.  **Install Stockfish:**
    Make sure you have the Stockfish engine installed and accessible in your system's PATH. You can download it from the [official Stockfish website](https://stockfishchess.org/download/).

## How to Run

Once the installation is complete, you can run the Flask server:

```bash
python3 chess-api-backend.py
```

The server will start on `http://127.0.0.1:5000`.

## Endpoints

Here are the available endpoints:

### 1. New Game

- **Method:** `POST`
- **Endpoint:** `/new_game`
- **Description:** Starts a new chess game.
- **Payload (JSON):**
  - `game_id` (string, optional): A unique ID for the game. Defaults to 'default'.
  - `color` (string, optional): The player's color ('white' or 'black'). Defaults to 'white'.
  - `engine_strength` (integer, optional): The engine's strength (1-20). Defaults to 20.
- **Curl Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{
      "game_id": "my_new_game",
      "color": "white",
      "engine_strength": 15
  }' http://127.0.0.1:5000/new_game
  ```

### 2. Make a Move

- **Method:** `POST`
- **Endpoint:** `/make_move`
- **Description:** Makes a move in the specified game.
- **Payload (JSON):**
  - `game_id` (string, optional): The ID of the game. Defaults to 'default'.
  - `move` (string): The move in UCI format (e.g., 'e2e4').
- **Curl Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{
      "game_id": "my_new_game",
      "move": "e2e4"
  }' http://127.0.0.1:5000/make_move
  ```

### 3. Analyze Position

- **Method:** `POST`
- **Endpoint:** `/analyze_position`
- **Description:** Analyzes the current position of a game.
- **Payload (JSON):**
  - `game_id` (string, optional): The ID of the game. Defaults to 'default'.
  - `engine` (string, optional): The engine to use for analysis ('stockfish', 'lichess', 'chesscom'). Defaults to 'stockfish'.
  - `top_moves` (integer, optional): The number of top moves to return. Defaults to 5.
  - `depth` (integer, optional): The search depth for Stockfish. Defaults to 5.
- **Curl Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{
      "game_id": "my_new_game",
      "engine": "stockfish",
      "top_moves": 3,
      "depth": 15
  }' http://127.0.0.1:5000/analyze_position
  ```

### 4. Set Engine Strength

- **Method:** `POST`
- **Endpoint:** `/set_engine_strength`
- **Description:** Sets the engine's strength for a game.
- **Payload (JSON):**
  - `game_id` (string, optional): The ID of the game. Defaults to 'default'.
  - `strength` (integer): The engine's strength (1-20).
- **Curl Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{
      "game_id": "my_new_game",
      "strength": 10
  }' http://127.0.0.1:5000/set_engine_strength
  ```

### 5. Get Capture Moves

- **Method:** `GET`
- **Endpoint:** `/get_capture_moves`
- **Description:** Returns all capture moves in the current position.
- **Query Parameters:**
  - `game_id` (string, optional): The ID of the game. Defaults to 'default'.
  - `engine` (string, optional): The engine to use for analysis. Defaults to 'stockfish'.
- **Curl Example:**
  ```bash
  curl "http://127.0.0.1:5000/get_capture_moves?game_id=my_new_game&engine=stockfish"
  ```

### 6. Legal Moves

- **Method:** `GET`
- **Endpoint:** `/legal_moves`
- **Description:** Returns all legal moves for a specific square.
- **Query Parameters:**
  - `game_id` (string, optional): The ID of the game. Defaults to 'default'.
  - `square` (string): The square to get legal moves for (e.g., 'e2').
- **Curl Example:**
  ```bash
  curl "http://127.0.0.1:5000/legal_moves?game_id=my_new_game&square=e2"
  ```

### 7. Compare Engines

- **Method:** `POST`
- **Endpoint:** `/compare_engines`
- **Description:** Compares the analysis of Stockfish and Lichess for the current position.
- **Payload (JSON):**
  - `game_id` (string, optional): The ID of the game. Defaults to 'default'.
- **Curl Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{
      "game_id": "my_new_game"
  }' http://127.0.0.1:5000/compare_engines
  ```
