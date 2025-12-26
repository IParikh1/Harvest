import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useAuthStatus } from '@/hooks/useHealth'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Eye, EyeOff, Check, X } from 'lucide-react'

export function ApiKeyInput() {
  const { apiKey, setApiKey } = useAuthStore()
  const { data: authStatus } = useAuthStatus()
  const [showKey, setShowKey] = useState(false)
  const [inputValue, setInputValue] = useState(apiKey || '')

  const handleSave = () => {
    setApiKey(inputValue || null)
  }

  const handleClear = () => {
    setInputValue('')
    setApiKey(null)
  }

  if (!authStatus?.auth_enabled) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>API Authentication</CardTitle>
          <CardDescription>Authentication is currently disabled</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            The API is running without authentication. All requests are allowed.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Key</CardTitle>
        <CardDescription>Enter your API key to authenticate requests</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Input
              type={showKey ? 'text' : 'password'}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Enter your API key"
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleSave} disabled={inputValue === apiKey}>
            <Check className="h-4 w-4 mr-2" />
            Save
          </Button>
          <Button variant="outline" onClick={handleClear} disabled={!apiKey}>
            <X className="h-4 w-4 mr-2" />
            Clear
          </Button>
        </div>
        {apiKey && (
          <p className="text-sm text-green-600 dark:text-green-400">
            API key configured
          </p>
        )}
      </CardContent>
    </Card>
  )
}
