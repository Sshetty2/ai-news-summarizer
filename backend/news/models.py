from django.db import models
from django.contrib.auth.models import User


class NewsSource(models.Model):
    """Model to store news sources"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class NewsCategory(models.Model):
    """Model to store news categories"""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "News Categories"

    def __str__(self):
        return self.name


class NewsArticle(models.Model):
    """Model to store news articles"""

    title = models.CharField(max_length=500)
    description = models.TextField()
    content = models.TextField(blank=True, null=True)  # Full article content
    url = models.URLField(unique=True)
    url_to_image = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=200, blank=True, null=True)
    source = models.ForeignKey(
        NewsSource, on_delete=models.CASCADE, related_name="articles"
    )
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Metadata
    language = models.CharField(max_length=10, default="en")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["category", "-published_at"]),
            models.Index(fields=["source", "-published_at"]),
        ]

    def __str__(self):
        return self.title[:100]


class UserReadArticle(models.Model):
    """Track which articles users have read"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="read_articles"
    )
    article = models.ForeignKey(
        NewsArticle, on_delete=models.CASCADE, related_name="readers"
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")

    def __str__(self):
        return f"{self.user.username} read {self.article.title[:50]}"
