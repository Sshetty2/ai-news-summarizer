# News Summarizer - Django + React Application

A full-stack news analysis application that fetches trending news articles and provides AI-powered political sentiment analysis with rich data visualizations.

## Features

- **News Aggregation**: Fetch and display trending news articles from NewsAPI.org
- **AI-Powered Analysis**: Political bias detection, sentiment analysis, and topic categorization using OpenAI
- **Rich Visualizations**: Interactive charts showing sentiment breakdown, topic distribution, and bias metrics
- **User Authentication**: Secure user accounts with session-based authentication
- **Analysis History**: Track and review past article analyses
- **Responsive UI**: Modern, clean interface built with React, TypeScript, and shadcn/ui

## Tech Stack

### Backend
- **Django 5.2.7** - Web framework
- **Django REST Framework** - API development
- **SQLite** - Database
- **OpenAI API** - AI-powered analysis
- **NewsAPI.org** - News article fetching
- **Python Decouple** - Environment variable management

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite 7** - Build tool
- **shadcn/ui** - Component library
- **Tailwind CSS v4** - Styling
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **React Router** - Routing

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 20+
- npm or yarn
- API keys from:
  - [NewsAPI.org](https://newsapi.org/)
  - [OpenAI](https://platform.openai.com/)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Activate virtual environment**:
   ```powershell
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** in the `backend` directory:
   ```env
   # Django Settings
   SECRET_KEY=django-insecure-g*afo11^ux)11&*l1%r_k7so=d0-ive$9kplokkga421j!vg$w
   DEBUG=True

   # API Keys (REPLACE WITH YOUR ACTUAL KEYS)
   NEWS_API_KEY=your_news_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run migrations** (if not already done):
   ```bash
   python manage.py migrate
   ```

6. **Create demo user** (for testing):
   ```bash
   python manage.py create_demo_user
   ```
   This creates a user with:
   - Username: `demo_user`
   - Password: `demo123`

7. **Create sample categories** (if not already done):
   ```bash
   python manage.py shell -c "from news.services import populate_sample_categories; populate_sample_categories()"
   ```

8. **Start the Django development server**:
   ```bash
   python manage.py runserver
   ```
   Backend will run at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   Frontend will run at: `http://localhost:5173`

## Usage

### Getting Started

1. **Access the application**: Open `http://localhost:5173` in your browser

2. **Login options**:
   - **Demo User**: Click the "Demo Login" button (bottom right) to quickly test with pre-created user
     - Username: `demo_user`
     - Password: `demo123`
   - **Create Account**: Click "Sign In" button (top right) and choose "Sign up"
   - **Sign In**: Use the "Sign In" button with your credentials

3. **Fetch News Articles** (IMPORTANT - First Time Setup):
   - If no articles appear, the database is empty
   - **Option 1**: Click the **"Fetch Latest News"** button in the UI (requires login)
   - **Option 2**: Run manually from backend:
     ```bash
     cd backend
     python manage.py fetch_news --max-articles 50
     ```
   - Use category filters to browse by topic
   - Use the search bar to find specific articles
   - Click "Refresh" to reload articles

4. **Analyze Articles**:
   - Click the "Analyze" button on any article card
   - Wait for AI analysis to complete (10-15 seconds)
   - View comprehensive analysis on the right panel including:
     - Political bias classification
     - Sentiment breakdown (positive/negative/neutral)
     - Topic distribution
     - Controversy level
     - Key themes and insights

5. **View Analysis History**:
   - Previously analyzed articles show "Analyzed" badge
   - Click to view past analysis results

### ⚠️ Important Notes

- **Database starts empty**: You must fetch news articles before using the app
- **News API**: The frontend does NOT call newsapi.org directly - it only calls your Django backend
- **Data flow**: External News API → Django (stores in DB) → React Frontend
- See [API_ARCHITECTURE.md](./API_ARCHITECTURE.md) for detailed architecture explanation

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Create new user account
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user info
- `GET /api/auth/dashboard/` - User dashboard data

### News
- `GET /api/news/articles/` - List articles (with filtering)
- `GET /api/news/articles/:id/` - Get article details
- `GET /api/news/categories/` - List categories
- `POST /api/news/articles/fetch_latest/` - Fetch new articles from NewsAPI
- `GET /api/news/articles/trending/` - Get trending articles

### Analysis
- `POST /api/analysis/analyses/analyze_article/` - Analyze an article
- `GET /api/analysis/analyses/` - List user's analyses
- `GET /api/analysis/analyses/:id/` - Get analysis details
- `GET /api/analysis/analyses/stats/` - Get analysis statistics
- `GET /api/analysis/analyses/trending_topics/` - Get trending topics

## Database Models

### NewsArticle
- Stores article metadata (title, description, URL, etc.)
- Links to NewsSource and NewsCategory
- Tracks publication date and active status

### SentimentAnalysis
- Stores AI analysis results
- Political bias classification (far_left to far_right)
- Sentiment metrics (positive, negative, neutral percentages)
- Topic distribution and key themes
- Controversy level and emotional tone
- Links to User and NewsArticle

### UserProfile
- Extended user information
- Usage tracking (total analyses, last analysis date)
- Preferences and settings

## Development

### Django Admin
Access at `http://localhost:8000/admin/`
- Username: `admin`
- Password: `admin` (created during setup)

### Fetching News Articles
To populate the database with news articles, you have three options:

1. **UI Button** (easiest - requires login):
   - Click "Fetch Latest News" button when database is empty

2. **Management Command**:
   ```bash
   python manage.py fetch_news --max-articles 50
   python manage.py fetch_news --category technology --max-articles 30
   ```

3. **Django Shell**:
   ```python
   from news.services import NewsAPIService
   service = NewsAPIService()
   service.fetch_and_store_articles(category='politics', max_articles=50)
   ```

**Valid Categories**: general, business, technology, politics, health, science, sports, entertainment

### Testing Analysis
The AI analysis uses OpenAI's GPT-4o-mini model for cost efficiency while maintaining quality. Each analysis typically takes 10-15 seconds and costs approximately $0.01-0.02 per article.

## Project Structure

```
news-summarizer-django-test/
├── backend/
│   ├── news_summarizer/          # Django project settings
│   ├── news/                      # News articles app
│   │   ├── models.py              # NewsArticle, NewsCategory, NewsSource
│   │   ├── views.py               # API views for news
│   │   ├── serializers.py         # DRF serializers
│   │   └── services.py            # NewsAPI integration
│   ├── analysis/                  # Analysis app
│   │   ├── models.py              # SentimentAnalysis model
│   │   ├── views.py               # Analysis API views
│   │   ├── serializers.py         # Analysis serializers
│   │   └── services.py            # OpenAI integration
│   ├── authentication/            # Auth app
│   │   ├── models.py              # UserProfile model
│   │   ├── views.py               # Auth endpoints
│   │   └── serializers.py         # User serializers
│   ├── manage.py
│   └── db.sqlite3                 # SQLite database
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Auth/              # Authentication components
    │   │   ├── News/              # News display components
    │   │   ├── Analysis/          # Analysis dashboard components
    │   │   ├── Layout/            # Layout components
    │   │   └── ui/                # shadcn/ui components
    │   ├── contexts/              # React contexts
    │   ├── lib/
    │   │   ├── api.ts             # API client & types
    │   │   └── utils.ts           # Utility functions
    │   ├── App.tsx                # Main app component
    │   └── main.tsx               # Entry point
    ├── package.json
    └── vite.config.ts

```

## Troubleshooting

### Backend Issues

**Database errors**: Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

**CORS errors**: Ensure `django-cors-headers` is installed and configured in settings.py

**API key errors**: Check that your `.env` file exists and contains valid API keys

### Frontend Issues

**Build errors**: Clear node_modules and reinstall
```bash
rm -rf node_modules package-lock.json
npm install
```

**API connection errors**: Ensure backend is running on port 8000

**Tailwind CSS errors**: Ensure Tailwind v4 is properly installed with `@tailwindcss/vite`

## Future Enhancements

- Email verification for user registration
- Password reset functionality
- Article bookmarking and favorites
- Comparative analysis of multiple articles
- Export analysis reports (PDF/CSV)
- Advanced filtering and sorting options
- Real-time notifications for new articles
- Social sharing features

## License

This project is for educational and demonstration purposes.

## Credits

- News data provided by [NewsAPI.org](https://newsapi.org/)
- AI analysis powered by [OpenAI](https://openai.com/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
