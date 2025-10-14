# Troubleshooting Guide

## Common Issues and Solutions

### 🔴 Issue: No Articles Appearing in Frontend

**Symptoms:**
- Frontend shows "No articles found"
- Empty state appears when you open the app
- Categories list is empty

**Root Cause:**
Database is empty - no articles have been fetched from News API yet

**Solutions (in order of preference):**

1. **Use UI Button** (Easiest):
   - Login with demo user or create account
   - Click the **"Fetch Latest News"** button in the empty state
   - Wait for articles to load (takes 5-10 seconds)

2. **Use Management Command**:
   ```bash
   cd backend
   python manage.py fetch_news --max-articles 50
   ```

3. **Verify in Database**:
   ```bash
   cd backend
   python manage.py shell
   >>> from news.models import NewsArticle
   >>> NewsArticle.objects.count()  # Should return > 0
   ```

---

### 🔴 Issue: "Failed to fetch news" Error

**Symptoms:**
- Error message when clicking "Fetch Latest News"
- Backend logs show API errors

**Possible Causes & Solutions:**

1. **Missing/Invalid News API Key**
   ```bash
   # Check your .env file
   cat backend/.env
   # Should contain: NEWS_API_KEY=your_actual_key
   ```
   
   **Fix:** Get API key from https://newsapi.org/ and add to `.env`

2. **Rate Limit Exceeded**
   - Free tier: 100 requests/day
   - Developer tier: 1000 requests/day
   
   **Fix:** Wait 24 hours or upgrade News API plan

3. **Network Issues**
   ```bash
   # Test API connection
   curl "https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_KEY"
   ```

---

### 🔴 Issue: Analysis Fails

**Symptoms:**
- "Failed to analyze article" error
- Analysis takes too long and times out

**Possible Causes & Solutions:**

1. **Missing/Invalid OpenAI API Key**
   ```bash
   # Check your .env file
   cat backend/.env
   # Should contain: OPENAI_API_KEY=sk-...
   ```
   
   **Fix:** Get API key from https://platform.openai.com/

2. **No OpenAI Credits**
   - Check your OpenAI account balance
   - Each analysis costs ~$0.01-0.02
   
   **Fix:** Add credits to OpenAI account

3. **Timeout Issues**
   - OpenAI API might be slow
   
   **Fix:** Try again after a few minutes

---

### 🔴 Issue: CORS Errors in Browser Console

**Symptoms:**
- Browser console shows "CORS policy" errors
- Frontend can't connect to backend

**Solutions:**

1. **Check Backend is Running**
   ```bash
   # Should see server running on port 8000
   cd backend
   python manage.py runserver
   ```

2. **Verify CORS Settings**
   ```python
   # backend/news_summarizer/settings.py
   INSTALLED_APPS = [
       ...
       'corsheaders',  # Should be here
   ]
   
   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',  # Should be near top
       ...
   ]
   
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:5173",  # Should match frontend URL
   ]
   ```

3. **Restart Backend**
   ```bash
   # Stop (Ctrl+C) and restart
   python manage.py runserver
   ```

---

### 🔴 Issue: Authentication Errors

**Symptoms:**
- Can't login
- "Invalid credentials" error
- Session expires immediately

**Solutions:**

1. **Demo User Not Created**
   ```bash
   cd backend
   python manage.py create_demo_user
   ```
   
   Then login with:
   - Username: `demo_user`
   - Password: `demo123`

2. **CSRF Token Issues**
   - Clear browser cookies
   - Hard refresh (Ctrl+Shift+R)
   - Check browser console for CSRF errors

3. **Session Cookie Issues**
   - Ensure backend and frontend URLs match in settings
   - Check `CORS_ALLOW_CREDENTIALS = True` in settings.py
   - Verify `withCredentials: true` in frontend API client

---

### 🔴 Issue: Categories Not Showing

**Symptoms:**
- Category filter is empty
- No category badges on articles

**Solutions:**

1. **Create Default Categories**
   ```bash
   cd backend
   python manage.py shell
   >>> from news.services import populate_sample_categories
   >>> populate_sample_categories()
   >>> exit()
   ```

2. **Fetch Articles with Categories**
   ```bash
   python manage.py fetch_news --category technology --max-articles 20
   python manage.py fetch_news --category politics --max-articles 20
   ```

---

### 🔴 Issue: Frontend Build Errors

**Symptoms:**
- `npm run dev` fails
- TypeScript errors
- Module not found errors

**Solutions:**

1. **Clean Install**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check Node Version**
   ```bash
   node --version  # Should be 20+
   npm --version   # Should be 10+
   ```

3. **Verify Dependencies**
   ```bash
   npm install react react-dom typescript @vitejs/plugin-react
   ```

---

### 🔴 Issue: Database Errors

**Symptoms:**
- "table doesn't exist" errors
- Migration errors
- Foreign key constraint errors

**Solutions:**

1. **Run Migrations**
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Reset Database** (⚠️ Deletes all data!)
   ```bash
   # Backup first if needed
   cd backend
   rm db.sqlite3
   python manage.py migrate
   python manage.py create_demo_user
   python manage.py fetch_news --max-articles 50
   ```

3. **Check Migration Status**
   ```bash
   python manage.py showmigrations
   ```

---

## Understanding the Architecture

### Why Frontend Shows Empty Even Though News API Works

**The architecture is:**
```
External News API (newsapi.org)
        ↓
Django Backend (fetches & stores in database)
        ↓
React Frontend (displays from database)
```

**Important:**
- Frontend NEVER calls newsapi.org directly
- Frontend ONLY calls Django backend at `localhost:8000/api`
- Django fetches from News API and stores in local database
- Frontend reads from local database

**This means:**
- Even if News API is working, if database is empty, frontend shows nothing
- You MUST fetch articles at least once to populate the database
- Use "Fetch Latest News" button or `python manage.py fetch_news`

See [API_ARCHITECTURE.md](./API_ARCHITECTURE.md) for detailed explanation.

---

## Quick Diagnostic Checklist

Use this to quickly diagnose issues:

### Backend Health Check
```bash
cd backend

# 1. Check virtual environment is activated
# (Should see (venv) in prompt)

# 2. Check Django server is running
# Should see output on http://127.0.0.1:8000/

# 3. Check database has articles
python manage.py shell -c "from news.models import NewsArticle; print(f'Articles: {NewsArticle.objects.count()}')"

# 4. Check environment variables
python manage.py shell -c "from django.conf import settings; print(f'NEWS_API_KEY: {settings.NEWS_API_KEY[:10]}...' if settings.NEWS_API_KEY else 'NOT SET'); print(f'OPENAI_API_KEY: {settings.OPENAI_API_KEY[:10]}...' if settings.OPENAI_API_KEY else 'NOT SET')"
```

### Frontend Health Check
```bash
cd frontend

# 1. Check server is running
# Should see output on http://localhost:5173

# 2. Open browser DevTools (F12)
# - Console: Check for errors
# - Network: Check API calls to localhost:8000
# - Application: Check cookies for sessionid and csrftoken

# 3. Test API connection
# In browser console:
fetch('http://localhost:8000/api/news/articles/')
  .then(r => r.json())
  .then(d => console.log('Articles:', d.length || d.results?.length || 0))
```

---

## Getting Help

If you're still stuck:

1. **Check Browser Console** (F12 → Console tab)
   - Look for red error messages
   - Note the exact error text

2. **Check Backend Terminal**
   - Look for error stack traces
   - Note the exact error and line numbers

3. **Check Network Tab** (F12 → Network tab)
   - Click on failed requests
   - Check "Response" tab for error details

4. **Verify Environment**
   ```bash
   # Backend
   cd backend
   python --version  # Should be 3.12+
   pip list          # Check installed packages
   
   # Frontend
   cd frontend
   node --version    # Should be 20+
   npm list          # Check installed packages
   ```

5. **Review Documentation**
   - [README.md](./README.md) - Setup instructions
   - [API_ARCHITECTURE.md](./API_ARCHITECTURE.md) - How the system works
   - [QUICKSTART.md](./QUICKSTART.md) - Quick setup guide

---

## Emergency Reset

If everything is broken and you want to start fresh:

```bash
# Backend reset
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py create_demo_user
python manage.py fetch_news --max-articles 50

# Frontend reset
cd frontend
rm -rf node_modules package-lock.json
npm install

# Restart both servers
# Terminal 1:
cd backend && python manage.py runserver

# Terminal 2:
cd frontend && npm run dev
```

Then open `http://localhost:5173` and login with `demo_user` / `demo123`.

