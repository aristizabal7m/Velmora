import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { getCategories, getInvestments, getLessons } from './lib/api'
import type { Investment } from './types/api'

vi.mock('./lib/api', () => ({
  getCategories: vi.fn(),
  getInvestments: vi.fn(),
  getRecommendations: vi.fn(),
  getLessons: vi.fn(),
}))

const investment: Investment = {
  id: '1',
  name: 'CDT bancario',
  slug: 'cdt-bancario',
  summary: 'Tasa fija',
  minimum_amount: '1000000',
  risk_level: 'bajo',
  horizon_months: 12,
  category_id: null,
  published: true,
  disclaimer: 'No garantiza rendimientos.',
}

describe('App', () => {
  beforeEach(() => {
    vi.mocked(getCategories).mockResolvedValue([])
    vi.mocked(getInvestments).mockResolvedValue([investment])
    vi.mocked(getLessons).mockResolvedValue([])
  })

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('muestra las inversiones devueltas por la API', async () => {
    render(<App />)

    expect(await screen.findByText('CDT bancario')).toBeInTheDocument()
    expect(screen.getByText(/Tasa fija/)).toBeInTheDocument()
  })

  it('muestra un error cuando falla la carga de inversiones', async () => {
    vi.mocked(getInvestments).mockRejectedValue(new Error('La API respondió 500'))
    render(<App />)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'No se pudieron cargar las inversiones',
    )
  })

  it('envía los filtros seleccionados a la API', async () => {
    render(<App />)
    const riskSelect = await screen.findByLabelText('Nivel de riesgo')

    fireEvent.change(riskSelect, { target: { value: 'alto' } })

    await waitFor(() => {
      expect(getInvestments).toHaveBeenCalledWith(
        expect.objectContaining({ risk: 'alto' }),
        null,
      )
    })
  })
})
