import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <main className="main-content">
      <h1>Página no encontrada</h1>
      <p>
        Vuelve a <Link to="/">explorar inversiones</Link>.
      </p>
    </main>
  )
}
