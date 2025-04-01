from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.model.predict import load_model_once, predict_best_legal_move
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    fen: str

@app.post("/predict")
def predict_move(request: PredictRequest):
    fen = request.fen
    try:
        model = load_model_once()
        best_move = predict_best_legal_move(fen, model)
        return {"best_move": best_move}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Chess-IA API"}

