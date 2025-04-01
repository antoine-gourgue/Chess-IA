import os
import numpy as np
import tensorflow as tf
from datetime import datetime
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau

from app.model.alphazero_model import build_dual_model
from app.utils.fen_encoder import fen_to_tensor
from app.utils.move_encoder import dummy_policy_vector  # ⚠️ Doit retourner un int

# Fixer une seed pour reproductibilité
tf.random.set_seed(42)
np.random.seed(42)

def load_training_data(path: str):
    print("📦 Chargement des données...")
    X, y_policy, y_value = [], [], []

    with open(path, "r", encoding="utf-8") as file:
        for idx, line in enumerate(file):
            try:
                fen, eval_str = line.strip().split(',')
                tensor = fen_to_tensor(fen)

                policy = dummy_policy_vector()
                eval_cp = float(eval_str)
                value = max(-1, min(1, eval_cp / 100))

                X.append(tensor)
                y_policy.append(policy)
                y_value.append(value)
            except Exception as e:
                print(f"⚠️ Ligne {idx+1} ignorée: {line.strip()} ({e})")

    X = np.array(X)
    y_policy = np.array(y_policy, dtype=np.int32)
    y_value = np.array(y_value, dtype=np.float32)

    print(f"✅ Données chargées : {len(X)} exemples valides\n")
    return X, y_policy, y_value

def get_callbacks():
    log_dir = os.path.join("logs_alphazero", datetime.now().strftime("%Y%m%d-%H%M%S"))
    return [
        EarlyStopping(patience=5, restore_best_weights=True, verbose=1),
        ModelCheckpoint("models/best_alphazero_model.keras", save_best_only=True, verbose=1),
        ReduceLROnPlateau(factor=0.5, patience=3, verbose=1),
        TensorBoard(log_dir=log_dir)
    ]

def train_model(X, y_policy, y_value):
    # Split
    split_idx = int(0.9 * len(X))
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_policy_train, y_policy_val = y_policy[:split_idx], y_policy[split_idx:]
    y_value_train, y_value_val = y_value[:split_idx], y_value[split_idx:]

    print("🧠 Création du modèle dual (policy + value)...")
    model = build_dual_model()

    print("🚀 Début de l'entraînement...\n")
    model.fit(
        X_train,
        {"policy_output": y_policy_train, "value_output": y_value_train},
        validation_data=(X_val, {"policy_output": y_policy_val, "value_output": y_value_val}),
        epochs=30,
        batch_size=64,
        callbacks=get_callbacks(),
        verbose=2
    )

    os.makedirs("models", exist_ok=True)
    model.save("models/final_alphazero_model.keras")
    print("\n✅ Entraînement terminé et modèle sauvegardé dans le dossier `models/`")

def main():
    X, y_policy, y_value = load_training_data("app/data/fen_analysis.csv")
    if len(X) < 10:
        print("❌ Pas assez de données pour entraîner un modèle.")
        return
    train_model(X, y_policy, y_value)

if __name__ == "__main__":
    main()
