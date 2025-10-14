import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import NewsArticle, NewsSource, NewsCategory
import logging

logger = logging.getLogger(__name__)


class NewsAPIService:
    """Service for fetching news from NewsAPI.org"""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        if not self.api_key:
            raise ValueError("NEWS_API_KEY not configured in settings")

    def _make_request(self, endpoint, params):
        """Make HTTP request to NewsAPI"""
        params["apiKey"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request failed: {e}")
            raise

    def get_top_headlines(self, category=None, country="us", page_size=50):
        """Fetch top headlines from NewsAPI"""
        params = {"country": country, "pageSize": page_size, "page": 1}

        if category:
            params["category"] = category

        return self._make_request("top-headlines", params)

    def get_everything(
        self, query, from_date=None, sort_by="publishedAt", page_size=50
    ):
        """Search for articles with everything endpoint"""
        params = {
            "q": query,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": 1,
            "language": "en",
        }

        if from_date:
            params["from"] = from_date.isoformat()

        return self._make_request("everything", params)

    def fetch_and_store_articles(self, category=None, max_articles=100):
        """Fetch articles from NewsAPI and store them in database"""
        try:
            # Get top headlines
            response_data = self.get_top_headlines(
                category=category, page_size=max_articles
            )

            if response_data.get("status") != "ok":
                logger.error(
                    f"NewsAPI returned error: {response_data.get('message', 'Unknown error')}"
                )
                return 0

            articles_data = response_data.get("articles", [])
            created_count = 0

            # Create category if provided
            category_obj = None
            if category:
                category_obj, _ = NewsCategory.objects.get_or_create(
                    slug=category,
                    defaults={
                        "name": category.title(),
                        "description": f"News articles about {category}",
                    },
                )

            for article_data in articles_data:
                # Skip articles without required fields
                if not article_data.get("url") or not article_data.get("title"):
                    continue

                # Get or create news source
                source_name = article_data.get("source", {}).get(
                    "name", "Unknown Source"
                )
                source_obj, _ = NewsSource.objects.get_or_create(
                    name=source_name,
                    defaults={"description": f"News source: {source_name}"},
                )

                # Parse published date
                published_at = None
                if article_data.get("publishedAt"):
                    try:
                        published_at = datetime.fromisoformat(
                            article_data["publishedAt"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        published_at = timezone.now()
                else:
                    published_at = timezone.now()

                # Create or update article
                article, created = NewsArticle.objects.get_or_create(
                    url=article_data["url"],
                    defaults={
                        "title": article_data.get("title", "")[:500],
                        "description": article_data.get("description", "") or "",
                        "content": article_data.get("content", ""),
                        "url_to_image": article_data.get("urlToImage"),
                        "author": article_data.get("author"),
                        "source": source_obj,
                        "category": category_obj,
                        "published_at": published_at,
                    },
                )

                if created:
                    created_count += 1
                    logger.info(f"Created article: {article.title[:50]}")

            logger.info(f"Fetched and stored {created_count} new articles")
            return created_count

        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return 0

    def get_article_content(self, url):
        """
        Fetch full article content from URL.
        This is a basic implementation - in production, you might want to use
        a service like newspaper3k or readability-lxml for better content extraction.
        """
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            response.raise_for_status()

            # Basic content extraction (you might want to improve this)
            # For now, we'll just return the description as content
            # In a real implementation, you'd parse the HTML to extract article text
            return response.text[:5000]  # Truncate for storage

        except Exception as e:
            logger.error(f"Error fetching article content from {url}: {e}")
            return None


def populate_sample_categories():
    """Create sample news categories"""
    categories = [
        ("general", "General News", "General news and current events"),
        ("business", "Business", "Business and financial news"),
        ("technology", "Technology", "Technology and innovation news"),
        ("politics", "Politics", "Political news and analysis"),
        ("health", "Health", "Health and medical news"),
        ("science", "Science", "Science and research news"),
        ("sports", "Sports", "Sports news and updates"),
        ("entertainment", "Entertainment", "Entertainment and celebrity news"),
    ]

    created_count = 0
    for slug, name, description in categories:
        category, created = NewsCategory.objects.get_or_create(
            slug=slug, defaults={"name": name, "description": description}
        )
        if created:
            created_count += 1

    return created_count
