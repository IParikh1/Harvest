import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { harvestApi } from '@/api/endpoints'
import { TaskStatus, type HarvestRequest } from '@/api/types'
import { POLLING_INTERVAL } from '@/lib/constants'

export function useTask(taskId: string | undefined) {
  return useQuery({
    queryKey: ['task', taskId],
    queryFn: () => harvestApi.getTask(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return POLLING_INTERVAL
      if (data.status === TaskStatus.PENDING || data.status === TaskStatus.PROCESSING) {
        return POLLING_INTERVAL
      }
      return false
    },
    staleTime: 1000,
  })
}

export function useTaskList(limit: number = 20) {
  return useQuery({
    queryKey: ['tasks', limit],
    queryFn: () => harvestApi.listTasks(limit),
    refetchInterval: 10000,
    staleTime: 5000,
  })
}

export function useSubmitTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (request: HarvestRequest) => harvestApi.submitTask(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

export function useTaskAnalytics() {
  const { data: tasksData } = useTaskList(100)

  if (!tasksData) {
    return {
      totalTasks: 0,
      completedTasks: 0,
      failedTasks: 0,
      pendingTasks: 0,
      successRate: 0,
      avgProcessingTime: 0,
    }
  }

  const tasks = tasksData.tasks
  const completed = tasks.filter((t) => t.status === TaskStatus.COMPLETED)
  const failed = tasks.filter((t) => t.status === TaskStatus.FAILED)
  const pending = tasks.filter(
    (t) => t.status === TaskStatus.PENDING || t.status === TaskStatus.PROCESSING
  )

  const finishedTasks = [...completed, ...failed]
  const successRate = finishedTasks.length > 0 ? (completed.length / finishedTasks.length) * 100 : 0

  const processingTimes = completed
    .map((t) => t.processing_time_ms)
    .filter((t): t is number => t !== undefined && t !== null)

  const avgProcessingTime =
    processingTimes.length > 0
      ? processingTimes.reduce((a, b) => a + b, 0) / processingTimes.length
      : 0

  return {
    totalTasks: tasks.length,
    completedTasks: completed.length,
    failedTasks: failed.length,
    pendingTasks: pending.length,
    successRate: Math.round(successRate * 10) / 10,
    avgProcessingTime: Math.round(avgProcessingTime),
  }
}
