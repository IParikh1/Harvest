import { Menu, Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { HealthIndicator } from '@/components/health/HealthIndicator'
import { useSettingsStore } from '@/stores/settingsStore'

export function Header() {
  const { theme, setTheme, toggleSidebar } = useSettingsStore()

  const toggleTheme = () => {
    if (theme === 'dark') {
      setTheme('light')
    } else {
      setTheme('dark')
    }
  }

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center gap-4 px-4">
        <Button variant="ghost" size="icon" className="md:hidden" onClick={toggleSidebar}>
          <Menu className="h-5 w-5" />
        </Button>

        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">H</span>
          </div>
          <span className="font-semibold hidden sm:inline">Harvest</span>
        </div>

        <div className="flex-1" />

        <HealthIndicator />

        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
      </div>
    </header>
  )
}
