import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, _info: ErrorInfo): void {
    console.error('Error de interfaz:', error.message)
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <main className="main-content">
          <h1>Algo salió mal</h1>
          <p>Recarga la página para volver a intentarlo.</p>
        </main>
      )
    }
    return this.props.children
  }
}
