from django.contrib import admin
from .models import NewsArticle, NewsSource, NewsCategory, UserReadArticle


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "description"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "source",
        "category",
        "published_at",
        "is_active",
        "created_at",
    ]
    list_filter = ["source", "category", "is_active", "published_at"]
    search_fields = ["title", "description", "author"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "published_at"
    list_per_page = 25

    fieldsets = (
        (
            "Article Information",
            {
                "fields": (
                    "title",
                    "description",
                    "content",
                    "url",
                    "url_to_image",
                    "author",
                )
            },
        ),
        (
            "Classification",
            {"fields": ("source", "category", "language")},
        ),
        (
            "Status & Dates",
            {
                "fields": (
                    "is_active",
                    "published_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(UserReadArticle)
class UserReadArticleAdmin(admin.ModelAdmin):
    list_display = ["user", "article", "read_at"]
    list_filter = ["read_at"]
    search_fields = ["user__username", "article__title"]
    readonly_fields = ["read_at"]
    date_hierarchy = "read_at"
