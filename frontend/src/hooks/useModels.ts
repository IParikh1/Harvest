import { useQuery } from '@tanstack/react-query'
import { harvestApi } from '@/api/endpoints'

export function useModels() {
  return useQuery({
    queryKey: ['models'],
    queryFn: harvestApi.getModels,
    staleTime: 60000,
  })
}
