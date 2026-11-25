import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export function Header() {
  const { user, signOut } = useAuth()

  return (
    <header className="site-header">
      <Link className="brand" to="/">
        VELMORA
      </Link>
      <nav aria-label="Navegación principal">
        <NavLink to="/" end>
          Explorar
        </NavLink>
        <NavLink to="/lecciones">Lecciones</NavLink>
        <NavLink to="/perfil">Perfil</NavLink>
      </nav>
      {user ? (
        <button type="button" onClick={() => void signOut()}>
          Cerrar sesión
        </button>
      ) : (
        <Link className="login-link" to="/ingresar">
          Ingresar
        </Link>
      )}
    </header>
  )
}
