import axios, { type AxiosInstance, type AxiosResponse } from 'axios'

// API configuration
const API_BASE_URL = 'http://localhost:8000/api'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes - allow time for AI analysis
  withCredentials: true, // Include cookies for session authentication
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add CSRF token
apiClient.interceptors.request.use(
  (config) => {
    // Get CSRF token from cookies if available
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Types for API responses
export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  profile: UserProfile
}

export interface UserProfile {
  bio: string
  avatar?: string
  location: string
  website?: string
  email_notifications: boolean
  total_analyses_created: number
  last_analysis_date?: string
}

export interface NewsArticle {
  id: number
  title: string
  description: string
  content?: string
  url: string
  url_to_image?: string
  author?: string
  source_name: string
  category_name?: string
  category_slug?: string
  published_at: string
  has_analysis: boolean
}

export interface NewsCategory {
  id: number
  name: string
  slug: string
  description: string
  article_count: number
}

export interface SentimentAnalysis {
  id: number
  article: NewsArticle
  political_bias: string
  bias_confidence_score: number
  bias_reasoning: string
  positive_sentiment: number
  negative_sentiment: number
  neutral_sentiment: number
  overall_sentiment_score: number
  primary_topics: string[]
  topic_distribution: Record<string, number>
  key_themes: string[]
  emotional_tone: string
  controversy_level: number
  bias_score_normalized: number
  created_at: string
}

export interface AnalysisStats {
  total_analyses: number
  average_bias_score: number
  average_sentiment: number
  average_controversy: number
  bias_distribution: Record<string, number>
  top_topics: [string, number][]
  sentiment_range: {
    min: number
    max: number
  }
  analyses_by_month: Array<{
    month: string
    count: number
  }>
}

// Authentication API
export const authAPI = {
  login: (username: string, password: string) =>
    apiClient.post('/auth/login/', { username, password }),
  
  register: (userData: {
    username: string
    email: string
    password: string
    password_confirm: string
    first_name?: string
    last_name?: string
  }) =>
    apiClient.post('/auth/register/', userData),
  
  logout: () =>
    apiClient.post('/auth/logout/'),
  
  getCurrentUser: () =>
    apiClient.get('/auth/user/'),
  
  getDashboard: () =>
    apiClient.get('/auth/dashboard/'),
}

// News API
export const newsAPI = {
  getArticles: (params?: {
    category?: string
    search?: string
    page?: number
    page_size?: number
  }) =>
    apiClient.get('/news/articles/', { params }),
  
  getArticle: (id: number) =>
    apiClient.get(`/news/articles/${id}/`),
  
  getCategories: () =>
    apiClient.get('/news/categories/'),
  
  getCategoriesWithCounts: () =>
    apiClient.get('/news/articles/categories_with_counts/'),
  
  getTrending: () =>
    apiClient.get('/news/articles/trending/'),
  
  markAsRead: (articleId: number) =>
    apiClient.post(`/news/articles/${articleId}/mark_as_read/`),
  
  fetchLatest: (category?: string, max_articles?: number) =>
    apiClient.post('/news/articles/fetch_latest/', {
      category,
      max_articles: max_articles || 50
    }),
}

// Analysis API
export const analysisAPI = {
  getAnalyses: (params?: {
    bias?: string
    category?: string
    page?: number
    page_size?: number
  }) =>
    apiClient.get('/analysis/analyses/', { params }),
  
  getAnalysis: (id: number) =>
    apiClient.get(`/analysis/analyses/${id}/`),
  
  analyzeArticle: (articleId: number) =>
    apiClient.post('/analysis/analyses/analyze_article/', {
      article_id: articleId
    }),
  
  getStats: () =>
    apiClient.get('/analysis/analyses/stats/'),
  
  getTrendingTopics: (days?: number) =>
    apiClient.get('/analysis/analyses/trending_topics/', {
      params: { days: days || 7 }
    }),
  
  getRecent: () =>
    apiClient.get('/analysis/analyses/recent/'),
  
  getControversial: () =>
    apiClient.get('/analysis/analyses/controversial/'),
}

// Profile API
export const profileAPI = {
  getProfile: () =>
    apiClient.get('/auth/profile/'),
  
  updateProfile: (data: Partial<UserProfile>) =>
    apiClient.patch('/auth/profile/', data),
  
  getStats: () =>
    apiClient.get('/auth/profile/stats/'),
  
  changePassword: (data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }) =>
    apiClient.post('/auth/profile/change_password/', data),
}

export { apiClient }
export default apiClient
