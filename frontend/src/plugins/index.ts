import type { App } from 'vue'
import { VueQueryPlugin } from '@tanstack/vue-query'

export function setupPlugins(app: App) {
  app.use(VueQueryPlugin)
}