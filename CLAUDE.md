# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A full-stack Django + React news analysis application that fetches news articles from NewsAPI.org and provides AI-powered political sentiment analysis with data visualizations. The app uses a 3-tier architecture: External News API → Django Backend (storage) → React Frontend (display).

## Development Commands

### Backend (Django)

Run all backend commands from the `backend/` directory with the virtual environment activated:

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Fetch news articles (REQUIRED on first run)
python manage.py fetch_news --max-articles 50
python manage.py fetch_news --category technology --max-articles 30

# Create demo user for testing
python manage.py create_demo_user  # Creates: demo_user/demo123

# Django shell for testing
python manage.py shell
```

Valid news categories: `general`, `business`, `technology`, `politics`, `health`, `science`, `sports`, `entertainment`

### Frontend (React + Vite)

Run all frontend commands from the `frontend/` directory:

```bash
# Install dependencies
npm install

# Start development server (runs on http://localhost:5173)
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

## Architecture

### 3-Tier Data Flow

1. **External News API (newsapi.org)** - Only accessed by Django backend
2. **Django Backend** - Fetches from NewsAPI, stores in SQLite, exposes REST API
3. **React Frontend** - Consumes Django API, NEVER calls newsapi.org directly

**Critical**: The frontend only communicates with the Django backend at `localhost:8000/api`. The backend handles all external API calls.

### Django Apps Structure

The backend uses a modular Django app architecture:

- **news** (`backend/news/`) - News article management
  - Models: `NewsArticle`, `NewsSource`, `NewsCategory`, `UserReadArticle`
  - Services: `NewsAPIService` - Handles NewsAPI.org integration
  - Management commands: `fetch_news`
  - API endpoints for article listing, filtering, searching, trending

- **analysis** (`backend/analysis/`) - AI-powered analysis
  - Models: `SentimentAnalysis`, `AnalysisComparison`, `UserPreferences`
  - Services: `OpenAIAnalysisService` - Handles OpenAI GPT-4o-mini integration
  - Political bias classification (7 levels: far_left → far_right)
  - Sentiment analysis (positive/negative/neutral percentages)
  - Topic distribution and controversy scoring

- **authentication** (`backend/authentication/`) - User management
  - Models: `UserProfile` (extends Django User)
  - Session-based authentication with CSRF tokens
  - Management commands: `create_demo_user`
  - Dashboard and user statistics

### Frontend Architecture

Built with React 19, TypeScript, Vite 7, and shadcn/ui:

- **API Client** (`frontend/src/lib/api.ts`) - Centralized API communication with axios
  - Handles CSRF token management automatically
  - Exports `newsAPI` and `analysisAPI` objects
  - All requests go to `http://localhost:8000/api`

- **Components Structure**:
  - `Auth/` - Login/registration modals
  - `News/` - Article cards and lists
  - `Analysis/` - Analysis dashboard with Recharts visualizations
  - `Layout/` - Main layout wrapper
  - `ui/` - shadcn/ui components (button, card, dialog, etc.)

- **Context**: `AuthContext.tsx` - Global authentication state management

- **Styling**: Tailwind CSS v4 with shadcn/ui design system

### Key Services Implementation

**NewsAPIService** (`backend/news/services.py`):
- Uses only 2 valid NewsAPI endpoints: `/v2/top-headlines` and `/v2/everything`
- Method `fetch_and_store_articles()` fetches from external API and persists to database
- Handles source/category creation, date parsing, deduplication by URL

**OpenAIAnalysisService** (`backend/analysis/services.py`):
- Uses GPT-4o-mini model for cost efficiency
- Structured JSON output with `response_format={"type": "json_object"}`
- Comprehensive prompt for political bias, sentiment, topics, controversy
- Processing typically takes 10-15 seconds per article
- Includes methods for bulk analysis and comparative analysis

### Database Models

**NewsArticle** (news/models.py:31):
- Stores title, description, content, URL, image, author, published date
- Foreign keys: `source` (NewsSource), `category` (NewsCategory)
- Indexed by published_at, category, source for query performance
- Unique constraint on URL to prevent duplicates

**SentimentAnalysis** (analysis/models.py:7):
- Links to User and NewsArticle (many analyses per article/user combination)
- Political bias: 8 choices (far_left, left, center_left, center, center_right, right, far_right, neutral)
- Sentiment: positive/negative/neutral percentages (0-1, sum to 1.0)
- Topics: JSONField for primary_topics (list) and topic_distribution (dict)
- Stores raw_ai_response for debugging and analysis version tracking
- Property `bias_score_normalized`: converts bias to numeric -1 to 1 scale

**UserProfile** (authentication/models.py):
- Extended user model with usage tracking
- Fields: total_analyses_created, last_analysis_date, preferences

### API Endpoints

All endpoints are prefixed with `/api/`:

**Authentication** (`/api/auth/`):
- POST `/login/`, `/register/`, `/logout/`
- GET `/user/`, `/dashboard/`

**News** (`/api/news/articles/`):
- GET `/` - List with filtering (category, search, page_size)
- GET `/:id/` - Single article detail
- GET `/trending/` - Most analyzed articles
- GET `/categories_with_counts/` - Categories with article counts
- POST `/fetch_latest/` - Fetch new articles from NewsAPI (auth required)
- POST `/:id/mark_as_read/` - Mark article as read (auth required)

**Analysis** (`/api/analysis/analyses/`):
- POST `/analyze_article/` - Create analysis (auth required)
- GET `/` - List user's analyses
- GET `/:id/` - Single analysis detail
- GET `/stats/` - User analysis statistics
- GET `/trending_topics/` - Trending topics from analyses

### Django Settings

**Environment Variables** (backend/.env):
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `NEWS_API_KEY` - NewsAPI.org API key (REQUIRED)
- `OPENAI_API_KEY` - OpenAI API key (REQUIRED)

**CORS Configuration**:
- Allowed origins: localhost:5173 (Vite), localhost:3000
- Credentials enabled for session-based auth
- CSRF trusted origins configured

**DRF Settings**:
- SessionAuthentication by default
- AllowAny on many News endpoints, IsAuthenticated on Analysis/Auth
- PageNumberPagination with PAGE_SIZE=20

## Common Development Tasks

### First-Time Setup

1. Backend: Create `.env` file with API keys, run migrations, create demo user, fetch initial news
2. Frontend: Install dependencies with `npm install`
3. Start both servers: Django on :8000, Vite on :5173
4. Important: Database starts empty, must run `fetch_news` or click "Fetch Latest News" button

### Adding New Features

**New API Endpoint**:
1. Add method to appropriate ViewSet in `views.py`
2. Add URL pattern in `urls.py` if needed
3. Create/update serializer in `serializers.py`
4. Add corresponding method to `frontend/src/lib/api.ts`

**New Analysis Field**:
1. Add field to `SentimentAnalysis` model
2. Create migration: `python manage.py makemigrations`
3. Update `OpenAIAnalysisService.get_analysis_prompt()` to request field
4. Update serializer to include field
5. Update frontend types in `api.ts` and display in components

**New News Source**:
- NewsSource and NewsCategory are auto-created by `fetch_and_store_articles()`
- No manual creation needed unless adding custom sources

### Testing the Application

**Test News API Connection**:
```python
from news.services import NewsAPIService
service = NewsAPIService()
data = service.get_top_headlines(page_size=5)
```

**Test Analysis**:
```python
from analysis.services import OpenAIAnalysisService
from news.models import NewsArticle
from django.contrib.auth.models import User

service = OpenAIAnalysisService()
article = NewsArticle.objects.first()
user = User.objects.first()
analysis = service.analyze_article(article, user)
```

**Check Database Contents**:
```python
from news.models import NewsArticle
NewsArticle.objects.count()  # How many articles?
NewsArticle.objects.first()  # See first article
```

### Common Issues

**Empty Articles List**: Database is empty, run `python manage.py fetch_news` or use UI button

**News API Errors**: Check NEWS_API_KEY in .env, verify API key at newsapi.org, check rate limits (free tier: 100 requests/day)

**Analysis Fails**: Check OPENAI_API_KEY in .env, verify OpenAI account has credits

**CORS Errors**: Ensure django-cors-headers is installed and CORS_ALLOWED_ORIGINS in settings.py includes frontend URL

**Frontend Build Errors**: Ensure Tailwind v4 is installed with `@tailwindcss/vite` plugin

## Important Notes

- The frontend NEVER calls newsapi.org directly - it only calls the Django backend
- Database uses SQLite by default - suitable for development, consider PostgreSQL for production
- Analysis uses GPT-4o-mini for cost efficiency (cost per article: ~$0.01-0.02)
- Session-based authentication stores credentials in cookies - no JWT tokens
- Django admin available at `/admin/` (credentials: admin/admin if created during setup)
- All timestamps use UTC timezone
- Articles are deduplicated by URL - re-fetching same category won't create duplicates
