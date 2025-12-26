import { TaskResult } from '@/api/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface TaskResultDisplayProps {
  task: TaskResult
}

export function TaskResultDisplay({ task }: TaskResultDisplayProps) {
  if (task.error) {
    return (
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Error</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap text-sm text-destructive">{task.error}</pre>
        </CardContent>
      </Card>
    )
  }

  if (!task.result) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Result</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {task.result_json ? (
          <pre className="rounded-lg bg-muted p-4 overflow-x-auto text-sm">
            {JSON.stringify(task.result_json, null, 2)}
          </pre>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <pre className="whitespace-pre-wrap">{task.result}</pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
