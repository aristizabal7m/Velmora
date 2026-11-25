import { useEffect, useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { completeLesson, getLessons } from '../lib/api'
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

  async function markComplete(id: string) {
    if (!token) return
    try {
      await completeLesson(id, token)
      setCompleted((previous) => [...previous, id])
      setError(null)
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'Error desconocido')
    }
  }

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
                disabled={completed.includes(lesson.id)}
                onClick={() => void markComplete(lesson.id)}
              >
                {completed.includes(lesson.id) ? 'Completada' : 'Marcar completada'}
              </button>
            )}
          </article>
        ))}
      </div>
    </main>
  )
}
