import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { isAuthConfigured } from '../lib/supabase'

export function LoginPage() {
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const { signIn, signUp } = useAuth()
  const navigate = useNavigate()

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      if (mode === 'login') {
        await signIn(email, password)
      } else if (await signUp(email, password)) {
        setNotice('Te enviamos un correo de confirmación. Confírmalo y luego ingresa.')
        setMode('login')
        return
      }
      navigate('/')
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'Error desconocido')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="main-content">
      <h1>{mode === 'login' ? 'Ingresar' : 'Crear cuenta'}</h1>
      {!isAuthConfigured && (
        <p className="status-error" role="alert">
          Configura VITE_SUPABASE_URL y VITE_SUPABASE_PUBLISHABLE_KEY para usar la
          autenticación.
        </p>
      )}
      <form className="auth-form" onSubmit={(event) => void submit(event)}>
        <label>
          Correo electrónico
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error !== null && (
          <p className="status-error" role="alert">
            {error}
          </p>
        )}
        {notice !== null && <p role="status">{notice}</p>}
        <button type="submit" disabled={busy || !isAuthConfigured}>
          {busy ? 'Procesando…' : mode === 'login' ? 'Ingresar' : 'Registrarme'}
        </button>
      </form>
      <p>
        <button
          type="button"
          className="link-button"
          onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}
        >
          {mode === 'login' ? '¿No tienes cuenta? Regístrate' : 'Ya tengo cuenta'}
        </button>
      </p>
      <p>
        <Link to="/">Volver a explorar</Link>
      </p>
    </main>
  )
}
