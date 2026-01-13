// API client for EmberLearn backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Token storage key
const TOKEN_KEY = 'emberlearn_token'

// Types
export interface User {
  id: string
  email: string
  name: string
}

export interface AuthResponse {
  token: string
  user: User
}

export interface ChatResponse {
  id: string
  message: string
  response: string
  agent_type: string
  created_at: string
}

export interface CodeExecutionResponse {
  success: boolean
  output: string
  error?: string
  execution_time_ms: number
}

export interface TopicProgress {
  slug: string
  name: string
  mastery_score: number
  exercises_completed: number
  total_exercises: number
}

export interface UserStats {
  user_id: string
  streak: number
  longest_streak: number
  total_xp: number
  level: number
  overall_mastery: number
  topics: TopicProgress[]
}

export interface Exercise {
  id: string
  title: string
  description: string
  difficulty: string
  topic_slug: string
  topic_name: string
  starter_code: string
  estimated_time: number
  completed: boolean
  best_score: number
}

export interface ExerciseDetail extends Exercise {
  solution?: string
  test_cases?: Array<{ input: string; expected: string }>
}

export interface TestCaseResult {
  input_data: string
  expected: string
  actual: string
  passed: boolean
}

export interface SubmitCodeResponse {
  success: boolean
  score: number
  passed: boolean
  output: string
  error?: string
  xp_earned: number
  test_results: TestCaseResult[]
}

// Legacy types for backward compatibility
export interface ProgressResponse {
  user_id: string
  overall_mastery: number
  topics: Array<{
    name: string
    mastery: number
    status: string
  }>
  streak_days: number
  total_exercises: number
  xp: number
  level: number
}

// Token management
export const tokenManager = {
  getToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(TOKEN_KEY)
  },

  setToken(token: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(TOKEN_KEY, token)
  },

  removeToken(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(TOKEN_KEY)
  },

  isAuthenticated(): boolean {
    return !!this.getToken()
  },
}

// API Error handling
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }

  isUnauthorized(): boolean {
    return this.status === 401
  }
}

// Fetch wrapper with JWT handling
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit,
  requireAuth: boolean = false
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  }

  // Add JWT token if available
  const token = tokenManager.getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  } else if (requireAuth) {
    throw new ApiError(401, 'Authentication required')
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      const apiError = new ApiError(response.status, error.detail || `HTTP ${response.status}`)
      
      // Handle 401 - clear token and redirect
      if (apiError.isUnauthorized()) {
        tokenManager.removeToken()
        // Optionally trigger a redirect to login
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('auth:unauthorized'))
        }
      }
      
      throw apiError
    }

    return response.json()
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new ApiError(0, 'Network error - is the backend running?')
  }
}

// Auth API
export const authApi = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await fetchApi<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    tokenManager.setToken(response.token)
    return response
  },

  async register(email: string, password: string, name: string): Promise<AuthResponse> {
    const response = await fetchApi<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    })
    tokenManager.setToken(response.token)
    return response
  },

  async getMe(): Promise<User> {
    return fetchApi<User>('/api/auth/me', { method: 'GET' }, true)
  },

  logout(): void {
    tokenManager.removeToken()
  },
}

// Chat API
export const chatApi = {
  async chat(message: string): Promise<ChatResponse> {
    return fetchApi<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    }, true)
  },

  async getHistory(): Promise<ChatResponse[]> {
    return fetchApi<ChatResponse[]>('/api/chat/history', { method: 'GET' }, true)
  },
}

// Code Execution API
export const sandboxApi = {
  async execute(code: string): Promise<CodeExecutionResponse> {
    return fetchApi<CodeExecutionResponse>('/api/execute', {
      method: 'POST',
      body: JSON.stringify({ code }),
    }, true)
  },

  async validate(code: string): Promise<{ valid: boolean; error?: string }> {
    return fetchApi<{ valid: boolean; error?: string }>('/api/execute/validate', {
      method: 'POST',
      body: JSON.stringify({ code }),
    }, true)
  },
}

// Progress API
export const progressApi = {
  async getStats(): Promise<UserStats> {
    return fetchApi<UserStats>('/api/progress', { method: 'GET' }, true)
  },

  async getTopics(): Promise<TopicProgress[]> {
    return fetchApi<TopicProgress[]>('/api/progress/topics', { method: 'GET' }, true)
  },

  async recordActivity(): Promise<{ streak: number; xp_earned: number; message: string }> {
    return fetchApi('/api/progress/activity', { method: 'POST' }, true)
  },

  // Legacy method for backward compatibility
  async getProgress(userId: string = 'anonymous'): Promise<ProgressResponse> {
    const stats = await this.getStats()
    return {
      user_id: stats.user_id,
      overall_mastery: stats.overall_mastery,
      topics: stats.topics.map(t => ({
        name: t.name,
        mastery: t.mastery_score,
        status: t.mastery_score >= 70 ? 'proficient' : t.mastery_score >= 40 ? 'learning' : 'beginner',
      })),
      streak_days: stats.streak,
      total_exercises: stats.topics.reduce((sum, t) => sum + t.exercises_completed, 0),
      xp: stats.total_xp,
      level: stats.level,
    }
  },
}

// Exercises API
export const exercisesApi = {
  async list(topic?: string): Promise<Exercise[]> {
    const endpoint = topic ? `/api/exercises?topic=${encodeURIComponent(topic)}` : '/api/exercises'
    return fetchApi<Exercise[]>(endpoint, { method: 'GET' }, true)
  },

  async getById(id: string): Promise<ExerciseDetail> {
    return fetchApi<ExerciseDetail>(`/api/exercises/${id}`, { method: 'GET' }, true)
  },

  async submit(id: string, code: string): Promise<SubmitCodeResponse> {
    return fetchApi<SubmitCodeResponse>(`/api/exercises/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ code }),
    }, true)
  },
}
