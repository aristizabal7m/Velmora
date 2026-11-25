import type { Investment } from '../types/api'

const formatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

export function InvestmentCard({ investment }: { investment: Investment }) {
  return (
    <article className="investment-card">
      <h3>{investment.name}</h3>
      <p>{investment.summary}</p>
      <dl className="investment-meta">
        <div>
          <dt>Inversión mínima</dt>
          <dd>{formatter.format(Number(investment.minimum_amount))}</dd>
        </div>
        <div>
          <dt>Riesgo</dt>
          <dd className={`risk risk-${investment.risk_level}`}>
            {investment.risk_level}
          </dd>
        </div>
        {investment.horizon_months !== null && (
          <div>
            <dt>Plazo orientativo</dt>
            <dd>{investment.horizon_months} meses</dd>
          </div>
        )}
      </dl>
      <p className="disclaimer">{investment.disclaimer}</p>
    </article>
  )
}
