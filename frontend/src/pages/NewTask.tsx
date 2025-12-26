import { TaskSubmitForm } from '@/components/task/TaskSubmitForm'

export function NewTask() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">New Analysis Task</h1>
        <p className="text-muted-foreground">
          Submit data for AI-powered analysis
        </p>
      </div>

      <TaskSubmitForm />
    </div>
  )
}
