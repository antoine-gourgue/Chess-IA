from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard
from app.model.cnn_model import build_chess_cnn
from app.utils.dataset_loader import load_dataset_from_file

def main():
    print("📦 Chargement du dataset...")
    X_train, y_train, X_val, y_val = load_dataset_from_file("/Users/antoinegourgue/Desktop/Projects/Chess-IA/backend/app/data/fen_stockfish.txt")

    print(f"✅ {len(X_train)} exemples d'entraînement / {len(X_val)} validation")

    print("🧠 Création du modèle CNN...")
    model = build_chess_cnn(input_shape=(8, 8, 12), num_classes=4096)

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        ModelCheckpoint('/Users/antoinegourgue/Desktop/Projects/Chess-IA/backend/best_model_chess.h5', monitor='val_loss', save_best_only=True),
        TensorBoard(log_dir='logs')
    ]

    print("🚀 Entraînement du modèle...")
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=20,
        batch_size=64,
        callbacks=callbacks
    )

    model.save("models/final_chess_model.h5")
    print("✅ Modèle final sauvegardé avec succès.")

if __name__ == '__main__':
    main()
