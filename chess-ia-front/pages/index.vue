<template>
  <main class="min-h-screen bg-gray-50 py-24 px-6 flex flex-col items-center text-center">
    <h1 class="text-4xl sm:text-5xl font-bold text-gray-800 mb-4">
      Bienvenue sur Chess-IA
    </h1>
    <p class="text-gray-600 text-lg mb-10 max-w-xl">
      Une plateforme d'entraînement et d'exploration des échecs propulsée par l'intelligence artificielle.
    </p>

    <div class="flex flex-col sm:flex-row gap-6">
      <NuxtLink
          to="/chess-ia-vs-ia"
          class="bg-black text-white px-6 py-3 rounded-full text-sm hover:bg-gray-800 transition"
      >
        🎯 IA vs IA
      </NuxtLink>
      <NuxtLink
          to="/chess-player-vs-ia"
          class="border border-black text-black px-6 py-3 rounded-full text-sm hover:bg-gray-100 transition"
      >
        🧠 Joueur vs IA
      </NuxtLink>
    </div>
  </main>
</template>
