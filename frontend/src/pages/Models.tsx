import { useModels } from '@/hooks/useModels'
import { useSettingsStore } from '@/stores/settingsStore'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Cpu, Check, RefreshCw } from 'lucide-react'

export function Models() {
  const { data: modelsData, isLoading, refetch } = useModels()
  const { defaultModel, setDefaultModel } = useSettingsStore()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Models</h1>
          <p className="text-muted-foreground">
            Available LLM models from Ollama ({modelsData?.count || 0} models)
          </p>
        </div>
        <Button variant="outline" onClick={() => refetch()}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {modelsData?.models.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Cpu className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-semibold">No models available</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Make sure Ollama is running and has models installed.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {modelsData?.models.map((model) => {
            const isDefault = model.name === (defaultModel || modelsData.default_model)

            return (
              <Card key={model.name} className={isDefault ? 'ring-2 ring-primary' : ''}>
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base">{model.name}</CardTitle>
                    {isDefault && <Badge variant="default">Default</Badge>}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                    {model.size && (
                      <span className="bg-muted px-2 py-1 rounded">{model.size}</span>
                    )}
                    {model.digest && (
                      <span className="bg-muted px-2 py-1 rounded font-mono">
                        {model.digest}
                      </span>
                    )}
                  </div>
                  {!isDefault && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => setDefaultModel(model.name)}
                    >
                      <Check className="h-4 w-4 mr-2" />
                      Set as Default
                    </Button>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
