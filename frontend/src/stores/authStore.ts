import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  apiKey: string | null
  authEnabled: boolean | null
  setApiKey: (key: string | null) => void
  setAuthEnabled: (enabled: boolean) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      apiKey: null,
      authEnabled: null,
      setApiKey: (key) => {
        if (key) {
          localStorage.setItem('harvest-api-key', key)
        } else {
          localStorage.removeItem('harvest-api-key')
        }
        set({ apiKey: key })
      },
      setAuthEnabled: (enabled) => set({ authEnabled: enabled }),
      clearAuth: () => {
        localStorage.removeItem('harvest-api-key')
        set({ apiKey: null })
      },
    }),
    {
      name: 'harvest-auth',
      partialize: (state) => ({ apiKey: state.apiKey }),
    }
  )
)
