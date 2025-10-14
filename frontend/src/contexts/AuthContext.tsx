import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authAPI, type User } from '@/lib/api'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (userData: {
    username: string
    email: string
    password: string
    password_confirm: string
    first_name?: string
    last_name?: string
  }) => Promise<void>
  checkAuthStatus: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.getCurrentUser()
      setUser(response.data)
    } catch (error) {
      setUser(null)
      // Clear any stale auth data
      localStorage.removeItem('user')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await authAPI.login(username, password)
      setUser(response.data.user)
      localStorage.setItem('user', JSON.stringify(response.data.user))
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      localStorage.removeItem('user')
    }
  }

  const register = async (userData: {
    username: string
    email: string
    password: string
    password_confirm: string
    first_name?: string
    last_name?: string
  }) => {
    try {
      const response = await authAPI.register(userData)
      setUser(response.data.user)
      localStorage.setItem('user', JSON.stringify(response.data.user))
    } catch (error) {
      throw error
    }
  }

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    register,
    checkAuthStatus,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthContext
