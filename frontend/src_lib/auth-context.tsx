'use client'

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { authApi, tokenManager, User, ApiError } from './api'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Refresh user data from API
  const refreshUser = useCallback(async () => {
    if (!tokenManager.isAuthenticated()) {
      setUser(null)
      setIsLoading(false)
      return
    }

    try {
      const userData = await authApi.getMe()
      setUser(userData)
      // Store user data for quick access
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (error) {
      if (error instanceof ApiError && error.isUnauthorized()) {
        // Token is invalid or expired
        tokenManager.removeToken()
        localStorage.removeItem('user')
        setUser(null)
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Check for stored auth on mount
  useEffect(() => {
    const initAuth = async () => {
      // First, try to load cached user for immediate display
      const storedUser = localStorage.getItem('user')
      if (storedUser && tokenManager.isAuthenticated()) {
        try {
          setUser(JSON.parse(storedUser))
        } catch {
          // Invalid stored user
        }
      }

      // Then verify with the server
      await refreshUser()
    }

    initAuth()
  }, [refreshUser])

  // Listen for unauthorized events
  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null)
      router.push('/login')
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [router])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await authApi.login(email, password)
      setUser(response.user)
      localStorage.setItem('user', JSON.stringify(response.user))
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true)
    try {
      const response = await authApi.register(email, password, name)
      setUser(response.user)
      localStorage.setItem('user', JSON.stringify(response.user))
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    authApi.logout()
    localStorage.removeItem('user')
    setUser(null)
    router.push('/login')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// HOC for protected routes
export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
): React.FC<P> {
  return function ProtectedRoute(props: P) {
    const { isAuthenticated, isLoading } = useAuth()
    const router = useRouter()

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/login')
      }
    }, [isLoading, isAuthenticated, router])

    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      )
    }

    if (!isAuthenticated) {
      return null
    }

    return <WrappedComponent {...props} />
  }
}
