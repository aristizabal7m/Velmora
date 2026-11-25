import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ErrorBoundary } from './components/ErrorBoundary'
import { Header } from './components/Header'
import { AuthProvider } from './context/AuthContext'
import { ExplorePage } from './pages/ExplorePage'
import { LessonsPage } from './pages/LessonsPage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ProfilePage } from './pages/ProfilePage'
import './App.css'

function Layout() {
  return (
    <div className="app">
      <a className="skip-link" href="#contenido">
        Saltar al contenido
      </a>
      <Header />
      <div id="contenido">
        <Routes>
          <Route path="/" element={<ExplorePage />} />
          <Route path="/lecciones" element={<LessonsPage />} />
          <Route path="/ingresar" element={<LoginPage />} />
          <Route path="/perfil" element={<ProfilePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </div>
      <footer className="site-footer">
        <p>
          VELMORA es educativo. No garantiza rendimientos ni constituye asesoría
          financiera.
        </p>
      </footer>
    </div>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Layout />
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
