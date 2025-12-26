import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useTaskAnalytics } from '@/hooks/useTasks'
import { CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react'
import { formatDuration } from '@/lib/utils'

export function StatsCards() {
  const stats = useTaskAnalytics()

  const cards = [
    {
      title: 'Total Tasks',
      value: stats.totalTasks,
      icon: TrendingUp,
      color: 'text-primary',
    },
    {
      title: 'Completed',
      value: stats.completedTasks,
      icon: CheckCircle,
      color: 'text-green-500',
    },
    {
      title: 'Failed',
      value: stats.failedTasks,
      icon: XCircle,
      color: 'text-red-500',
    },
    {
      title: 'Success Rate',
      value: `${stats.successRate}%`,
      icon: TrendingUp,
      color: 'text-blue-500',
    },
    {
      title: 'Avg. Processing',
      value: formatDuration(stats.avgProcessingTime),
      icon: Clock,
      color: 'text-yellow-500',
    },
    {
      title: 'Active',
      value: stats.pendingTasks,
      icon: Clock,
      color: 'text-orange-500',
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <card.icon className={`h-4 w-4 ${card.color}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
