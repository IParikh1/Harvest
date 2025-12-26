import { useModels } from '@/hooks/useModels'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface ModelSelectorProps {
  value: string
  onChange: (value: string) => void
}

export function ModelSelector({ value, onChange }: ModelSelectorProps) {
  const { data: modelsData, isLoading } = useModels()

  if (isLoading) {
    return (
      <Select disabled>
        <SelectTrigger>
          <SelectValue placeholder="Loading models..." />
        </SelectTrigger>
      </Select>
    )
  }

  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger>
        <SelectValue placeholder={modelsData?.default_model || 'Select model'} />
      </SelectTrigger>
      <SelectContent>
        {modelsData?.models.map((model) => (
          <SelectItem key={model.name} value={model.name}>
            {model.name} {model.size && `(${model.size})`}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
