<template>
  <div id="app" class="min-h-screen bg-[#fafbfe]">
    <main
      id="main-content"
      class="container flex flex-col gap-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8"
      role="main"
      aria-label="Task management application"
    >
      <slot />
    </main>
  </div>
</template>
