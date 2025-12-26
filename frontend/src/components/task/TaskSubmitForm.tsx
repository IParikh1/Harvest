import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSubmitTask } from '@/hooks/useTasks'
import { useModels } from '@/hooks/useModels'
import { useSettingsStore } from '@/stores/settingsStore'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { MAX_SOURCE_LENGTH, MAX_QUERY_LENGTH, MIN_TIMEOUT, MAX_TIMEOUT } from '@/lib/constants'
import { OutputFormat } from '@/api/types'
import { Loader2, ChevronDown, ChevronUp } from 'lucide-react'

export function TaskSubmitForm() {
  const navigate = useNavigate()
  const submitTask = useSubmitTask()
  const { data: modelsData } = useModels()
  const { defaultModel, defaultTimeout, defaultOutputFormat } = useSettingsStore()

  const [showAdvanced, setShowAdvanced] = useState(false)
  const [formData, setFormData] = useState({
    source: '',
    query: '',
    model: defaultModel || '',
    timeout: defaultTimeout,
    output_format: defaultOutputFormat as 'text' | 'json',
    callback_url: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.source.trim()) {
      newErrors.source = 'Source is required'
    } else if (formData.source.length > MAX_SOURCE_LENGTH) {
      newErrors.source = `Source must be less than ${MAX_SOURCE_LENGTH.toLocaleString()} characters`
    }

    if (!formData.query.trim()) {
      newErrors.query = 'Query is required'
    } else if (formData.query.length > MAX_QUERY_LENGTH) {
      newErrors.query = `Query must be less than ${MAX_QUERY_LENGTH} characters`
    }

    if (formData.callback_url && !formData.callback_url.startsWith('http')) {
      newErrors.callback_url = 'Must be a valid URL'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) return

    try {
      const request = {
        source: formData.source,
        query: formData.query,
        ...(formData.model && { model: formData.model }),
        timeout: formData.timeout,
        output_format: formData.output_format as OutputFormat,
        ...(formData.callback_url && { callback_url: formData.callback_url }),
      }

      const result = await submitTask.mutateAsync(request)
      navigate(`/task/${result.task_id}`)
    } catch (error) {
      console.error('Failed to submit task:', error)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit Analysis Task</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Data Source</label>
            <Textarea
              value={formData.source}
              onChange={(e) => setFormData({ ...formData, source: e.target.value })}
              placeholder="Paste your data here (e.g., financial reports, logs, documents)..."
              rows={8}
              className="font-mono text-sm"
            />
            {errors.source && <p className="text-destructive text-sm mt-1">{errors.source}</p>}
            <p className="text-xs text-muted-foreground mt-1">
              {formData.source.length.toLocaleString()} / {MAX_SOURCE_LENGTH.toLocaleString()}{' '}
              characters
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Query</label>
            <Input
              value={formData.query}
              onChange={(e) => setFormData({ ...formData, query: e.target.value })}
              placeholder="What would you like to analyze? (e.g., 'Summarize the key trends')"
            />
            {errors.query && <p className="text-destructive text-sm mt-1">{errors.query}</p>}
          </div>

          <div>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
            >
              {showAdvanced ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              Advanced Options
            </button>

            {showAdvanced && (
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium mb-2">Model</label>
                  <Select
                    value={formData.model}
                    onValueChange={(value) => setFormData({ ...formData, model: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Default model" />
                    </SelectTrigger>
                    <SelectContent>
                      {modelsData?.models.map((model) => (
                        <SelectItem key={model.name} value={model.name}>
                          {model.name} {model.size && `(${model.size})`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Timeout: {formData.timeout}s
                  </label>
                  <input
                    type="range"
                    min={MIN_TIMEOUT}
                    max={MAX_TIMEOUT}
                    value={formData.timeout}
                    onChange={(e) =>
                      setFormData({ ...formData, timeout: parseInt(e.target.value) })
                    }
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Output Format</label>
                  <Select
                    value={formData.output_format}
                    onValueChange={(value: 'text' | 'json') =>
                      setFormData({ ...formData, output_format: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">Text</SelectItem>
                      <SelectItem value="json">JSON</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Callback URL (optional)</label>
                  <Input
                    type="url"
                    value={formData.callback_url}
                    onChange={(e) => setFormData({ ...formData, callback_url: e.target.value })}
                    placeholder="https://your-webhook.com/callback"
                  />
                  {errors.callback_url && (
                    <p className="text-destructive text-sm mt-1">{errors.callback_url}</p>
                  )}
                </div>
              </div>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={submitTask.isPending}>
            {submitTask.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {submitTask.isPending ? 'Submitting...' : 'Submit Analysis'}
          </Button>

          {submitTask.isError && (
            <p className="text-destructive text-sm text-center">
              Error: {(submitTask.error as Error).message}
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  )
}
