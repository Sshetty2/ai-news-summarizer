# AI News Summarizer - API Architecture Guide

## 🏗️ System Architecture

The application uses a **3-tier architecture**:

```
External News API (newsapi.org)
        ↓
Django Backend (fetches & stores)
        ↓
React Frontend (displays)
```

### Important: Two Different APIs

1. **External News API** (newsapi.org) - Only used by Django backend
2. **Internal Django API** - Used by React frontend

## 📡 External News API (newsapi.org)

### Valid Endpoints (Used by Backend Only)

The News API provides only **3 endpoints**:

1. **`/v2/top-headlines`** - Get breaking news headlines
2. **`/v2/everything`** - Search and filter articles
3. **`/v2/top-headlines/sources`** - Get available news sources (not currently used)

### Backend Implementation

Located in: `backend/news/services.py`

```python
class NewsAPIService:
    BASE_URL = "https://newsapi.org/v2"
    
    def get_top_headlines(self, category=None, country="us", page_size=50):
        """Fetch top headlines from News API"""
        # Uses: /v2/top-headlines
        
    def get_everything(self, query, from_date=None, sort_by="publishedAt", page_size=50):
        """Search for articles with everything endpoint"""
        # Uses: /v2/everything
        
    def fetch_and_store_articles(self, category=None, max_articles=100):
        """Fetch articles from NewsAPI and store them in database"""
        # Fetches from News API → Stores in Django DB
```

## 🔌 Internal Django API Endpoints

### News Endpoints (`/api/news/`)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/news/articles/` | GET | No* | List articles from DB |
| `/api/news/articles/{id}/` | GET | No* | Get single article |
| `/api/news/articles/categories_with_counts/` | GET | No* | Get categories with article counts |
| `/api/news/articles/trending/` | GET | No* | Get trending articles (most analyzed) |
| `/api/news/articles/fetch_latest/` | POST | **Yes** | Fetch new articles from News API |
| `/api/news/articles/{id}/mark_as_read/` | POST | **Yes** | Mark article as read |
| `/api/news/categories/` | GET | No* | List all categories |
| `/api/news/sources/` | GET | No* | List all sources |

*Auth optional - some features require authentication

### Analysis Endpoints (`/api/analysis/`)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/analysis/analyses/` | GET | **Yes** | List user's analyses |
| `/api/analysis/analyses/{id}/` | GET | **Yes** | Get single analysis |
| `/api/analysis/analyses/analyze_article/` | POST | **Yes** | Create new analysis with AI |
| `/api/analysis/analyses/stats/` | GET | **Yes** | Get user's analysis statistics |
| `/api/analysis/analyses/trending_topics/` | GET | **Yes** | Get trending topics from analyses |
| `/api/analysis/analyses/recent/` | GET | **Yes** | Get recent analyses |
| `/api/analysis/analyses/controversial/` | GET | **Yes** | Get most controversial analyses |

### Authentication Endpoints (`/api/auth/`)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/auth/login/` | POST | No | User login |
| `/api/auth/register/` | POST | No | User registration |
| `/api/auth/logout/` | POST | **Yes** | User logout |
| `/api/auth/user/` | GET | **Yes** | Get current user info |
| `/api/auth/dashboard/` | GET | **Yes** | Get user dashboard data |

## 🎯 Frontend API Calls

Located in: `frontend/src/lib/api.ts`

### How Frontend Calls Work

```typescript
// Frontend NEVER calls newsapi.org directly!
// It only calls YOUR Django backend at localhost:8000/api

// Example: Get articles
newsAPI.getArticles({ page_size: 20 })
// Calls: http://localhost:8000/api/news/articles/?page_size=20
// Django returns articles FROM DATABASE, not from external API

// Example: Fetch new articles
newsAPI.fetchLatest(category, max_articles)
// Calls: http://localhost:8000/api/news/articles/fetch_latest/
// Django then calls newsapi.org and stores results in DB
```

### Frontend API Methods

```typescript
// News API (calls Django backend)
newsAPI.getArticles(params?)          // List articles from DB
newsAPI.getArticle(id)                // Get single article
newsAPI.getCategoriesWithCounts()     // Get categories with counts
newsAPI.getTrending()                 // Get trending articles
newsAPI.fetchLatest(category?, max?)  // Fetch NEW articles from News API
newsAPI.markAsRead(articleId)         // Mark as read

// Analysis API (calls Django backend)
analysisAPI.analyzeArticle(articleId) // Analyze with OpenAI
analysisAPI.getAnalyses(params?)      // List analyses
analysisAPI.getStats()                // Get statistics
```

## 🔄 Complete Data Flow

### Initial Setup (Empty Database)

1. **User opens app** → Frontend calls `newsAPI.getArticles()`
2. **Django returns empty list** (database is empty)
3. **Frontend shows empty state** with "Fetch Latest News" button
4. **User clicks button** → Frontend calls `newsAPI.fetchLatest()`
5. **Django backend** calls newsapi.org `/v2/top-headlines`
6. **Django stores articles** in local database
7. **Frontend reloads** and displays articles from database

### Normal Operation (Database Has Articles)

1. **User opens app** → Frontend calls `newsAPI.getArticles()`
2. **Django returns articles** from local database
3. **User filters by category** → Frontend calls `newsAPI.getArticles({ category: 'technology' })`
4. **Django queries database** with filter and returns results
5. **User searches** → Frontend calls `newsAPI.getArticles({ search: 'AI' })`
6. **Django searches database** and returns matching articles

### Analysis Flow

1. **User clicks "Analyze"** → Frontend calls `analysisAPI.analyzeArticle(articleId)`
2. **Django gets article** from database
3. **Django calls OpenAI API** to analyze the article
4. **Django stores analysis** in database
5. **Frontend receives analysis** and displays results

## 🔐 Authentication Flow

Django uses **session-based authentication** with CSRF tokens:

1. User logs in → Django creates session
2. Frontend stores session cookie
3. All subsequent requests include:
   - Session cookie (automatic)
   - CSRF token (from cookie, sent in header)

```typescript
// Frontend automatically adds CSRF token
apiClient.interceptors.request.use((config) => {
  const csrfToken = getCsrfTokenFromCookie()
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
})
```

## 📊 Database Models & Serializers

### How Serializers Work

Serializers convert between Django models (Python) and JSON (API responses):

**Example: NewsArticleListSerializer**

```python
class NewsArticleListSerializer(serializers.ModelSerializer):
    # Traverse relationship to get source name
    source_name = serializers.CharField(source="source.name", read_only=True)
    
    # Computed field using method
    has_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = ["id", "title", "description", ...]
    
    def get_has_analysis(self, obj):
        # obj is a NewsArticle instance
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.sentiment_analyses.filter(user=request.user).exists()
        return False
```

**What it does:**

- `source_name`: Instead of returning `source: 123`, it returns `source_name: "CNN"`
- `has_analysis`: Checks if current user has analyzed this article
- Automatically handles model → JSON conversion

### Read vs Write Fields

```python
class SentimentAnalysisSerializer(serializers.ModelSerializer):
    # For reading (GET requests) - returns full nested object
    article = NewsArticleListSerializer(read_only=True)
    
    # For writing (POST requests) - accepts just an ID
    article_id = serializers.IntegerField(write_only=True)
```

**Why both?**

- **POST request**: Send `{"article_id": 123, ...}` (just the ID)
- **GET response**: Receive `{"article": {"id": 123, "title": "...", ...}, ...}` (full object)

## 🚀 Getting Started

### 1. Setup Backend

```bash
cd backend

# Create .env file with your News API key
echo "NEWS_API_KEY=your_key_here" > .env

# Run migrations
python manage.py migrate

# Create demo user (optional)
python manage.py create_demo_user

# Fetch initial news (IMPORTANT!)
python manage.py fetch_news --max-articles 50
```

### 2. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Using the App

1. **Login** with demo user: `demo_user` / `demo123`
2. If no articles appear, click **"Fetch Latest News"** button
3. Browse articles, filter by category, search
4. Click **"Analyze"** on any article to get AI analysis

## ⚠️ Common Issues

### Empty Articles List

**Problem**: Frontend shows "No articles found"

**Solution**: 
- Backend database is empty
- Click "Fetch Latest News" button (requires login)
- Or run: `python manage.py fetch_news`

### News API Errors

**Problem**: "Failed to fetch news"

**Solutions**:
- Check `NEWS_API_KEY` is set in `.env`
- Verify API key is valid at newsapi.org
- Check API rate limits (free tier: 100 requests/day)

### Analysis Fails

**Problem**: "Failed to analyze article"

**Solutions**:
- Check `OPENAI_API_KEY` is set in `.env`
- Verify OpenAI API key is valid
- Check OpenAI account has credits

## 🔍 Debugging Tips

### Check What's in Database

```bash
cd backend
python manage.py shell

>>> from news.models import NewsArticle
>>> NewsArticle.objects.count()  # How many articles?
>>> NewsArticle.objects.first()  # See first article
```

### Test News API Connection

```bash
cd backend
python manage.py shell

>>> from news.services import NewsAPIService
>>> service = NewsAPIService()
>>> data = service.get_top_headlines(page_size=5)
>>> print(data)
```

### Monitor API Calls

Open browser DevTools → Network tab to see:
- What endpoints frontend calls
- What responses it receives
- Any errors

## 📝 Summary

**Key Points:**

1. ✅ **Frontend NEVER calls newsapi.org directly**
2. ✅ **All valid News API endpoints are properly implemented**
3. ✅ **Database acts as local cache for articles**
4. ✅ **Serializers handle all data transformations**
5. ✅ **Authentication required for fetching and analysis**

**The architecture is CORRECT!** The only issue was lack of initial data, which is now fixed with the "Fetch Latest News" button.

