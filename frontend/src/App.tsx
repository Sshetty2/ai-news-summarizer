import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import MainLayout from './components/Layout/MainLayout'
import NewsList from './components/News/NewsList'
import AnalysisDashboard from './components/Analysis/AnalysisDashboard'
import AuthModal from './components/Auth/AuthModal'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { type NewsArticle, type NewsCategory, type SentimentAnalysis, newsAPI, analysisAPI } from './lib/api'

function AppContent() {
  const { user, login, logout } = useAuth()
  
  // State management
  const [articles, setArticles] = useState<NewsArticle[]>([])
  const [categories, setCategories] = useState<NewsCategory[]>([])
  const [selectedAnalysis, setSelectedAnalysis] = useState<SentimentAnalysis | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isFetchingNews, setIsFetchingNews] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analyzingArticleId, setAnalyzingArticleId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)

  // Load initial data
  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const [articlesResponse, categoriesResponse] = await Promise.all([
        newsAPI.getArticles({ page_size: 20 }),
        newsAPI.getCategoriesWithCounts(),
      ])
      
      setArticles(articlesResponse.data.results || articlesResponse.data)
      setCategories(categoriesResponse.data || [])
    } catch (err) {
      setError('Failed to load news data. Please try again.')
      console.error('Error loading initial data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAnalyzeArticle = async (article: NewsArticle) => {
    if (!user) {
      setIsAuthModalOpen(true)
      return
    }

    setIsAnalyzing(true)
    setAnalyzingArticleId(article.id)
    setError(null)

    try {
      const response = await analysisAPI.analyzeArticle(article.id)
      setSelectedAnalysis(response.data.analysis)
      
      // Update the article to mark it as analyzed
      setArticles(prev => 
        prev.map(a => 
          a.id === article.id 
            ? { ...a, has_analysis: true }
            : a
        )
      )
    } catch (err) {
      setError('Failed to analyze article. Please try again.')
      console.error('Error analyzing article:', err)
    } finally {
      setIsAnalyzing(false)
      setAnalyzingArticleId(null)
    }
  }

  const handleRefresh = async () => {
    await loadInitialData()
  }

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      await loadInitialData()
      return
    }

    setIsLoading(true)
    try {
      const response = await newsAPI.getArticles({ 
        search: query,
        page_size: 20 
      })
      setArticles(response.data.results || response.data)
    } catch (err) {
      setError('Search failed. Please try again.')
      console.error('Error searching articles:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCategoryFilter = async (category: string | null) => {
    setSelectedCategory(category)
    setIsLoading(true)
    
    try {
      const response = await newsAPI.getArticles({ 
        category: category || undefined,
        page_size: 20 
      })
      setArticles(response.data.results || response.data)
    } catch (err) {
      setError('Failed to filter articles. Please try again.')
      console.error('Error filtering articles:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFetchNews = async () => {
    if (!user) {
      setIsAuthModalOpen(true)
      return
    }

    setIsFetchingNews(true)
    setError(null)

    try {
      const response = await newsAPI.fetchLatest(undefined, 50)
      
      if (response.data.created_count > 0) {
        // Reload the articles after fetching
        await loadInitialData()
      } else {
        setError('No new articles were fetched. The database might already be up to date.')
      }
    } catch (err) {
      setError('Failed to fetch news. Please ensure you have a valid NEWS_API_KEY configured.')
      console.error('Error fetching news:', err)
    } finally {
      setIsFetchingNews(false)
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      setSelectedAnalysis(null)
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  // Demo user login with actual API authentication
  const handleDemoLogin = async () => {
    try {
      await login('demo_user', 'demo123')
    } catch (error) {
      console.error('Demo login error:', error)
      alert('Demo login failed. Please try signing in manually.')
    }
  }

  // Open auth modal
  const handleOpenAuthModal = () => {
    setIsAuthModalOpen(true)
  }

  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Routes>
          <Route 
            path="/" 
            element={
              <MainLayout
                user={user || undefined}
                onLogout={user ? handleLogout : undefined}
                onSignIn={handleOpenAuthModal}
                leftPanel={
                  <NewsList
                    articles={articles}
                    categories={categories}
                    onAnalyzeArticle={handleAnalyzeArticle}
                    onRefresh={handleRefresh}
                    onSearch={handleSearch}
                    onCategoryFilter={handleCategoryFilter}
                    onFetchNews={handleFetchNews}
                    isLoading={isLoading}
                    isFetching={isFetchingNews}
                    error={error || undefined}
                    selectedCategory={selectedCategory}
                    analyzingArticleId={analyzingArticleId}
                  />
                }
                rightPanel={
                  <AnalysisDashboard
                    analysis={selectedAnalysis}
                    isLoading={isAnalyzing}
                  />
                }
              />
            } 
          />
        </Routes>

        {/* Demo Login Button for Testing */}
        {!user && (
          <div className="fixed bottom-4 right-4">
            <button
              onClick={handleDemoLogin}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md shadow-lg hover:bg-primary/90 transition-colors"
            >
              Demo Login (for testing)
            </button>
          </div>
        )}

        {/* Authentication Modal */}
        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
        />
      </div>
    </Router>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
