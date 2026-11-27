import type { RiskProfile } from '../types/api'

export const RISK_PROFILE_OPTIONS: {
  value: RiskProfile
  label: string
  description: string
}[] = [
  {
    value: 'conservador',
    label: 'Conservador',
    description: 'Prefiero no perder dinero, aunque la rentabilidad sea menor.',
  },
  {
    value: 'moderado',
    label: 'Moderado',
    description: 'Acepto algo de variación a cambio de más rentabilidad esperada.',
  },
  {
    value: 'agresivo',
    label: 'Agresivo',
    description: 'Tolero caídas fuertes buscando más rentabilidad a largo plazo.',
  },
]

export function riskProfileLabel(value: RiskProfile | null): string {
  return RISK_PROFILE_OPTIONS.find((option) => option.value === value)?.label ?? 'Sin definir'
}
