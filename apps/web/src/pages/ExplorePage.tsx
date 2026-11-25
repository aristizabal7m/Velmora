import { useEffect, useState } from 'react'
import { InvestmentCard } from '../components/InvestmentCard'
import { InvestmentFiltersForm } from '../components/InvestmentFiltersForm'
import { useAuth } from '../hooks/useAuth'
import {
  getCategories,
  getInvestments,
  getRecommendations,
} from '../lib/api'
import type {
  Category,
  Investment,
  InvestmentFilters,
  Recommendation,
} from '../types/api'

const initialFilters: InvestmentFilters = {
  risk: '',
  category: '',
  minAmount: '',
  maxAmount: '',
}

export function ExplorePage() {
  const [filters, setFilters] = useState(initialFilters)
  const [categories, setCategories] = useState<Category[]>([])
  const [investments, setInvestments] = useState<Investment[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { token } = useAuth()

  useEffect(() => {
    let active = true
    void (async () => {
      try {
        const data = await getCategories()
        if (active) setCategories(data)
      } catch {
        if (active) setCategories([])
      }
    })()
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    let active = true
    void (async () => {
      if (active) setLoading(true)
      try {
        const data = await getInvestments(filters, token)
        if (!active) return
        setInvestments(data)
        setError(null)
      } catch (reason: unknown) {
        if (!active) return
        setError(reason instanceof Error ? reason.message : 'Error desconocido')
      } finally {
        if (active) setLoading(false)
      }
    })()
    return () => {
      active = false
    }
  }, [filters, token])

  useEffect(() => {
    if (!token) return
    let active = true
    void (async () => {
      try {
        const data = await getRecommendations('moderado', token)
        if (active) setRecommendations(data)
      } catch {
        if (active) setRecommendations([])
      }
    })()
    return () => {
      active = false
    }
  }, [token])

  const visibleRecommendations = token ? recommendations : []

  return (
    <main className="main-content">
      <section className="hero-section" aria-labelledby="explore-title">
        <h1 id="explore-title">Explora tus opciones de inversión</h1>
        <p>
          Compara alternativas según tu presupuesto, nivel de riesgo y categoría.
          Información educativa para personas en Colombia.
        </p>
      </section>

      <InvestmentFiltersForm
        categories={categories}
        filters={filters}
        onChange={setFilters}
      />

      {error !== null && (
        <p className="status-error" role="alert">
          No se pudieron cargar las inversiones: {error}
        </p>
      )}

      {loading ? (
        <p>Cargando inversiones…</p>
      ) : (
        <section aria-label="Listado de inversiones">
          <h2>Alternativas disponibles</h2>
          <div className="card-grid">
            {investments.map((investment) => (
              <InvestmentCard key={investment.id} investment={investment} />
            ))}
          </div>
          {investments.length === 0 && <p>No hay alternativas con estos filtros.</p>}
        </section>
      )}

      {visibleRecommendations.length > 0 && (
        <section aria-labelledby="recommendations-title">
          <h2 id="recommendations-title">Sugerencias para tu perfil</h2>
          <p className="disclaimer">
            Sugerencias educativas basadas en riesgo; no prometen rentabilidad.
          </p>
          <div className="card-grid">
            {visibleRecommendations.map((recommendation) => (
              <article key={recommendation.investment.id} className="investment-card">
                <h3>{recommendation.investment.name}</h3>
                <p>{recommendation.reason}</p>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  )
}
