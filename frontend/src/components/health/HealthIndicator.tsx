import { useHealth } from '@/hooks/useHealth'
import { cn } from '@/lib/utils'

export function HealthIndicator() {
  const { data: health, isError, isLoading } = useHealth()

  const getStatusColor = () => {
    if (isLoading) return 'bg-gray-400'
    if (isError) return 'bg-red-500'
    switch (health?.status) {
      case 'healthy':
        return 'bg-green-500'
      case 'degraded':
        return 'bg-yellow-500'
      case 'unhealthy':
        return 'bg-red-500'
      default:
        return 'bg-gray-400'
    }
  }

  const getStatusText = () => {
    if (isLoading) return 'Checking...'
    if (isError) return 'Disconnected'
    return health?.status || 'Unknown'
  }

  return (
    <div className="flex items-center gap-2">
      <div className={cn('w-2.5 h-2.5 rounded-full', getStatusColor())} />
      <span className="text-sm text-muted-foreground capitalize">{getStatusText()}</span>
      {health && <span className="text-xs text-muted-foreground">v{health.version}</span>}
    </div>
  )
}
