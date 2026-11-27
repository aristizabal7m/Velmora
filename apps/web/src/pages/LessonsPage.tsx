import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { completeLesson, getLessonProgress, getLessons } from '../lib/api'
import type { Lesson } from '../types/api'

export function LessonsPage() {
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [completed, setCompleted] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const { token, user } = useAuth()

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
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'Error desconocido')
    }
  }

  const completedIds = token ? completed : []

  return (
    <main className="main-content">
      <h1>Lecciones</h1>
      {!user && <p>Ingresa para registrar tu progreso.</p>}
      {error !== null && (
        <p className="status-error" role="alert">
          {error}
        </p>
      )}
      <div className="card-grid">
        {lessons.map((lesson) => (
          <article key={lesson.id} className="investment-card">
            <h2>{lesson.title}</h2>
            <p>{lesson.content}</p>
            {user && (
              <button
                type="button"
                disabled={completedIds.includes(lesson.id)}
                onClick={() => void markComplete(lesson.id)}
              >
                {completedIds.includes(lesson.id) ? 'Completada' : 'Marcar completada'}
              </button>
            )}
          </article>
        ))}
      </div>
    </main>
  )
}
