import type {
  Category,
  CurrentUser,
  HealthResponse,
  Investment,
  InvestmentFilters,
  Lesson,
  Recommendation,
  RiskProfile,
} from '../types/api'

const API_URL = (
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
).replace(/\/$/, '')

function authInit(token: string | null, init?: RequestInit): RequestInit {
  if (!token) return init ?? {}
  return {
    ...init,
    headers: { ...init?.headers, Authorization: `Bearer ${token}` },
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init)
  if (!response.ok) {
    throw new Error(`La API respondió ${response.status}`)
  }
  return (await response.json()) as T
}

export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health', { signal })
}

export function getCategories(): Promise<Category[]> {
  return apiFetch<Category[]>('/api/v1/categories')
}

export function getLessons(): Promise<Lesson[]> {
  return apiFetch<Lesson[]>('/api/v1/lessons')
}

export function getInvestments(
  filters: InvestmentFilters,
  token: string | null = null,
): Promise<Investment[]> {
  const params = new URLSearchParams()
  if (filters.risk) params.set('risk', filters.risk)
  if (filters.category) params.set('category', filters.category)
  if (filters.minAmount) params.set('min_amount', filters.minAmount)
  if (filters.maxAmount) params.set('max_amount', filters.maxAmount)
  const query = params.size > 0 ? `?${params.toString()}` : ''
  return apiFetch<Investment[]>(`/api/v1/investments${query}`, authInit(token))
}

export function getRecommendations(
  profile: RiskProfile,
  token: string | null = null,
): Promise<Recommendation[]> {
  return apiFetch<Recommendation[]>(
    `/api/v1/investments/recommendations?profile=${profile}`,
    authInit(token),
  )
}

export function getMe(token: string): Promise<CurrentUser> {
  return apiFetch<CurrentUser>('/api/v1/auth/me', authInit(token))
}

export function completeLesson(id: string, token: string): Promise<void> {
  return apiFetch<void>(`/api/v1/lessons/${id}/complete`, authInit(token, { method: 'POST' }))
}
