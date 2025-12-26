import { useSettingsStore } from '@/stores/settingsStore'
import { useHealth, useAuthStatus } from '@/hooks/useHealth'
import { ApiKeyInput } from '@/components/settings/ApiKeyInput'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, Moon, Sun, Monitor } from 'lucide-react'

export function Settings() {
  const { theme, setTheme, defaultTimeout, setDefaultTimeout, defaultOutputFormat, setDefaultOutputFormat } =
    useSettingsStore()
  const { data: health } = useHealth()
  const { data: authStatus } = useAuthStatus()

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Configure your Harvest dashboard</p>
      </div>

      <ApiKeyInput />

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize the look of your dashboard</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Theme</label>
            <Select value={theme} onValueChange={(v: 'light' | 'dark' | 'system') => setTheme(v)}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">
                  <div className="flex items-center gap-2">
                    <Sun className="h-4 w-4" />
                    Light
                  </div>
                </SelectItem>
                <SelectItem value="dark">
                  <div className="flex items-center gap-2">
                    <Moon className="h-4 w-4" />
                    Dark
                  </div>
                </SelectItem>
                <SelectItem value="system">
                  <div className="flex items-center gap-2">
                    <Monitor className="h-4 w-4" />
                    System
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Default Values</CardTitle>
          <CardDescription>Set default values for new tasks</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Default Timeout: {defaultTimeout}s
            </label>
            <input
              type="range"
              min="10"
              max="300"
              value={defaultTimeout}
              onChange={(e) => setDefaultTimeout(parseInt(e.target.value))}
              className="w-full max-w-xs"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Default Output Format</label>
            <Select
              value={defaultOutputFormat}
              onValueChange={(v: 'text' | 'json') => setDefaultOutputFormat(v)}
            >
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="text">Text</SelectItem>
                <SelectItem value="json">JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Connection Status</CardTitle>
          <CardDescription>Backend service status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">API Server</span>
              <Badge variant={health ? 'success' : 'destructive'}>
                {health ? (
                  <>
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Connected (v{health.version})
                  </>
                ) : (
                  <>
                    <XCircle className="h-3 w-3 mr-1" />
                    Disconnected
                  </>
                )}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Ollama</span>
              <Badge variant={health?.ollama_available ? 'success' : 'destructive'}>
                {health?.ollama_available ? (
                  <>
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Available
                  </>
                ) : (
                  <>
                    <XCircle className="h-3 w-3 mr-1" />
                    Unavailable
                  </>
                )}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Redis</span>
              <Badge variant={health?.redis_available ? 'success' : 'secondary'}>
                {health?.redis_available ? (
                  <>
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Connected
                  </>
                ) : (
                  'Using Memory Store'
                )}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Authentication</span>
              <Badge variant={authStatus?.auth_enabled ? 'default' : 'secondary'}>
                {authStatus?.auth_enabled ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
