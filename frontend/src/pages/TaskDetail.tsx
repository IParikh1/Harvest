import { useParams, Link } from 'react-router-dom'
import { useTask } from '@/hooks/useTasks'
import { TaskStatusBadge } from '@/components/task/TaskStatusBadge'
import { TaskResultDisplay } from '@/components/task/TaskResultDisplay'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatDate, formatDuration } from '@/lib/utils'
import { ArrowLeft, Clock, Cpu, FileText, RefreshCw } from 'lucide-react'
import { TaskStatus } from '@/api/types'

export function TaskDetail() {
  const { taskId } = useParams<{ taskId: string }>()
  const { data: task, isLoading, refetch } = useTask(taskId)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!task) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold">Task not found</h2>
        <p className="text-muted-foreground mt-2">The task you're looking for doesn't exist.</p>
        <Link to="/history">
          <Button className="mt-4">Back to History</Button>
        </Link>
      </div>
    )
  }

  const isActive = task.status === TaskStatus.PENDING || task.status === TaskStatus.PROCESSING

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/history">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold">Task Details</h1>
            <TaskStatusBadge status={task.status} />
          </div>
          <p className="text-sm text-muted-foreground font-mono">{task.task_id}</p>
        </div>
        {isActive && (
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              Created
            </div>
            <p className="mt-1 font-medium">{formatDate(task.created_at)}</p>
          </CardContent>
        </Card>
        {task.completed_at && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                Completed
              </div>
              <p className="mt-1 font-medium">{formatDate(task.completed_at)}</p>
            </CardContent>
          </Card>
        )}
        {task.processing_time_ms && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="h-4 w-4" />
                Processing Time
              </div>
              <p className="mt-1 font-medium">{formatDuration(task.processing_time_ms)}</p>
            </CardContent>
          </Card>
        )}
        {task.model && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Cpu className="h-4 w-4" />
                Model
              </div>
              <p className="mt-1 font-medium">{task.model}</p>
            </CardContent>
          </Card>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Query</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm">{task.query}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Source Data</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-sm whitespace-pre-wrap bg-muted p-4 rounded-lg overflow-x-auto max-h-64 overflow-y-auto">
            {task.source}
          </pre>
        </CardContent>
      </Card>

      <TaskResultDisplay task={task} />
    </div>
  )
}
