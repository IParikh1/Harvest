export enum TaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum OutputFormat {
  TEXT = 'text',
  JSON = 'json',
}

export interface HarvestRequest {
  source: string
  query: string
  model?: string
  timeout?: number
  output_format?: OutputFormat
  callback_url?: string
}

export interface BatchHarvestRequest {
  requests: HarvestRequest[]
}

export interface HarvestResponse {
  task_id: string
  status: TaskStatus
  message: string
}

export interface BatchHarvestResponse {
  task_ids: string[]
  count: number
  message: string
}

export interface TaskResult {
  task_id: string
  status: TaskStatus
  source?: string
  query?: string
  model?: string
  result?: string
  result_json?: Record<string, unknown>
  error?: string
  created_at?: string
  completed_at?: string
  processing_time_ms?: number
}

export interface TasksListResponse {
  tasks: TaskResult[]
  count: number
}

export interface ModelInfo {
  name: string
  size?: string
  modified_at?: string
  digest?: string
}

export interface ModelsResponse {
  models: ModelInfo[]
  default_model: string
  count: number
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  version: string
  ollama_available: boolean
  redis_available: boolean
}

export interface AuthStatusResponse {
  auth_enabled: boolean
  message: string
}
