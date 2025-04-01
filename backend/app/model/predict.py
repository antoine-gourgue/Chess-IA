import numpy as np
import chess
from app.model.cnn_model import build_chess_cnn
from app.utils.fen_encoder import fen_to_tensor
from app.utils.move_encoder import move_to_index, index_to_move

_model = None

def load_model_once():
    global _model
    if _model is None:
        _model = build_chess_cnn(input_shape=(8, 8, 12))
        _model.load_weights("/Users/antoinegourgue/Desktop/Projects/Chess-IA/backend/best_model_chess.h5")
    return _model

def load_model(path: str):
    model = build_chess_cnn()
    model.load_weights(path)
    return model


def predict_best_legal_move(fen: str, model=None) -> str:
    board = chess.Board(fen)
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return "no_legal_moves"

    x = fen_to_tensor(fen)
    x = np.expand_dims(x, axis=0)

    if model is None:
        model = load_model_once()

    probs = model.predict(x, verbose=0)[0]
    legal_move_indices = [move_to_index(m.uci()) for m in legal_moves]
    legal_probs = [(idx, probs[idx]) for idx in legal_move_indices]
    best_move_idx, _ = max(legal_probs, key=lambda x: x[1])
    return index_to_move(best_move_idx)
