import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { LessonsPage } from './LessonsPage'
import {
  completeLesson,
  getLessonProgress,
  getLessons,
  getMyProfile,
  saveRiskProfile,
} from '../lib/api'
import type { Lesson, MyProfile } from '../types/api'

vi.mock('../lib/api', () => ({
  getLessons: vi.fn(),
  getLessonProgress: vi.fn(),
  completeLesson: vi.fn(),
  getMyProfile: vi.fn(),
  saveRiskProfile: vi.fn(),
}))

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    token: 'token-de-prueba',
    user: { email: 'ana@example.com' },
    loading: false,
    signIn: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
  }),
}))

const lessons: Lesson[] = [
  { id: 'l1', title: 'Qué es una inversión', slug: 'que-es', content: 'Texto', published: true },
  { id: 'risk', title: 'Riesgo y rentabilidad', slug: 'riesgo-y-rentabilidad', content: 'Texto', published: true },
]

const baseProfile: MyProfile = {
  id: 'u1',
  display_name: null,
  role: 'user',
  risk_profile: null,
  completed_lessons: 0,
  total_lessons: 2,
  risk_lesson_id: 'risk',
  can_choose_risk_profile: false,
}

describe('Flujo lección de riesgo → perfil', () => {
  beforeEach(() => {
    vi.mocked(getLessons).mockResolvedValue(lessons)
    vi.mocked(getLessonProgress).mockResolvedValue([])
    vi.mocked(completeLesson).mockResolvedValue(undefined)
    vi.mocked(getMyProfile)
      .mockResolvedValueOnce(baseProfile)
      .mockResolvedValue({ ...baseProfile, completed_lessons: 1, can_choose_risk_profile: true })
    vi.mocked(saveRiskProfile).mockResolvedValue({
      ...baseProfile,
      completed_lessons: 1,
      can_choose_risk_profile: true,
      risk_profile: 'agresivo',
    })
  })

  afterEach(() => {
    cleanup()
    vi.resetAllMocks()
  })

  it('habilita y guarda el perfil al completar la lección de riesgo', async () => {
    render(
      <MemoryRouter>
        <LessonsPage />
      </MemoryRouter>,
    )

    expect(
      await screen.findByText('Al completarla podrás definir tu perfil de riesgo.'),
    ).toBeInTheDocument()
    expect(screen.queryByRole('radio')).not.toBeInTheDocument()

    const buttons = await screen.findAllByRole('button', { name: 'Marcar completada' })
    fireEvent.click(buttons[1])

    fireEvent.click(await screen.findByLabelText(/Agresivo/))
    fireEvent.click(screen.getByRole('button', { name: 'Guardar perfil' }))

    expect(await screen.findByText(/Perfil guardado/)).toBeInTheDocument()
    expect(saveRiskProfile).toHaveBeenCalledWith('agresivo', 'token-de-prueba')
    expect(completeLesson).toHaveBeenCalledWith('risk', 'token-de-prueba')
    expect(await screen.findByText('Ver sugerencias para tu perfil')).toBeInTheDocument()
  })
})
