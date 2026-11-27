import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { RiskProfilePicker } from '../components/RiskProfilePicker'
import { useAuth } from '../hooks/useAuth'
import { useMyProfile } from '../hooks/useMyProfile'
import { completeLesson, getLessonProgress, getLessons } from '../lib/api'
import type { Lesson } from '../types/api'

export function LessonsPage() {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [completed, setCompleted] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const { token, user } = useAuth()
  const { profile, setProfile, reload } = useMyProfile(token)

  useEffect(() => {
    getLessons()
      .then(setLessons)
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : 'Error desconocido')
      })
  }, [])

  useEffect(() => {
    if (!token) return
    let active = true
    getLessonProgress(token)
      .then((ids) => {
        if (active) setCompleted(ids)
      })
      .catch(() => {
        // Sin progreso previo visible; las acciones nuevas siguen funcionando.
      })
    return () => {
      active = false
    }
  }, [token])

  async function markComplete(id: string) {
    if (!token) return
    try {
      await completeLesson(id, token)
      setCompleted((previous) => (previous.includes(id) ? previous : [...previous, id]))
      setError(null)
      reload()
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'Error desconocido')
    }
  }

  const completedIds = token ? completed : []
  const riskLessonId = profile?.risk_lesson_id ?? null

  return (
    <main className="main-content">
      <h1>Lecciones</h1>
      {!user && <p>Ingresa para registrar tu progreso y definir tu perfil de riesgo.</p>}
      {profile && (
        <p className="progress-note">
          Has completado {profile.completed_lessons} de {profile.total_lessons} lecciones.
        </p>
      )}
      {error !== null && (
        <p className="status-error" role="alert">
          {error}
        </p>
      )}
      <div className="card-grid">
        {lessons.map((lesson) => {
          const isDone = completedIds.includes(lesson.id)
          const isRiskLesson = lesson.id === riskLessonId
          return (
            <article key={lesson.id} className="investment-card">
              <h2>{lesson.title}</h2>
              <p>{lesson.content}</p>
              {isRiskLesson && !isDone && user && (
                <p className="disclaimer">
                  Al completarla podrás definir tu perfil de riesgo.
                </p>
              )}
              {user && (
                <button
                  type="button"
                  disabled={isDone}
                  onClick={() => void markComplete(lesson.id)}
                >
                  {isDone ? 'Completada' : 'Marcar completada'}
                </button>
              )}
              {isRiskLesson && isDone && token && profile?.can_choose_risk_profile && (
                <>
                  <RiskProfilePicker
                    token={token}
                    current={profile.risk_profile}
                    onSaved={setProfile}
                  />
                  {profile.risk_profile && (
                    <p>
                      <Link to="/">Ver sugerencias para tu perfil</Link>
                    </p>
                  )}
                </>
              )}
            </article>
          )
        })}
      </div>
    </main>
  )
}
