import numpy as np
from sklearn.model_selection import train_test_split
from app.utils.fen_encoder import fen_to_tensor

def move_to_class(move: str) -> int:
    """Encode un coup UCI (ex: e2e4) en entier entre 0 et 4095"""
    from_square = move[:2]
    to_square = move[2:4]

    def square_to_index(square: str) -> int:
        col = ord(square[0]) - ord('a')  # a=0, b=1, ...
        row = 8 - int(square[1])         # 8=0, 7=1, ..., 1=7
        return row * 8 + col

    from_idx = square_to_index(from_square)
    to_idx = square_to_index(to_square)
    return from_idx * 64 + to_idx  # 0-4095

def load_dataset_from_file(filepath: str, test_size: float = 0.1):
    X, y = [], []

    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            if '|' not in line:
                continue
            fen, move = line.strip().split("|")
            try:
                tensor = fen_to_tensor(fen)  # (8,8,12)
                label = move_to_class(move)  # int
                X.append(tensor)
                y.append(label)
            except Exception as e:
                print(f"⛔️ Erreur sur ligne : {line.strip()} — {e}")

    X = np.array(X)
    y = np.array(y)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=42, shuffle=True
    )

    return X_train, y_train, X_val, y_val
