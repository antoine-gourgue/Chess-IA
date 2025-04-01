export async function getBestMove(fen: string): Promise<string> {
    const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fen }),
    })

    const data = await res.json()
    return data.best_move
}
