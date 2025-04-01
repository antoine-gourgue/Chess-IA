import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, ReLU, Dense, Flatten, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

from app.utils.fen_encoder import fen_to_tensor_25
from app.utils.move_encoder import move_to_index


def load_training_data(path):
    X, y_policy, y_value = [], [], []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                if line.startswith("FEN"):
                    continue
                fen, move_eval = line.strip().split(",")
                move, eval_str = move_eval.split("|")

                board_tensor = fen_to_tensor_25(fen)
                X.append(board_tensor)
                y_policy.append(move_to_index(move))
                y_value.append(float(eval_str) / 100.0)  # Scale the evaluation to [-1, 1] approx

            except ValueError:
                print(f"⚠️ Ligne ignorée: {line.strip()}")

    X = np.array(X)
    y_policy = np.array(y_policy, dtype=np.int32)
    y_value = np.array(y_value)
    return X, y_policy, y_value


def build_dual_model(input_shape=(8, 8, 25), num_classes=4096):
    inputs = Input(shape=input_shape)

    x = Conv2D(64, (3, 3), padding="same")(inputs)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    x = Conv2D(128, (3, 3), padding="same")(x)
    x = BatchNormalization()(x)
    x = ReLU()(x)

    x = Flatten()(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.3)(x)

    policy_head = Dense(num_classes, activation="softmax", name="policy_output")(x)
    value_head = Dense(1, activation="tanh", name="value_output")(x)

    model = Model(inputs=inputs, outputs=[policy_head, value_head])
    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss={
            "policy_output": "sparse_categorical_crossentropy",
            "value_output": "mean_squared_error",
        },
        metrics={
            "policy_output": "accuracy",
            "value_output": "mse",
        },
    )
    return model


def main():
    print("📦 Chargement des données...")
    X, y_policy, y_value = load_training_data("/Users/antoinegourgue/Desktop/Projects/Chess-IA/backend/app/data/fen_analysis.csv")
    print(f"✅ Dataset chargé : {len(X)} exemples")

    print("🧠 Création du modèle dual (policy + value)...")
    model = build_dual_model()

    print("🚀 Entraînement du modèle...")
    X_train, X_val, y_policy_train, y_policy_val, y_value_train, y_value_val = train_test_split(
        X, y_policy, y_value, test_size=0.1, random_state=42
    )

    model.fit(
        X_train,
        {"policy_output": y_policy_train, "value_output": y_value_train},
        validation_data=(X_val, {"policy_output": y_policy_val, "value_output": y_value_val}),
        epochs=30,
        batch_size=64,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint("model_alphazero_best.h5", save_best_only=True)
        ]
    )

    model.save("model_alphazero_final.h5")
    print("✅ Modèle final sauvegardé avec succès.")


if __name__ == "__main__":
    main()