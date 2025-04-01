import numpy as np
import chess

def move_to_index(move_uci: str) -> int:
    move = chess.Move.from_uci(move_uci)
    from_square = move.from_square
    to_square = move.to_square

    return from_square * 64 + to_square

def index_to_move(index: int) -> str:
    from_square = index // 64
    to_square = index % 64
    move = chess.Move(from_square, to_square)
    return move.uci()

def dummy_policy_vector() -> np.ndarray:
    return np.zeros(4096, dtype=np.float32)

