import { Link } from 'react-router-dom'
import { TaskResult } from '@/api/types'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { TaskStatusBadge } from './TaskStatusBadge'
import { formatDate, formatDuration, truncate } from '@/lib/utils'
import { Clock, FileText } from 'lucide-react'

interface TaskCardProps {
  task: TaskResult
}

export function TaskCard({ task }: TaskCardProps) {
  return (
    <Link to={`/task/${task.task_id}`}>
      <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{truncate(task.query || '', 60)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {task.task_id.slice(0, 8)}...
              </p>
            </div>
            <TaskStatusBadge status={task.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDate(task.created_at)}
            </div>
            {task.processing_time_ms && (
              <div className="flex items-center gap-1">
                <FileText className="h-3 w-3" />
                {formatDuration(task.processing_time_ms)}
              </div>
            )}
            {task.model && (
              <div className="text-xs bg-muted px-1.5 py-0.5 rounded">{task.model}</div>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
