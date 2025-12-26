import { useState } from 'react'
import { useTaskList } from '@/hooks/useTasks'
import { TaskList } from '@/components/task/TaskList'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { TaskStatus } from '@/api/types'
import { Search } from 'lucide-react'

export function TaskHistory() {
  const { data: tasksData, isLoading } = useTaskList(100)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const filteredTasks = tasksData?.tasks.filter((task) => {
    const matchesSearch =
      !search ||
      task.query?.toLowerCase().includes(search.toLowerCase()) ||
      task.task_id.includes(search)

    const matchesStatus = statusFilter === 'all' || task.status === statusFilter

    return matchesSearch && matchesStatus
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Task History</h1>
        <p className="text-muted-foreground">View and manage your analysis tasks</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by query or task ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value={TaskStatus.PENDING}>Pending</SelectItem>
            <SelectItem value={TaskStatus.PROCESSING}>Processing</SelectItem>
            <SelectItem value={TaskStatus.COMPLETED}>Completed</SelectItem>
            <SelectItem value={TaskStatus.FAILED}>Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">Loading tasks...</div>
      ) : (
        <>
          <p className="text-sm text-muted-foreground">
            Showing {filteredTasks?.length || 0} of {tasksData?.count || 0} tasks
          </p>
          <TaskList tasks={filteredTasks || []} />
        </>
      )}
    </div>
  )
}
