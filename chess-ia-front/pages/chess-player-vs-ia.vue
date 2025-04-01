<template>
  <main class="min-h-screen bg-gray-50 py-16 px-4 sm:px-6 lg:px-16">
    <header class="text-center mb-16">
      <h1 class="text-4xl sm:text-5xl font-bold text-gray-800 mb-4">
        Joueur vs Intelligence Artificielle
      </h1>
      <p class="text-lg text-gray-500 max-w-2xl mx-auto">
        Affrontez notre moteur IA stratégique. Choisissez votre camp, jouez votre coup, et laissez l'IA répondre.
      </p>
    </header>

    <section class="flex flex-col items-center gap-10">
      <div class="w-full max-w-3xl bg-white rounded-xl shadow p-6">
        <div v-if="!gameStarted" class="mb-8 text-center">
          <label for="color" class="block text-gray-700 font-medium mb-2">Choisissez votre couleur :</label>
          <select id="color" v-model="playerColor" class="p-2 border rounded w-40 text-center">
            <option value="white">Blancs</option>
            <option value="black">Noirs</option>
          </select>
          <button
              @click="startGame"
              class="ml-4 bg-gray-800 text-white px-5 py-2 rounded-full hover:bg-gray-700 transition"
          >
            Commencer la partie
          </button>
        </div>

        <ClientOnly>
          <TheChessboard
              v-if="gameStarted"
              ref="chessboard"
              board-class="rounded"
              :animationDuration="300"
              :arePiecesDraggable="isPlayerTurn"
              :boardOrientation="playerColor"
              @board-created="onBoardCreated"
              @move="onPlayerMove"
          />
        </ClientOnly>

        <div v-if="gameStarted" class="flex justify-between items-center mt-6 text-gray-700">
          <p><strong>Tour :</strong> {{ turn }}</p>
          <p><strong>Dernier coup :</strong> {{ lastMove || '—' }}</p>
          <p><strong>Status :</strong> {{ status }}</p>
        </div>

        <div v-if="gameStarted" class="flex justify-center gap-4 mt-6">
          <button
              @click="resetGame"
              class="border border-gray-300 text-gray-800 px-6 py-2 rounded-full hover:bg-gray-100 transition"
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

const playerColor = ref<'white' | 'black'>('white')
const turn = ref<'white' | 'black'>('white')
const isPlayerTurn = ref(true)
const lastMove = ref('')
const status = ref('En attente')
const gameStarted = ref(false)

function onBoardCreated(api: any) {
  boardApi.value = api
  api.setPosition(game.fen())
}

function startGame() {
  resetGame()
  gameStarted.value = true
  if (playerColor.value === 'black') {
    isPlayerTurn.value = false
    iaPlay()
  }
}

async function onPlayerMove(move: { from: string; to: string }) {
  const played = game.move({ from: move.from, to: move.to, promotion: 'q' })
  if (!played) return
  lastMove.value = `${move.from}${move.to}`
  turn.value = game.turn() === 'w' ? 'white' : 'black'
  isPlayerTurn.value = false

  if (game.isGameOver()) return (status.value = 'Fin de partie')
  await iaPlay()
}

async function iaPlay() {
  const currentTurn = game.turn() === 'w' ? 'white' : 'black'
  if (currentTurn === playerColor.value) return

  const bestMove = await getBestMove(game.fen())

  if (bestMove === 'no_legal_moves') {
    status.value = 'Aucun coup légal'
    return
  }

  const move = game.move({
    from: bestMove.slice(0, 2),
    to: bestMove.slice(2, 4),
    promotion: 'q'
  })

  if (!move) {
    console.warn(`[IA] Coup invalide : ${bestMove}`)
    return
  }

  await boardApi.value?.move({
    from: move.from,
    to: move.to,
    promotion: move.promotion
  })

  lastMove.value = `${move.from}${move.to}`
  turn.value = game.turn() === 'w' ? 'white' : 'black'
  isPlayerTurn.value = turn.value === playerColor.value


  if (game.isGameOver()) {
    console.log('⛔ Fin de partie détectée')
    console.log('Checkmate:', game.isCheckmate())
    console.log('Stalemate:', game.isStalemate())
    console.log('Draw:', game.isDraw())
    console.log('Repetition:', game.isThreefoldRepetition())
    console.log('Matériel insuffisant:', game.isInsufficientMaterial())
    console.log('Timeout:', game.isTimeout && game.isTimeout())
    if (game.isCheckmate()) {
      status.value = `Échec et mat pour ${turn.value === 'white' ? 'noir' : 'blanc'}`
    } else if (game.isDraw()) {
      status.value = 'Match nul'
    } else if (game.isStalemate()) {
      status.value = 'Pat (aucun coup possible, mais pas de mat)'
    } else if (game.isThreefoldRepetition()) {
      status.value = 'Nulle par répétition de position'
    } else if (game.isInsufficientMaterial()) {
      status.value = 'Nulle (mat impossible à cause du matériel insuffisant)'
    } else if (game.isTimeout && game.isTimeout()) {
      status.value = 'Temps écoulé'
    } else {
      status.value = 'Fin de partie'
    }

    return
  }
}


function resetGame() {
  game.reset()
  boardApi.value?.setPosition(game.fen())
  turn.value = 'white'
  isPlayerTurn.value = true
  lastMove.value = ''
  status.value = 'En attente'
  gameStarted.value = false
}
</script>
