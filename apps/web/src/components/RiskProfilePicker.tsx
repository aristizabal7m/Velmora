import { useState, type FormEvent } from 'react'
import { saveRiskProfile } from '../lib/api'
import { RISK_PROFILE_OPTIONS } from '../lib/riskProfiles'
import type { MyProfile, RiskProfile } from '../types/api'

interface Props {
  token: string
  current: RiskProfile | null
  onSaved: (profile: MyProfile) => void
}

export function RiskProfilePicker({ token, current, onSaved }: Props) {
  const [selected, setSelected] = useState<RiskProfile | null>(current)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selected) return
    setBusy(true)
    setError(null)
    setSaved(false)
    try {
      onSaved(await saveRiskProfile(selected, token))
      setSaved(true)
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'Error desconocido')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="risk-picker" onSubmit={(event) => void submit(event)}>
      <fieldset>
        <legend>¿Qué perfil de riesgo te describe mejor?</legend>
        {RISK_PROFILE_OPTIONS.map((option) => (
          <label key={option.value} className="risk-option">
            <input
              type="radio"
              name="risk_profile"
              value={option.value}
              checked={selected === option.value}
              onChange={() => setSelected(option.value)}
            />
            <span>
              <strong>{option.label}</strong>
              <small>{option.description}</small>
            </span>
          </label>
        ))}
      </fieldset>
      {error !== null && (
        <p className="status-error" role="alert">
          {error}
        </p>
      )}
      {saved && <p role="status">Perfil guardado. Tus sugerencias ya lo usan.</p>}
      <button type="submit" disabled={busy || !selected || selected === current}>
        {busy ? 'Guardando…' : 'Guardar perfil'}
      </button>
    </form>
  )
}
