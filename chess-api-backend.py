from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
import requests
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

app = Flask(__name__)
CORS(app)

# Configuración de Stockfish
STOCKFISH_PATH = "stockfish"  # Ajustar según sistema operativo
# STOCKFISH_PATH = "C:\\Path\\To\\stockfish.exe"  # Windows

# Almacenamiento de partidas
games = {}

@dataclass
class MoveEvaluation:
    move: str
    evaluation: float  # En centipawns o mate
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
    """Obtiene un juego existente o crea uno nuevo desde un FEN"""
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
        # Si se proporciona FEN, actualizar la posición
        games[game_id]['board'] = chess.Board(fen)
        print(f"🔄 Game {game_id} updated with new FEN")
    
    return games[game_id]

@app.route('/new_game', methods=['POST'])
def new_game():
    """Inicia una nueva partida"""
    data = request.json
    game_id = data.get('game_id', 'default')
    player_color = data.get('color', 'white')
    engine_strength = data.get('engine_strength', 20)  # 1-20, 20 = máximo
    engine_type = data.get('engine', 'stockfish')  # stockfish, lichess, chesscom
    fen = data.get('fen')  # FEN opcional
    
    game_data = get_or_create_game(game_id, fen, player_color, engine_strength)
    game_data['current_engine'] = engine_type
    
    response = {
        'game_id': game_id,
        'fen': game_data['board'].fen(),
        'player_color': player_color,
        'engine_strength': engine_strength,
        'engine': engine_type
    }
    
    # Si el jugador eligió negras, el motor hace el primer movimiento
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
    """Procesa el movimiento del jugador y responde con el motor seleccionado"""
    data = request.json
    game_id = data.get('game_id', 'default')
    move_uci = data.get('move')
    fen = data.get('fen')  # FEN opcional para sincronización
    engine_type = data.get('engine', 'stockfish')  # Motor a usar
    engine_strength = data.get('engine_strength', 20)
    
    # Obtener o crear juego desde FEN
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
                # Usar el motor especificado
                analysis = get_engine_move(game_id, engine_type)
                
                if analysis:
                    # Motor hace su movimiento
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
            return jsonify({'error': 'Movimiento ilegal', 'fen': board.fen()}), 400
            
    except Exception as e:
        return jsonify({'error': str(e), 'fen': board.fen() if game_id in games else None}), 400

def get_engine_move(game_id: str, engine_type: str) -> Optional[EngineAnalysis]:
    """Obtiene el movimiento del motor especificado"""
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
    """Sincroniza la posición del tablero con el backend (útil después de recargar)"""
    data = request.json
    game_id = data.get('game_id', 'default')
    fen = data.get('fen')
    player_color = data.get('player_color', 'white')
    engine_strength = data.get('engine_strength', 20)
    
    if not fen:
        return jsonify({'error': 'FEN requerido'}), 400
    
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
    """Analiza la posición actual con el motor elegido"""
    data = request.json
    game_id = data.get('game_id', 'default')
    engine_type = data.get('engine', 'stockfish')  # stockfish, lichess, chesscom
    top_n = data.get('top_moves', 5)
    depth = data.get('depth', 20)
    fen = data.get('fen')  # FEN opcional
    
    # Sincronizar posición si se proporciona FEN
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Partida no encontrada y no se proporcionó FEN'}), 404
    
    if engine_type == 'stockfish':
        analysis = analyze_position_stockfish(game_id, top_n, depth)
    elif engine_type == 'lichess':
        analysis = analyze_position_lichess(game_id, top_n)
    elif engine_type == 'chesscom':
        analysis = analyze_position_chesscom(game_id)
    else:
        return jsonify({'error': 'Motor no válido'}), 400
    
    if analysis:
        return jsonify(asdict(analysis))
    else:
        return jsonify({'error': 'Error en el análisis'}), 500

def analyze_position_stockfish(game_id: str, top_n: int = 5, depth: int = 20) -> Optional[EngineAnalysis]:
    """Analiza posición con Stockfish local - análisis completo"""
    if game_id not in games:
        return None
    
    board = games[game_id]['board']
    engine_strength = games[game_id].get('engine_strength', 20)
    
    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            # Configurar fuerza del motor (Skill Level 0-20)
            engine.configure({"Skill Level": engine_strength})
            
            # Análisis multi-PV para obtener top N movimientos
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
            
            # Analizar TODOS los movimientos legales
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
                    eval_score = -score.score()  # Invertir porque es relativo al oponente
                
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
            
            # Filtrar movimientos de captura
            capture_moves = [m for m in all_moves if m.is_capture]
            
            # Ordenar todos los movimientos por evaluación
            all_moves.sort(key=lambda x: x.evaluation, reverse=True)
            capture_moves.sort(key=lambda x: x.evaluation, reverse=True)
            
            # Evaluación de la posición (SIEMPRE desde perspectiva de blancas)
            main_eval = engine.analyse(board, chess.engine.Limit(depth=depth))
            position_eval = 0
            if main_eval['score'].relative.is_mate():
                mate_score = main_eval['score'].relative.mate()
                position_eval = 10000 if mate_score > 0 else -10000
            else:
                position_eval = main_eval['score'].relative.score()
            
            # Si es turno de negras, invertir la evaluación para que sea desde perspectiva de blancas
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
        print(f"Error con Stockfish: {e}")
        return None

def analyze_position_lichess(game_id: str, top_n: int = 5) -> Optional[EngineAnalysis]:
    """Analiza posición usando Lichess Cloud Evaluation API"""
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
            
            # Para Lichess, generamos todos los movimientos legales sin evaluación profunda
            all_moves = []
            for move in board.legal_moves:
                all_moves.append(MoveEvaluation(
                    move=move.uci(),
                    evaluation=0,  # Lichess no evalúa todos los movimientos
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
        print(f"Error con Lichess: {e}")
        return None

def analyze_position_chesscom(game_id: str) -> Optional[EngineAnalysis]:
    """Analiza posición usando Chess.com - implementación básica con Stockfish"""
    if game_id not in games:
        return None
    
    board = games[game_id]['board']
    
    # Chess.com no tiene API pública de análisis directo
    # Usar Stockfish como fallback pero con configuración diferente
    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            # Análisis rápido
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
            
            # Evaluación de posición (SIEMPRE desde perspectiva de blancas)
            main_eval = engine.analyse(board, chess.engine.Limit(depth=15))
            position_eval = 0
            if main_eval['score'].relative.is_mate():
                mate_score = main_eval['score'].relative.mate()
                position_eval = 10000 if mate_score > 0 else -10000
            else:
                position_eval = main_eval['score'].relative.score()
            
            # Si es turno de negras, invertir para perspectiva de blancas
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
        print(f"Error con Chess.com fallback: {e}")
        return None

@app.route('/set_engine_strength', methods=['POST'])
def set_engine_strength():
    """Cambia la fuerza del motor (1-20)"""
    data = request.json
    game_id = data.get('game_id', 'default')
    strength = data.get('strength', 20)
    fen = data.get('fen')  # FEN opcional
    
    # Sincronizar si se proporciona FEN
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Partida no encontrada'}), 404
    
    if not 1 <= strength <= 20:
        return jsonify({'error': 'Fuerza debe estar entre 1 y 20'}), 400
    
    games[game_id]['engine_strength'] = strength
    
    return jsonify({
        'success': True,
        'engine_strength': strength,
        'message': f'Fuerza del motor ajustada a {strength}/20'
    })

@app.route('/get_capture_moves', methods=['GET'])
def get_capture_moves():
    """Devuelve solo los movimientos de captura con evaluación"""
    game_id = request.args.get('game_id', 'default')
    engine = request.args.get('engine', 'stockfish')
    fen = request.args.get('fen')  # FEN opcional
    
    # Sincronizar si se proporciona FEN
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Partida no encontrada'}), 404
    
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
    
    return jsonify({'error': 'Error en el análisis'}), 500

@app.route('/legal_moves', methods=['GET'])
def legal_moves():
    """Devuelve los movimientos legales para una casilla con evaluación"""
    game_id = request.args.get('game_id', 'default')
    square = request.args.get('square')
    fen = request.args.get('fen')  # FEN opcional
    
    # Sincronizar si se proporciona FEN
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Partida no encontrada'}), 404
    
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
    """Compara el mejor movimiento de diferentes motores"""
    data = request.json
    game_id = data.get('game_id', 'default')
    fen = data.get('fen')  # FEN opcional
    
    # Sincronizar si se proporciona FEN
    if fen:
        get_or_create_game(game_id, fen)
    
    if game_id not in games:
        return jsonify({'error': 'Partida no encontrada'}), 404
    
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

if __name__ == '__main__':
    print("=" * 60)
    print("♟️  SERVIDOR DE AJEDREZ AVANZADO (REFACTORIZADO)")
    print("=" * 60)
    print("📍 URL: http://localhost:5000")
    print("\n📊 Características:")
    print("  ✓ Soporte para FEN en todos los endpoints")
    print("  ✓ Sincronización automática de posiciones")
    print("  ✓ Multi-motor en make_move (Stockfish, Lichess, Chess.com)")
    print("  ✓ Análisis de TODOS los movimientos legales")
    print("  ✓ Nivel de fuerza configurable (1-20)")
    print("\n🔌 Endpoints:")
    print("  POST /new_game - Nueva partida (soporta FEN)")
    print("  POST /make_move - Movimiento con motor seleccionado")
    print("  POST /sync_position - Sincronizar posición con FEN")
    print("  POST /analyze_position - Análisis completo (soporta FEN)")
    print("  POST /set_engine_strength - Ajustar fuerza (soporta FEN)")
    print("  GET  /get_capture_moves - Solo capturas (soporta FEN)")
    print("  GET  /legal_moves - Movimientos legales (soporta FEN)")
    print("  POST /compare_engines - Comparar motores (soporta FEN)")
    print("=" * 60)
    app.run(debug=True, port=5000)