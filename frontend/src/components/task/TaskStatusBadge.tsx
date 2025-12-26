import { TaskStatus } from '@/api/types'
import { Badge } from '@/components/ui/badge'
import { Loader2 } from 'lucide-react'

interface TaskStatusBadgeProps {
  status: TaskStatus
}

export function TaskStatusBadge({ status }: TaskStatusBadgeProps) {
  const getVariant = () => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return 'success'
      case TaskStatus.FAILED:
        return 'destructive'
      case TaskStatus.PROCESSING:
        return 'warning'
      case TaskStatus.PENDING:
      default:
        return 'secondary'
    }
  }

  const isActive = status === TaskStatus.PENDING || status === TaskStatus.PROCESSING

  return (
    <Badge variant={getVariant()} className="capitalize">
      {isActive && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
      {status}
    </Badge>
  )
}
