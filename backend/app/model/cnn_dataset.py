import tensorflow as tf
import numpy as np
from app.utils.fen_encoder import fen_to_tensor
from app.utils.move_encoder import move_to_index


def parse_line(line: str):
    fen, move = line.strip().split("|")
    x = fen_to_tensor(fen)
    y = move_to_index(move)
    return x, y


def load_dataset(file_path: str, max_samples=50000):
    X = []
    y = []

    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_samples:
                break
            try:
                x_tensor, label = parse_line(line)
                X.append(x_tensor)
                y.append(label)
            except Exception as e:
                print(f"Erreur à la ligne {i} : {e}")

    X = np.array(X, dtype=np.uint8)
    y = np.array(y, dtype=np.int32)
    return X, y


def get_tf_dataset(X, y, batch_size=64):
    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    dataset = dataset.shuffle(10000).batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return dataset

if __name__ == "__main__":
    X, y = load_dataset("/Users/antoinegourgue/Desktop/Projects/Chess-IA/backend/app/data/fen_stockfish.txt", max_samples=100)
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    print("Premier label (mouvement encodé):", y[0])
