from django.core.management.base import BaseCommand
from news.services import NewsAPIService


class Command(BaseCommand):
    help = "Fetches news articles from NewsAPI.org and stores them in the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            type=str,
            help="News category to fetch (general, business, technology, politics, etc.)",
            default=None,
        )
        parser.add_argument(
            "--max-articles",
            type=int,
            help="Maximum number of articles to fetch (default: 50)",
            default=50,
        )

    def handle(self, *args, **options):
        category = options["category"]
        max_articles = options["max_articles"]

        self.stdout.write(
            self.style.WARNING(f"Fetching up to {max_articles} articles...")
        )
        if category:
            self.stdout.write(f"Category: {category}")

        try:
            service = NewsAPIService()
            created_count = service.fetch_and_store_articles(
                category=category, max_articles=max_articles
            )

            if created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully fetched and stored {created_count} new articles!"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "No new articles were added (they might already exist in the database)"
                    )
                )

        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Configuration error: {e}"))
            self.stdout.write(
                self.style.WARNING(
                    "Please ensure NEWS_API_KEY is set in your .env file"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching articles: {e}"))
