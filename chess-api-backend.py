from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import chess
import chess.engine
import requests
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json

app = Flask(__name__)
CORS(app)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Advanced Chess API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Stockfish configuration
STOCKFISH_PATH = "stockfish"  # Adjust according to operating system
# STOCKFISH_PATH = "C:\\Path\\To\\stockfish.exe"  # Windows

# Game storage
games = {}

@dataclass
class MoveEvaluation:
    move: str
    evaluation: float  # In centipawns or mate
    is_mate: bool
    mate_in: Optional[int]
    is_capture: bool
    piece: str
    from_square: str
    to_square: str

@dataclass
class EngineAnalysis:
    best_move: str
    top_moves: List[MoveEvaluation]
    all_legal_moves: List[MoveEvaluation]
    capture_moves: List[MoveEvaluation]
    position_evaluation: float
    fen: str

def get_or_create_game(game_id: str, fen: Optional[str] = None, 
                       player_color: str = 'white', 
                       engine_strength: int = 20) -> Dict:
    """Gets an existing game or creates a new one from a FEN"""
    if game_id not in games:
        board = chess.Board() if not fen else chess.Board(fen)
        games[game_id] = {
            'board': board,
            'player_color': player_color,
            'moves': [],
            'engine_strength': engine_strength,
            'current_engine': 'stockfish'  # Default engine
        }
        print(f"📝 New game created: {game_id} (FEN: {board.fen()[:50]}...)")
    elif fen:
        # If FEN is provided, update the position
        games[game_id]['board'] = chess.Board(fen)
        print(f"🔄 Game {game_id} updated with new FEN")
    
    return games[game_id]

@app.route('/api/swagger.json')
def swagger_spec():
    """Returns the Swagger/OpenAPI specification"""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Advanced Chess API",
            "description": "Multi-engine chess API with Stockfish, Lichess, and Chess.com support. Features FEN synchronization, position analysis, and configurable engine strength.",
            "version": "1.0.0",
            "contact": {
                "name": "Chess API Support"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Local development server"
            }
        ],
        "tags": [
            {
                "name": "Game Management",
                "description": "Endpoints for creating and managing chess games"
            },
            {
                "name": "Moves",
                "description": "Endpoints for making and analyzing moves"
            },
            {
                "name": "Analysis",
                "description": "Position analysis and evaluation endpoints"
            },
            {
                "name": "Configuration",
                "description": "Engine configuration endpoints"
            }
        ],
        "paths": {
            "/new_game": {
                "post": {
                    "tags": ["Game Management"],
                    "summary": "Start a new chess game",
                    "description": "Creates a new game with optional FEN position, player color, and engine settings",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "game_id": {
                                            "type": "string",
                                            "default": "default",
                                            "description": "Unique identifier for the game"
                                        },
                                        "color": {
                                            "type": "string",
                                            "enum": ["white", "black"],
                                            "default": "white",
                                            "description": "Player's color"
                                        },
                                        "engine_strength": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 20,
                                            "default": 20,
                                            "description": "Engine strength level (1=weakest, 20=strongest)"
                                        },
                                        "engine": {
                                            "type": "string",
                                            "enum": ["stockfish", "lichess", "chesscom"],
                                            "default": "stockfish",
                                            "description": "Chess engine to use"
                                        },
                                        "fen": {
                                            "type": "string",
                                            "description": "Optional FEN string for custom starting position"
                                        }
                                    }
                                },
                                "examples": {
                                    "default_game": {
                                        "summary": "Default new game",
                                        "value": {
                                            "game_id": "game1",
                                            "color": "white",
                                            "engine_strength": 20,
                                            "engine": "stockfish"
                                        }
                                    },
                                    "custom_position": {
                                        "summary": "Game from FEN",
                                        "value": {
                                            "game_id": "custom1",
                                            "color": "white",
                                            "engine": "lichess",
                                            "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Game created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "game_id": {"type": "string"},
                                            "fen": {"type": "string"},
                                            "player_color": {"type": "string"},
                                            "engine_strength": {"type": "integer"},
                                            "engine": {"type": "string"},
                                            "ai_move": {"type": "string"},
                                            "analysis": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/make_move": {
                "post": {
                    "tags": ["Moves"],
                    "summary": "Make a player move",
                    "description": "Processes the player's move and returns the engine's response",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["move"],
                                    "properties": {
                                        "game_id": {
                                            "type": "string",
                                            "default": "default"
                                        },
                                        "move": {
                                            "type": "string",
                                            "description": "Move in UCI format (e.g., 'e2e4')"
                                        },
                                        "fen": {
                                            "type": "string",
                                            "description": "Optional FEN for position sync"
                                        },
                                        "engine": {
                                            "type": "string",
                                            "enum": ["stockfish", "lichess", "chesscom"],
                                            "default": "stockfish"
                                        },
                                        "engine_strength": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 20,
                                            "default": 20
                                        }
                                    }
                                },
                                "examples": {
                                    "simple_move": {
                                        "summary": "Simple move",
                                        "value": {
                                            "game_id": "game1",
                                            "move": "e2e4",
                                            "engine": "stockfish"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Move processed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "player_move": {"type": "string"},
                                            "ai_move": {"type": "string"},
                                            "fen": {"type": "string"},
                                            "game_over": {"type": "boolean"},
                                            "moves_history": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            },
                                            "analysis": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Illegal move or error"
                        }
                    }
                }
            },
            "/sync_position": {
                "post": {
                    "tags": ["Game Management"],
                    "summary": "Synchronize board position",
                    "description": "Synchronizes the board position with the backend using FEN",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["fen"],
                                    "properties": {
                                        "game_id": {
                                            "type": "string",
                                            "default": "default"
                                        },
                                        "fen": {
                                            "type": "string",
                                            "description": "FEN string of current position"
                                        },
                                        "player_color": {
                                            "type": "string",
                                            "enum": ["white", "black"],
                                            "default": "white"
                                        },
                                        "engine_strength": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 20,
                                            "default": 20
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Position synchronized"
                        },
                        "400": {
                            "description": "FEN required"
                        }
                    }
                }
            },
            "/analyze_position": {
                "post": {
                    "tags": ["Analysis"],
                    "summary": "Analyze current position",
                    "description": "Analyzes the current position with the chosen engine",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "game_id": {
                                            "type": "string",
                                            "default": "default"
                                        },
                                        "engine": {
                                            "type": "string",
                                            "enum": ["stockfish", "lichess", "chesscom"],
                                            "default": "stockfish"
                                        },
                                        "top_moves": {
                                            "type": "integer",
                                            "default": 5,
                                            "description": "Number of top moves to return"
                                        },
                                        "depth": {
                                            "type": "integer",
                                            "default": 20,
                                            "description": "Search depth for Stockfish"
                                        },
                                        "fen": {
                                            "type": "string",
                                            "description": "Optional FEN for position sync"
                                        }
                                    }
                                },
                                "examples": {
                                    "stockfish_analysis": {
                                        "summary": "Stockfish deep analysis",
                                        "value": {
                                            "game_id": "game1",
                                            "engine": "stockfish",
                                            "top_moves": 5,
                                            "depth": 20
                                        }
                                    },
                                    "lichess_analysis": {
                                        "summary": "Lichess cloud analysis",
                                        "value": {
                                            "game_id": "game1",
                                            "engine": "lichess",
                                            "top_moves": 3
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Analysis completed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "best_move": {"type": "string"},
                                            "top_moves": {"type": "array"},
                                            "all_legal_moves": {"type": "array"},
                                            "capture_moves": {"type": "array"},
                                            "position_evaluation": {"type": "number"},
                                            "fen": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Game not found"
                        },
                        "500": {
                            "description": "Analysis error"
                        }
                    }
                }
            },
            "/set_engine_strength": {
                "post": {
                    "tags": ["Configuration"],
                    "summary": "Set engine strength",
                    "description": "Changes the engine strength level (1-20)",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["strength"],
                                    "properties": {
                                        "game_id": {
                                            "type": "string",
                                            "default": "default"
                                        },
                                        "strength": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 20,
                                            "description": "Engine strength (1=weakest, 20=strongest)"
                                        },
                                        "fen": {
                                            "type": "string",
                                            "description": "Optional FEN for position sync"
                                        }
                                    }
                                },
                                "examples": {
                                    "beginner": {
                                        "summary": "Beginner level",
                                        "value": {
                                            "game_id": "game1",
                                            "strength": 5
                                        }
                                    },
                                    "expert": {
                                        "summary": "Expert level",
                                        "value": {
                                            "game_id": "game1",
                                            "strength": 20
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Strength updated"
                        },
                        "400": {
                            "description": "Invalid strength value"
                        },
                        "404": {
                            "description": "Game not found"
                        }
                    }
                }
            },
            "/get_capture_moves": {
                "get": {
                    "tags": ["Analysis"],
                    "summary": "Get capture moves",
                    "description": "Returns only capture moves with evaluation",
                    "parameters": [
                        {
                            "name": "game_id",
                            "in": "query",
                            "schema": {
                                "type": "string",
                                "default": "default"
                            }
                        },
                        {
                            "name": "engine",
                            "in": "query",
                            "schema": {
                                "type": "string",
                                "enum": ["stockfish", "lichess", "chesscom"],
                                "default": "stockfish"
                            }
                        },
                        {
                            "name": "fen",
                            "in": "query",
                            "schema": {
                                "type": "string"
                            },
                            "description": "Optional FEN for position sync"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Capture moves returned",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "capture_moves": {"type": "array"},
                                            "total_captures": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Game not found"
                        },
                        "500": {
                            "description": "Analysis error"
                        }
                    }
                }
            },
            "/legal_moves": {
                "get": {
                    "tags": ["Moves"],
                    "summary": "Get legal moves",
                    "description": "Returns legal moves for a specific square",
                    "parameters": [
                        {
                            "name": "game_id",
                            "in": "query",
                            "schema": {
                                "type": "string",
                                "default": "default"
                            }
                        },
                        {
                            "name": "square",
                            "in": "query",
                            "schema": {
                                "type": "string"
                            },
                            "description": "Square in algebraic notation (e.g., 'e2')"
                        },
                        {
                            "name": "fen",
                            "in": "query",
                            "schema": {
                                "type": "string"
                            },
                            "description": "Optional FEN for position sync"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Legal moves returned",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "legal_moves": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "to": {"type": "string"},
                                                        "move": {"type": "string"},
                                                        "is_capture": {"type": "boolean"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Game not found"
                        }
                    }
                }
            },
            "/compare_engines": {
                "post": {
                    "tags": ["Analysis"],
                    "summary": "Compare engines",
                    "description": "Compares the best move from different engines",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "game_id": {
                                            "type": "string",
                                            "default": "default"
                                        },
                                        "fen": {
                                            "type": "string",
                                            "description": "Optional FEN for position sync"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Engine comparison completed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "stockfish": {
                                                "type": "object",
                                                "properties": {
                                                    "best_move": {"type": "string"},
                                                    "evaluation": {"type": "number"},
                                                    "top_3": {"type": "array"}
                                                }
                                            },
                                            "lichess": {
                                                "type": "object",
                                                "properties": {
                                                    "best_move": {"type": "string"},
                                                    "evaluation": {"type": "number"},
                                                    "top_3": {"type": "array"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Game not found"
                        }
                    }
                }
            }
        }
    }
    return jsonify(spec)

@app.route('/new_game', methods=['POST'])
def new_game():
    """Starts a new game"""
    data = request.json
    game_id = data.get('game_id', 'default')
    player_color = data.get('color', 'white')
    engine_strength = data.get('engine_strength', 20)  # 1-20, 20 = maximum
    engine_type = data.get('engine', 'stockfish')  # stockfish, lichess, chesscom
    fen = data.get('fen')  # Optional FEN
    
    game_data = get_or_create_game(game_id, fen, player_color, engine_strength)
    game_data['current_engine'] = engine_type
    
    response = {
        'game_id': game_id,
        'fen': game_data['board'].fen(),
        'player_color': player_color,
        'engine_strength': engine_strength,
        'engine': engine_type
    }
    
    # If the player chose black, the engine makes the first move
    if player_color == 'black':
        analysis = get_engine_move(game_id, engine_type)
        if analysis:
            board = game_data['board']
            move = chess.Move.from_uci(analysis.best_move)
            board.push(move)
            game_data['moves'].append(analysis.best_move)
            response['ai_move'] = analysis.best_move
            response['fen'] = board.fen()
            response['analysis'] = asdict(analysis)
    
    return jsonify(response)

@app.route('/make_move', methods=['POST'])
def make_move():
    """Processes the player's move and responds with the selected engine"""
    data = request.json
    game_id = data.get('game_id', 'default')
    move_uci = data.get('move')
    fen = data.get('fen')  # Optional FEN for synchronization
    engine_type = data.get('engine', 'stockfish')  # Engine to use
    engine_strength = data.get('engine_strength', 20)
    
    # Get or create game from FEN
    game_data = get_or_create_game(game_id, fen, engine_strength=engine_strength)
    game_data['current_engine'] = engine_type
    board = game_data['board']
    
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            game_data['moves'].append(move_uci)
            
            response = {
                'success': True,
                'player_move': move_uci,
                'fen': board.fen(),
                'game_over': board.is_game_over(),
                'moves_history': game_data['moves'],
                'engine_used': engine_type
            }
            
            if not board.is_game_over():
                # Use the specified engine
                analysis = get_engine_move(game_id, engine_type)
                
                if analysis:
                    # Engine makes its move
                    ai_move = chess.Move.from_uci(analysis.best_move)
                    board.push(ai_move)
                    game_data['moves'].append(analysis.best_move)
                    
                    response['ai_move'] = analysis.best_move
                    response['fen'] = board.fen()
                    response['game_over'] = board.is_game_over()
                    response['analysis'] = asdict(analysis)
                else:
                    response['error'] = f'Engine {engine_type} failed to provide move'
            
            return jsonify(response)
        else:
            return jsonify({'error': 'Illegal move', 'fen': board.fen()}), 400
            
    except Exception as e:
        return jsonify({'error': str(e), 'fen': board.fen() if game_id in games else None}), 400

def get_engine_move(game_id: str, engine_type: str) -> Optional[EngineAnalysis]:
    """Gets the move from the specified engine"""
    if engine_type == 'stockfish':
        return analyze_position_stockfish(game_id, top_n=5)
    elif engine_type == 'lichess':
        return analyze_position_lichess(game_id, top_n=5)
    elif engine_type == 'chesscom':
        return analyze_position_chesscom(game_id)
    else:
        print(f"⚠️ Unknown engine type: {engine_type}, falling back to Stockfish")
        return analyze_position_stockfish(game_id, top_n=5)

@app.route('/sync_position', methods=['POST'])
def sync_position():
    """Synchronizes the board position with the backend (useful after reload)"""
    data = request.json
    game_id = data.get('game_id', 'default')
    fen = data.get('fen')
    player_color = data.get('player_color', 'white')
    engine_strength = data.get('engine_strength', 20)
    
    if not fen:
        return jsonify({'error': 'FEN required'}), 400
    
    game_data = get_or_create_game(game_id, fen, player_color, engine_strength)
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'fen': game_data['board'].fen(),
        'legal_moves': [m.uci() for m in game_data['board'].legal_moves],
        'is_game_over': game_data['board'].is_game_over()
    })

@app.route('/analyze_position', methods=['POST'])
def analyze_position():
    """Analyzes the current position with the chosen engine"""
    data = request.json
    game_id = data.get('game_id', 'default')
    engine_type = data.get('engine', 'stockfish')  # stockfish, lichess, chesscom
    top_n = data.get('top_moves', 5)
    depth = data.get('depth', 20)
    fen = data.get('fen')  # Optional FEN
    
    # Synchronize position if FEN is provided
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Game not found and no FEN provided'}), 404
    
    if engine_type == 'stockfish':
        analysis = analyze_position_stockfish(game_id, top_n, depth)
    elif engine_type == 'lichess':
        analysis = analyze_position_lichess(game_id, top_n)
    elif engine_type == 'chesscom':
        analysis = analyze_position_chesscom(game_id)
    else:
        return jsonify({'error': 'Invalid engine'}), 400
    
    if analysis:
        return jsonify(asdict(analysis))
    else:
        return jsonify({'error': 'Analysis error'}), 500

def analyze_position_stockfish(game_id: str, top_n: int = 5, depth: int = 20) -> Optional[EngineAnalysis]:
    """Analyzes position with local Stockfish - complete analysis"""
    if game_id not in games:
        return None
    
    board = games[game_id]['board']
    engine_strength = games[game_id].get('engine_strength', 20)
    
    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            # Configure engine strength (Skill Level 0-20)
            engine.configure({"Skill Level": engine_strength})
            
            # Multi-PV analysis to get top N moves
            info = engine.analyse(
                board, 
                chess.engine.Limit(depth=depth),
                multipv=top_n
            )
            
            top_moves = []
            for pv_info in info:
                move = pv_info['pv'][0]
                score = pv_info['score'].relative
                
                eval_score = 0
                is_mate = False
                mate_in = None
                
                if score.is_mate():
                    is_mate = True
                    mate_in = score.mate()
                    eval_score = 10000 if mate_in > 0 else -10000
                else:
                    eval_score = score.score()
                
                top_moves.append(MoveEvaluation(
                    move=move.uci(),
                    evaluation=eval_score,
                    is_mate=is_mate,
                    mate_in=mate_in,
                    is_capture=board.is_capture(move),
                    piece=board.piece_at(move.from_square).symbol(),
                    from_square=chess.square_name(move.from_square),
                    to_square=chess.square_name(move.to_square)
                ))
            
            # Analyze ALL legal moves
            all_moves = []
            for move in board.legal_moves:
                board.push(move)
                eval_info = engine.analyse(board, chess.engine.Limit(depth=10))
                board.pop()
                
                score = eval_info['score'].relative
                eval_score = 0
                is_mate = False
                mate_in = None
                
                if score.is_mate():
                    is_mate = True
                    mate_in = score.mate()
                    eval_score = 10000 if mate_in > 0 else -10000
                else:
                    eval_score = -score.score()  # Invert because it's relative to opponent
                
                all_moves.append(MoveEvaluation(
                    move=move.uci(),
                    evaluation=eval_score,
                    is_mate=is_mate,
                    mate_in=mate_in,
                    is_capture=board.is_capture(move),
                    piece=board.piece_at(move.from_square).symbol(),
                    from_square=chess.square_name(move.from_square),
                    to_square=chess.square_name(move.to_square)
                ))
            
            # Filter capture moves
            capture_moves = [m for m in all_moves if m.is_capture]
            
            # Sort all moves by evaluation
            all_moves.sort(key=lambda x: x.evaluation, reverse=True)
            capture_moves.sort(key=lambda x: x.evaluation, reverse=True)
            
            # Position evaluation (ALWAYS from white's perspective)
            main_eval = engine.analyse(board, chess.engine.Limit(depth=depth))
            position_eval = 0
            if main_eval['score'].relative.is_mate():
                mate_score = main_eval['score'].relative.mate()
                position_eval = 10000 if mate_score > 0 else -10000
            else:
                position_eval = main_eval['score'].relative.score()
            
            # If it's black's turn, invert the evaluation to be from white's perspective
            if board.turn == chess.BLACK:
                position_eval = -position_eval
            
            return EngineAnalysis(
                best_move=top_moves[0].move,
                top_moves=top_moves,
                all_legal_moves=all_moves,
                capture_moves=capture_moves,
                position_evaluation=position_eval,
                fen=board.fen()
            )
            
    except Exception as e:
        print(f"Error with Stockfish: {e}")
        return None

def analyze_position_lichess(game_id: str, top_n: int = 5) -> Optional[EngineAnalysis]:
    """Analyzes position using Lichess Cloud Evaluation API"""
    if game_id not in games:
        return None
    
    board = games[game_id]['board']
    fen = board.fen()
    
    try:
        # Lichess Cloud Eval API
        url = "https://lichess.org/api/cloud-eval"
        params = {
            'fen': fen,
            'multiPv': top_n
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'pvs' not in data or len(data['pvs']) == 0:
                return None
            
            top_moves = []
            for pv in data['pvs']:
                move_uci = pv['moves'].split()[0]
                move = chess.Move.from_uci(move_uci)
                
                cp = pv.get('cp')
                mate = pv.get('mate')
                
                eval_score = 0
                is_mate = False
                mate_in = None
                
                if mate is not None:
                    is_mate = True
                    mate_in = mate
                    eval_score = 10000 if mate > 0 else -10000
                elif cp is not None:
                    eval_score = cp
                
                top_moves.append(MoveEvaluation(
                    move=move_uci,
                    evaluation=eval_score,
                    is_mate=is_mate,
                    mate_in=mate_in,
                    is_capture=board.is_capture(move),
                    piece=board.piece_at(move.from_square).symbol(),
                    from_square=chess.square_name(move.from_square),
                    to_square=chess.square_name(move.to_square)
                ))
            
            # For Lichess, we generate all legal moves without deep evaluation
            all_moves = []
            for move in board.legal_moves:
                all_moves.append(MoveEvaluation(
                    move=move.uci(),
                    evaluation=0,  # Lichess doesn't evaluate all moves
                    is_mate=False,
                    mate_in=None,
                    is_capture=board.is_capture(move),
                    piece=board.piece_at(move.from_square).symbol(),
                    from_square=chess.square_name(move.from_square),
                    to_square=chess.square_name(move.to_square)
                ))
            
            capture_moves = [m for m in all_moves if m.is_capture]
            
            position_eval = top_moves[0].evaluation if top_moves else 0
            
            return EngineAnalysis(
                best_move=top_moves[0].move,
                top_moves=top_moves,
                all_legal_moves=all_moves,
                capture_moves=capture_moves,
                position_evaluation=position_eval,
                fen=fen
            )
        
        return None
        
    except Exception as e:
        print(f"Error with Lichess: {e}")
        return None

def analyze_position_chesscom(game_id: str) -> Optional[EngineAnalysis]:
    """Analyzes position using Chess.com - basic implementation with Stockfish"""
    if game_id not in games:
        return None
    
    board = games[game_id]['board']
    
    # Chess.com doesn't have a public direct analysis API
    # Use Stockfish as fallback but with different configuration
    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            # Quick analysis
            info = engine.analyse(board, chess.engine.Limit(depth=15), multipv=3)
            
            top_moves = []
            for pv_info in info:
                move = pv_info['pv'][0]
                score = pv_info['score'].relative
                
                eval_score = 0
                is_mate = False
                mate_in = None
                
                if score.is_mate():
                    is_mate = True
                    mate_in = score.mate()
                    eval_score = 10000 if mate_in > 0 else -10000
                else:
                    eval_score = score.score()
                
                top_moves.append(MoveEvaluation(
                    move=move.uci(),
                    evaluation=eval_score,
                    is_mate=is_mate,
                    mate_in=mate_in,
                    is_capture=board.is_capture(move),
                    piece=board.piece_at(move.from_square).symbol(),
                    from_square=chess.square_name(move.from_square),
                    to_square=chess.square_name(move.to_square)
                ))
            
            all_moves = []
            for move in board.legal_moves:
                all_moves.append(MoveEvaluation(
                    move=move.uci(),
                    evaluation=0,
                    is_mate=False,
                    mate_in=None,
                    is_capture=board.is_capture(move),
                    piece=board.piece_at(move.from_square).symbol(),
                    from_square=chess.square_name(move.from_square),
                    to_square=chess.square_name(move.to_square)
                ))
            
            capture_moves = [m for m in all_moves if m.is_capture]
            
            # Position evaluation (ALWAYS from white's perspective)
            main_eval = engine.analyse(board, chess.engine.Limit(depth=15))
            position_eval = 0
            if main_eval['score'].relative.is_mate():
                mate_score = main_eval['score'].relative.mate()
                position_eval = 10000 if mate_score > 0 else -10000
            else:
                position_eval = main_eval['score'].relative.score()
            
            # If it's black's turn, invert for white's perspective
            if board.turn == chess.BLACK:
                position_eval = -position_eval
            
            return EngineAnalysis(
                best_move=top_moves[0].move if top_moves else None,
                top_moves=top_moves,
                all_legal_moves=all_moves,
                capture_moves=capture_moves,
                position_evaluation=position_eval,
                fen=board.fen()
            )
        
    except Exception as e:
        print(f"Error with Chess.com fallback: {e}")
        return None

@app.route('/set_engine_strength', methods=['POST'])
def set_engine_strength():
    """Changes the engine strength (1-20)"""
    data = request.json
    game_id = data.get('game_id', 'default')
    strength = data.get('strength', 20)
    fen = data.get('fen')  # Optional FEN
    
    # Synchronize if FEN is provided
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    if not 1 <= strength <= 20:
        return jsonify({'error': 'Strength must be between 1 and 20'}), 400
    
    games[game_id]['engine_strength'] = strength
    
    return jsonify({
        'success': True,
        'engine_strength': strength,
        'message': f'Engine strength set to {strength}/20'
    })

@app.route('/get_capture_moves', methods=['GET'])
def get_capture_moves():
    """Returns only capture moves with evaluation"""
    game_id = request.args.get('game_id', 'default')
    engine = request.args.get('engine', 'stockfish')
    fen = request.args.get('fen')  # Optional FEN
    
    # Synchronize if FEN is provided
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    if engine == 'stockfish':
        analysis = analyze_position_stockfish(game_id, top_n=5)
    elif engine == 'lichess':
        analysis = analyze_position_lichess(game_id, top_n=5)
    else:
        analysis = analyze_position_chesscom(game_id)
    
    if analysis:
        return jsonify({
            'capture_moves': [asdict(m) for m in analysis.capture_moves],
            'total_captures': len(analysis.capture_moves)
        })
    
    return jsonify({'error': 'Analysis error'}), 500

@app.route('/legal_moves', methods=['GET'])
def legal_moves():
    """Returns legal moves for a square with evaluation"""
    game_id = request.args.get('game_id', 'default')
    square = request.args.get('square')
    fen = request.args.get('fen')  # Optional FEN
    
    # Synchronize if FEN is provided
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    board = games[game_id]['board']
    legal = []
    
    if square:
        square_idx = chess.parse_square(square)
        for move in board.legal_moves:
            if move.from_square == square_idx:
                legal.append({
                    'to': chess.square_name(move.to_square),
                    'move': move.uci(),
                    'is_capture': board.is_capture(move)
                })
    
    return jsonify({'legal_moves': legal})

@app.route('/compare_engines', methods=['POST'])
def compare_engines():
    """Compares the best move from different engines"""
    data = request.json
    game_id = data.get('game_id', 'default')
    fen = data.get('fen')  # Optional FEN
    
    # Synchronize if FEN is provided
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    results = {}
    
    # Stockfish
    sf_analysis = analyze_position_stockfish(game_id, top_n=3)
    if sf_analysis:
        results['stockfish'] = {
            'best_move': sf_analysis.best_move,
            'evaluation': sf_analysis.position_evaluation,
            'top_3': [asdict(m) for m in sf_analysis.top_moves[:3]]
        }
    
    # Lichess
    li_analysis = analyze_position_lichess(game_id, top_n=3)
    if li_analysis:
        results['lichess'] = {
            'best_move': li_analysis.best_move,
            'evaluation': li_analysis.position_evaluation,
            'top_3': [asdict(m) for m in li_analysis.top_moves[:3]]
        }
    
    return jsonify(results)

@app.route('/')
def home():
    """Home page with API information"""
    return jsonify({
        'message': 'Advanced Chess API',
        'version': '1.0.0',
        'documentation': '/api/docs',
        'swagger_json': '/api/swagger.json',
        'endpoints': {
            'new_game': 'POST /new_game',
            'make_move': 'POST /make_move',
            'sync_position': 'POST /sync_position',
            'analyze_position': 'POST /analyze_position',
            'set_engine_strength': 'POST /set_engine_strength',
            'get_capture_moves': 'GET /get_capture_moves',
            'legal_moves': 'GET /legal_moves',
            'compare_engines': 'POST /compare_engines'
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("♟️  ADVANCED CHESS SERVER (WITH SWAGGER UI)")
    print("=" * 60)
    print("📍 API URL: http://localhost:5000")
    print("📚 Swagger UI: http://localhost:5000/api/docs")
    print("📄 OpenAPI Spec: http://localhost:5000/api/swagger.json")
    print("\n📊 Features:")
    print("  ✓ FEN support in all endpoints")
    print("  ✓ Automatic position synchronization")
    print("  ✓ Multi-engine in make_move (Stockfish, Lichess, Chess.com)")
    print("  ✓ Analysis of ALL legal moves")
    print("  ✓ Configurable strength level (1-20)")
    print("  ✓ Interactive Swagger UI for testing")
    print("\n🔌 Endpoints:")
    print("  POST /new_game - New game (supports FEN)")
    print("  POST /make_move - Move with selected engine")
    print("  POST /sync_position - Synchronize position with FEN")
    print("  POST /analyze_position - Complete analysis (supports FEN)")
    print("  POST /set_engine_strength - Adjust strength (supports FEN)")
    print("  GET  /get_capture_moves - Captures only (supports FEN)")
    print("  GET  /legal_moves - Legal moves (supports FEN)")
    print("  POST /compare_engines - Compare engines (supports FEN)")
    print("\n💡 Quick Start:")
    print("  1. Install dependencies: pip install flask-swagger-ui")
    print("  2. Visit http://localhost:5000/api/docs to test the API")
    print("  3. Try the endpoints directly from the Swagger interface")
    print("=" * 60)
    app.run(debug=True, port=5000)