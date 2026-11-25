import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { getMe } from '../lib/api'
import type { CurrentUser } from '../types/api'

export function ProfilePage() {
  const { user, token } = useAuth()
  const [profile, setProfile] = useState<CurrentUser | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    getMe(token)
      .then(setProfile)
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : 'Error desconocido')
      })
  }, [token])

  if (!user) {
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
          <dt>Rol en la API</dt>
          <dd>{profile?.role ?? 'Cargando…'}</dd>
        </div>
      </dl>
      {error !== null && (
        <p className="status-error" role="alert">
          {error}
        </p>
      )}
    </main>
  )
}
