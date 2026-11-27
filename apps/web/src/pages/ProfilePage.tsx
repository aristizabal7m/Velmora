import { Link } from 'react-router-dom'
import { RiskProfilePicker } from '../components/RiskProfilePicker'
import { useAuth } from '../hooks/useAuth'
import { useMyProfile } from '../hooks/useMyProfile'
import { riskProfileLabel } from '../lib/riskProfiles'

export function ProfilePage() {
  const { user, token } = useAuth()
  const { profile, error, setProfile } = useMyProfile(token)

  if (!user || !token) {
    return (
      <main className="main-content">
        <h1>Perfil</h1>
        <p>
          Necesitas <Link to="/ingresar">ingresar</Link> para ver tu perfil.
        </p>
      </main>
    )
  }

  return (
    <main className="main-content">
      <h1>Perfil</h1>
      <dl className="profile-details">
        <div>
          <dt>Correo</dt>
          <dd>{user.email ?? 'No disponible'}</dd>
        </div>
        <div>
          <dt>Rol</dt>
          <dd>{profile?.role ?? 'Cargando…'}</dd>
        </div>
        <div>
          <dt>Lecciones</dt>
          <dd>
            {profile
              ? `${profile.completed_lessons} de ${profile.total_lessons} completadas`
              : 'Cargando…'}
          </dd>
        </div>
        <div>
          <dt>Perfil de riesgo</dt>
          <dd>{profile ? riskProfileLabel(profile.risk_profile) : 'Cargando…'}</dd>
        </div>
      </dl>

      {profile && !profile.can_choose_risk_profile && (
        <p>
          Completa la lección <Link to="/lecciones">«Riesgo y rentabilidad»</Link> para
          definir tu perfil de riesgo.
        </p>
      )}
      {profile?.can_choose_risk_profile && (
        <RiskProfilePicker
          token={token}
          current={profile.risk_profile}
          onSaved={setProfile}
        />
      )}

      {error !== null && (
        <p className="status-error" role="alert">
          {error}
        </p>
      )}
    </main>
  )
}
