import { useCallback, useEffect, useState } from 'react'
import { getMyProfile } from '../lib/api'
import type { MyProfile } from '../types/api'

/** Perfil propio con progreso; `reload` lo vuelve a pedir tras una acción. */
export function useMyProfile(token: string | null) {
  const [profile, setProfile] = useState<MyProfile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [version, setVersion] = useState(0)

  useEffect(() => {
    if (!token) return
    let active = true
    getMyProfile(token)
      .then((data) => {
        if (!active) return
        setProfile(data)
        setError(null)
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : 'Error desconocido')
      })
    return () => {
      active = false
    }
  }, [token, version])

  const reload = useCallback(() => setVersion((value) => value + 1), [])

  return {
    profile: token ? profile : null,
    error: token ? error : null,
    setProfile,
    reload,
  }
}
