import { apiClient } from './client'
import type {
  HarvestRequest,
  HarvestResponse,
  BatchHarvestRequest,
  BatchHarvestResponse,
  TaskResult,
  TasksListResponse,
  ModelsResponse,
  HealthResponse,
  AuthStatusResponse,
} from './types'

export const harvestApi = {
  submitTask: async (request: HarvestRequest): Promise<HarvestResponse> => {
    const { data } = await apiClient.post('/harvest', request)
    return data
  },

  submitBatch: async (request: BatchHarvestRequest): Promise<BatchHarvestResponse> => {
    const { data } = await apiClient.post('/harvest/batch', request)
    return data
  },

  getTask: async (taskId: string): Promise<TaskResult> => {
    const { data } = await apiClient.get(`/harvest/${taskId}`)
    return data
  },

  listTasks: async (limit: number = 20): Promise<TasksListResponse> => {
    const { data } = await apiClient.get('/tasks', { params: { limit } })
    return data
  },

  getModels: async (): Promise<ModelsResponse> => {
    const { data } = await apiClient.get('/models')
    return data
  },

  getHealth: async (): Promise<HealthResponse> => {
    const { data } = await apiClient.get('/health')
    return data
  },

  getAuthStatus: async (): Promise<AuthStatusResponse> => {
    const { data } = await apiClient.get('/auth/status')
    return data
  },
}
