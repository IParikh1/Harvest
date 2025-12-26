import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark' | 'system'
type OutputFormat = 'text' | 'json'

interface SettingsState {
  theme: Theme
  defaultModel: string | null
  defaultTimeout: number
  defaultOutputFormat: OutputFormat
  sidebarCollapsed: boolean
  setTheme: (theme: Theme) => void
  setDefaultModel: (model: string | null) => void
  setDefaultTimeout: (timeout: number) => void
  setDefaultOutputFormat: (format: OutputFormat) => void
  toggleSidebar: () => void
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'system',
      defaultModel: null,
      defaultTimeout: 60,
      defaultOutputFormat: 'text',
      sidebarCollapsed: false,
      setTheme: (theme) => set({ theme }),
      setDefaultModel: (model) => set({ defaultModel: model }),
      setDefaultTimeout: (timeout) => set({ defaultTimeout: timeout }),
      setDefaultOutputFormat: (format) => set({ defaultOutputFormat: format }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    { name: 'harvest-settings' }
  )
)
