<template>
  <main class="min-h-screen bg-gray-50 py-16 px-4 sm:px-6 lg:px-16">
    <header class="text-center mb-16">
      <h1 class="text-4xl sm:text-5xl font-bold text-gray-800 mb-4">
        Intelligence Artificielle vs Intelligence Artificielle
      </h1>
      <p class="text-lg text-gray-500 max-w-2xl mx-auto">
        Observez une partie d'échecs entre deux intelligences artificielles. Chaque coup est choisi de manière stratégique selon le modèle d'apprentissage.
      </p>
    </header>

    <section class="flex flex-col items-center gap-10">
      <div class="w-full max-w-3xl bg-white rounded-xl shadow p-6">
        <ClientOnly>
          <TheChessboard
              ref="chessboard"
              board-class="rounded"
              :animationDuration="300"
              :arePiecesDraggable="false"
              boardOrientation="white"
              @board-created="onBoardCreated"
          />
        </ClientOnly>

        <div class="flex justify-between items-center mt-6 text-gray-700">
          <p><strong>Tour :</strong> {{ turn }}</p>
          <p><strong>Dernier coup :</strong> {{ lastMove || '—' }}</p>
          <p><strong>Status :</strong> {{ status }}</p>
        </div>

        <div class="flex justify-center gap-4 mt-6">
          <button
              @click="startMatch"
              class="bg-gray-800 text-white px-6 py-2 rounded-full hover:bg-gray-700 transition"
              :disabled="running"
          >
            Lancer la partie IA vs IA
          </button>

          <button
              @click="resetGame"
              class="border border-gray-300 text-gray-800 px-6 py-2 rounded-full hover:bg-gray-100 transition"
              :disabled="running"
          >
            Réinitialiser
          </button>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Chess } from 'chess.js'
import { TheChessboard } from 'vue3-chessboard'
import 'vue3-chessboard/style.css'
import { getBestMove } from '@/utils/api'

const game = new Chess()
const boardApi = ref<any>(null)

const lastMove = ref('')
const turn = ref<'white' | 'black'>('white')
const status = ref('En attente')
const running = ref(false)

const fenHistory = new Map<string, number>()

function onBoardCreated(api: any) {
  boardApi.value = api
  api.setPosition(game.fen())
}

function resetGame() {
  game.reset()
  fenHistory.clear()
  boardApi.value?.setPosition(game.fen())
  lastMove.value = ''
  turn.value = 'white'
  status.value = 'En attente'
  running.value = false
}

function updateFenHistory(fen: string) {
  const count = fenHistory.get(fen) || 0
  fenHistory.set(fen, count + 1)
}

function startMatch() {
  resetGame()
  running.value = true
  status.value = 'En cours...'
  playNext()
}

async function playNext() {
  const currentFen = game.fen()
  updateFenHistory(currentFen)

  if (game.isGameOver()) {
    console.log('⛔ Fin de partie détectée')
    console.log('Checkmate:', game.isCheckmate())
    console.log('Stalemate:', game.isStalemate())
    console.log('Draw:', game.isDraw())
    console.log('Repetition:', game.isThreefoldRepetition())
    console.log('Matériel insuffisant:', game.isInsufficientMaterial())

    status.value = game.isCheckmate()
        ? `Mat pour ${turn.value === 'white' ? 'noir' : 'blanc'}`
        : 'Match nul'
    running.value = false
    return
  }

  let bestMove = await getBestMove(currentFen)
  let moveResult = null
  let attempts = 0

  while (attempts < 10) {
    if (!bestMove || bestMove === 'no_legal_moves') {
      status.value = '❌ Aucun coup reçu ou valide'
      running.value = false
      return
    }

    const tempGame = new Chess(currentFen)
    const testMove = tempGame.move({
      from: bestMove.slice(0, 2),
      to: bestMove.slice(2, 4),
      promotion: 'q',
    })

    if (testMove) {
      const nextFen = tempGame.fen()
      const repetitionCount = fenHistory.get(nextFen) || 0

      if (repetitionCount < 2) {
        // 👍 Valide, pas de répétition critique
        moveResult = game.move(testMove)
        updateFenHistory(nextFen)
        break
      } else {
        console.warn(`[Tentative ${attempts + 1}] Coup évité : répétition détectée (${nextFen})`)
      }
    }

    // Retente avec un nouveau coup IA
    bestMove = await getBestMove(currentFen)
    attempts++
  }

  if (!moveResult) {
    status.value = '❌ Répétition forcée, aucun autre coup trouvé'
    running.value = false
    return
  }

  await boardApi.value?.move({
    from: moveResult.from,
    to: moveResult.to,
    promotion: moveResult.promotion,
  })

  lastMove.value = `${moveResult.from}${moveResult.to}`
  turn.value = game.turn() === 'w' ? 'white' : 'black'

  setTimeout(playNext, 800)
}
</script>
