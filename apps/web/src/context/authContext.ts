import { createContext } from 'react'
import type { User } from '@supabase/supabase-js'

export interface AuthContextValue {
  user: User | null
  token: string | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  /** Devuelve true si Supabase exige confirmar el correo antes de ingresar. */
  signUp: (email: string, password: string) => Promise<boolean>
  signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
