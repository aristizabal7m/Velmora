import type { Category, InvestmentFilters, RiskLevel } from '../types/api'

interface Props {
  categories: Category[]
  filters: InvestmentFilters
  onChange: (filters: InvestmentFilters) => void
}

export function InvestmentFiltersForm({ categories, filters, onChange }: Props) {
  return (
    <form className="filters" aria-label="Filtros de inversión">
      <label>
        Nivel de riesgo
        <select
          value={filters.risk}
          onChange={(event) =>
            onChange({
              ...filters,
              risk: event.target.value as RiskLevel | '',
            })
          }
        >
          <option value="">Todos</option>
          <option value="bajo">Bajo</option>
          <option value="medio">Medio</option>
          <option value="alto">Alto</option>
        </select>
      </label>
      <label>
        Categoría
        <select
          value={filters.category}
          onChange={(event) =>
            onChange({ ...filters, category: event.target.value })
          }
        >
          <option value="">Todas</option>
          {categories.map((category) => (
            <option key={category.id} value={category.slug}>
              {category.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Monto mínimo (COP)
        <input
          type="number"
          min="0"
          value={filters.minAmount}
          onChange={(event) =>
            onChange({ ...filters, minAmount: event.target.value })
          }
        />
      </label>
      <label>
        Monto máximo (COP)
        <input
          type="number"
          min="0"
          value={filters.maxAmount}
          onChange={(event) =>
            onChange({ ...filters, maxAmount: event.target.value })
          }
        />
      </label>
    </form>
  )
}
