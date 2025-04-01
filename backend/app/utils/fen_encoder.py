import numpy as np
import chess

PIECE_TO_INDEX = {
    'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
    'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
}

def fen_to_tensor(fen: str) -> np.ndarray:
    board = chess.Board(fen)
    tensor = np.zeros((8, 8, 12), dtype=np.float32)

    rows = fen.split(' ')[0].split('/')
    for row_idx, row in enumerate(rows):
        col_idx = 0
        for char in row:
            if char.isdigit():
                col_idx += int(char)
            elif char in PIECE_TO_INDEX:
                tensor[row_idx, col_idx, PIECE_TO_INDEX[char]] = 1
                col_idx += 1

    return tensor


def fen_to_tensor_25(fen: str) -> np.ndarray:
    board = chess.Board(fen)
    tensor = np.zeros((8, 8, 25), dtype=np.float32)

    rows = fen.split(' ')[0].split('/')
    for row_idx, row in enumerate(rows):
        col_idx = 0
        for char in row:
            if char.isdigit():
                col_idx += int(char)
            elif char in PIECE_TO_INDEX:
                tensor[row_idx, col_idx, PIECE_TO_INDEX[char]] = 1
                col_idx += 1

    tensor[:, :, 12] = 1 if board.turn == chess.WHITE else 0

    for i, piece in enumerate([chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]):
        squares = board.pieces(piece, board.turn)
        attacks = [board.attacks(sq) for sq in squares]
        for attack in attacks:
            for sq in attack:
                row, col = divmod(sq, 8)
                tensor[row, col, 13 + i] = 1

    board.turn = not board.turn
    for i, piece in enumerate([chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]):
        squares = board.pieces(piece, board.turn)
        attacks = [board.attacks(sq) for sq in squares]
        for attack in attacks:
            for sq in attack:
                row, col = divmod(sq, 8)
                tensor[row, col, 19 + i] = 1
    board.turn = not board.turn

    return tensor
