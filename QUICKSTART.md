# Quick Start Guide

Get the News Summarizer app running in under 5 minutes!

## Step 1: Backend Setup

1. **Create `.env` file** in the `backend` directory:
   ```bash
   cd backend
   ```

2. **Create and edit `.env`** (you can copy from .env.example if it exists):
   ```env
   SECRET_KEY=django-insecure-g*afo11^ux)11&*l1%r_k7so=d0-ive$9kplokkga421j!vg$w
   DEBUG=True
   NEWS_API_KEY=YOUR_ACTUAL_NEWS_API_KEY
   OPENAI_API_KEY=YOUR_ACTUAL_OPENAI_API_KEY
   ```

3. **Start the Django server**:
   ```powershell
   .\venv\Scripts\activate
   python manage.py runserver
   ```

   The backend will be available at `http://localhost:8000`

## Step 2: Fetch Some News Articles

In a new terminal (with venv activated):

```bash
cd backend
.\venv\Scripts\activate
python manage.py fetch_news --category=politics --max-articles=20
```

This will fetch 20 political news articles. You can also try:
- `--category=technology`
- `--category=business`
- `--category=general`
- Or omit `--category` for all categories

## Step 3: Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## Step 4: Try It Out!

1. **Open** `http://localhost:5173` in your browser

2. **Quick login** using the Demo User:
   - Click "Demo Login (for testing)" button in bottom-right
   - This logs you in as `demo_user` / `demo123`

3. **Or create your own account**:
   - Click "Sign In" button in top-right
   - Click "Don't have an account? Sign up"
   - Fill in the form and submit

4. **Analyze an article**:
   - Click the "Analyze" button on any news card
   - Wait 10-15 seconds for AI analysis
   - View the results in the right panel with:
     - Political bias meter
     - Sentiment breakdown pie chart
     - Topic distribution bar chart
     - Controversy level indicator
     - Key themes and AI reasoning

5. **Explore features**:
   - Filter by category using the filter button
   - Search for specific topics
   - View analysis history for analyzed articles

## Common Commands

### Backend

```bash
# Fetch more news
python manage.py fetch_news --category=technology --max-articles=30

# Create a new user manually
python manage.py createsuperuser

# Access Django admin
# Visit http://localhost:8000/admin/ (username: admin, password: admin)

# Check database
python manage.py shell
>>> from news.models import NewsArticle
>>> NewsArticle.objects.count()
```

### Frontend

```bash
# Install new dependencies
npm install <package-name>

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

**No articles showing?**
- Make sure you ran `python manage.py fetch_news`
- Check that your NEWS_API_KEY is valid

**Can't analyze articles?**
- Ensure you're logged in
- Check that your OPENAI_API_KEY is valid
- Check browser console for errors

**CORS errors?**
- Ensure backend is running on port 8000
- Ensure frontend is running on port 5173
- Check Django CORS settings in `backend/news_summarizer/settings.py`

## What's Next?

- Analyze more articles to build your history
- Try different news categories
- Compare political bias across different sources
- Explore the topic distribution patterns

Enjoy analyzing the news! 📰🤖📊
