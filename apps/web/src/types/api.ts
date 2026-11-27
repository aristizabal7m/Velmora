export type RiskLevel = 'bajo' | 'medio' | 'alto'
export type RiskProfile = 'conservador' | 'moderado' | 'agresivo'

export interface HealthResponse {
  status: string
  environment: string
  version: string
}

export interface Category {
  id: string
  name: string
  slug: string
  description: string | null
  published: boolean
}

export interface Investment {
  id: string
  name: string
  slug: string
  summary: string
  minimum_amount: string
  risk_level: RiskLevel
  horizon_months: number | null
  category_id: string | null
  published: boolean
  disclaimer: string
}

export interface Lesson {
  id: string
  title: string
  slug: string
  content: string
  published: boolean
}

export interface Recommendation {
  investment: Investment
  score: number
  reason: string
}

export interface CurrentUser {
  id: string
  role: string
  email: string | null
}

export interface InvestmentFilters {
  risk: RiskLevel | ''
  category: string
  minAmount: string
  maxAmount: string
}

export interface MyProfile {
  id: string
  display_name: string | null
  role: string
  risk_profile: RiskProfile | null
  completed_lessons: number
  total_lessons: number
  risk_lesson_id: string | null
  can_choose_risk_profile: boolean
}
