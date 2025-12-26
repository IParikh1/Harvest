import { useQuery } from '@tanstack/react-query'
import { harvestApi } from '@/api/endpoints'
import { HEALTH_CHECK_INTERVAL } from '@/lib/constants'

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: harvestApi.getHealth,
    refetchInterval: HEALTH_CHECK_INTERVAL,
    staleTime: HEALTH_CHECK_INTERVAL / 2,
  })
}

export function useAuthStatus() {
  return useQuery({
    queryKey: ['authStatus'],
    queryFn: harvestApi.getAuthStatus,
    staleTime: 60000,
  })
}
