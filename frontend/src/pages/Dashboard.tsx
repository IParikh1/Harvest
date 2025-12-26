import { Link } from 'react-router-dom'
import { useTaskList } from '@/hooks/useTasks'
import { StatsCards } from '@/components/analytics/StatsCards'
import { TaskStatusChart } from '@/components/analytics/TaskStatusChart'
import { TaskList } from '@/components/task/TaskList'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus } from 'lucide-react'

export function Dashboard() {
  const { data: tasksData, isLoading } = useTaskList(5)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your data analysis tasks</p>
        </div>
        <Link to="/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Task
          </Button>
        </Link>
      </div>

      <StatsCards />

      <div className="grid gap-6 lg:grid-cols-2">
        <TaskStatusChart />

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Tasks</CardTitle>
            <Link to="/history" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : (
              <TaskList tasks={tasksData?.tasks || []} />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
