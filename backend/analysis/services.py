import json
import time
from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from .models import SentimentAnalysis
from news.models import NewsArticle
import logging

logger = logging.getLogger(__name__)


class OpenAIAnalysisService:
    """Service for AI-powered sentiment and political analysis using OpenAI"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured in settings")

    def get_analysis_prompt(
        self, article_title, article_description, article_content=None
    ):
        """Create comprehensive analysis prompt for OpenAI"""

        content_text = article_content or article_description

        prompt = f"""
        Please analyze the following news article for political bias, sentiment, and topical content:

        Title: {article_title}
        Description: {article_description}
        Content: {content_text[:3000]}  # Limit content length

        Provide a comprehensive analysis in the following JSON format:

        {{
            "political_bias": {{
                "classification": "far_left|left|center_left|center|center_right|right|far_right|neutral",
                "confidence_score": 0.85,
                "reasoning": "Detailed explanation of why this classification was chosen"
            }},
            "sentiment_analysis": {{
                "positive_sentiment": 0.25,
                "negative_sentiment": 0.15,
                "neutral_sentiment": 0.60,
                "overall_sentiment_score": 0.10,
                "emotional_tone": "cautious|optimistic|pessimistic|angry|neutral|concerned"
            }},
            "topic_analysis": {{
                "primary_topics": ["economy", "healthcare", "foreign_policy", "immigration", "climate"],
                "topic_distribution": {{
                    "economy": 0.40,
                    "healthcare": 0.30,
                    "immigration": 0.20,
                    "foreign_policy": 0.10
                }}
            }},
            "key_insights": {{
                "main_themes": ["economic recovery", "policy implications", "public reaction"],
                "controversy_level": 0.65,
                "key_phrases": ["significant development", "policy change", "public concern"],
                "target_audience": "general_public|political_insiders|industry_experts|activists"
            }},
            "detailed_analysis": {{
                "bias_indicators": ["word choice", "source selection", "framing"],
                "factual_vs_opinion": {{
                    "factual_content": 0.70,
                    "opinion_content": 0.30
                }},
                "rhetorical_devices": ["statistics", "expert quotes", "emotional appeals"],
                "missing_perspectives": ["opposition viewpoint", "expert analysis"]
            }}
        }}

        Rules:
        1. Be objective and analytical
        2. All numeric values should be between 0 and 1
        3. Sentiment percentages should sum to 1.0
        4. Classification must be one of the specified options
        5. Provide specific evidence for bias classification
        6. Focus on political and social implications
        """

        return prompt

    def analyze_article(self, article, user):
        """
        Analyze a news article using OpenAI and store results

        Args:
            article (NewsArticle): Article to analyze
            user (User): User requesting the analysis

        Returns:
            SentimentAnalysis: Created analysis object
        """
        start_time = time.time()

        try:
            # Get article content if available
            content = article.content or article.description

            # Create analysis prompt
            prompt = self.get_analysis_prompt(
                article.title, article.description, content
            )

            # Make OpenAI API call
            response = self.client.chat.completions.create(
                model="gpt-5-mini",  # Using gpt-5-mini for cost efficiency and performance
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert political analyst and sentiment analysis specialist. Provide objective, thorough analysis of news content focusing on political bias, sentiment, and topical categorization. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=2000,  # Sufficient for structured JSON analysis (~1500 tokens typical)
                response_format={"type": "json_object"},
                reasoning_effort="low",  # Balance quality and latency
                verbosity="low",  # Keep responses concise
            )

            # Parse response
            raw_response = response.choices[0].message.content
            analysis_data = json.loads(raw_response)

            # Extract data with fallbacks
            political_bias_data = analysis_data.get("political_bias", {})
            sentiment_data = analysis_data.get("sentiment_analysis", {})
            topic_data = analysis_data.get("topic_analysis", {})
            insights_data = analysis_data.get("key_insights", {})

            # Calculate processing time
            processing_time = time.time() - start_time

            # Create SentimentAnalysis object
            analysis = SentimentAnalysis.objects.create(
                user=user,
                article=article,
                # Political bias
                political_bias=political_bias_data.get("classification", "neutral"),
                bias_confidence_score=political_bias_data.get("confidence_score", 0.5),
                bias_reasoning=political_bias_data.get("reasoning", ""),
                # Sentiment metrics
                positive_sentiment=sentiment_data.get("positive_sentiment", 0.33),
                negative_sentiment=sentiment_data.get("negative_sentiment", 0.33),
                neutral_sentiment=sentiment_data.get("neutral_sentiment", 0.34),
                overall_sentiment_score=sentiment_data.get(
                    "overall_sentiment_score", 0.0
                ),
                # Topic analysis
                primary_topics=topic_data.get("primary_topics", []),
                topic_distribution=topic_data.get("topic_distribution", {}),
                # Key insights
                key_themes=insights_data.get("main_themes", []),
                emotional_tone=sentiment_data.get("emotional_tone", "neutral"),
                controversy_level=insights_data.get("controversy_level", 0.0),
                # Metadata
                processing_time_seconds=processing_time,
                raw_ai_response=analysis_data,
            )

            # Update user profile analysis count
            if hasattr(user, "profile"):
                profile = user.profile
                profile.total_analyses_created += 1
                profile.last_analysis_date = timezone.now()
                profile.save()

            logger.info(
                f"Created analysis for article '{article.title[:50]}' by user {user.username}"
            )
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            raise ValueError("Invalid JSON response from AI service")
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise

    def bulk_analyze_articles(self, articles, user, max_articles=10):
        """
        Analyze multiple articles in batch

        Args:
            articles (QuerySet): Articles to analyze
            user (User): User requesting the analysis
            max_articles (int): Maximum number of articles to analyze

        Returns:
            list: Created SentimentAnalysis objects
        """
        analyses = []
        processed = 0

        for article in articles[:max_articles]:
            try:
                # Skip if already analyzed by this user
                if SentimentAnalysis.objects.filter(
                    user=user, article=article
                ).exists():
                    continue

                analysis = self.analyze_article(article, user)
                analyses.append(analysis)
                processed += 1

                # Add delay to respect rate limits
                time.sleep(1)

            except Exception as e:
                logger.error(f"Failed to analyze article {article.id}: {e}")
                continue

        logger.info(f"Bulk analyzed {processed} articles for user {user.username}")
        return analyses

    def get_comparative_analysis(self, analyses):
        """
        Generate comparative insights from multiple analyses

        Args:
            analyses (QuerySet): SentimentAnalysis objects to compare

        Returns:
            dict: Comparative analysis results
        """
        if not analyses:
            return {}

        # Calculate averages and distributions
        bias_scores = [analysis.bias_score_normalized for analysis in analyses]
        sentiment_scores = [analysis.overall_sentiment_score for analysis in analyses]
        controversy_levels = [analysis.controversy_level for analysis in analyses]

        # Count bias classifications
        bias_distribution = {}
        for analysis in analyses:
            bias = analysis.political_bias
            bias_distribution[bias] = bias_distribution.get(bias, 0) + 1

        # Collect all topics
        all_topics = []
        for analysis in analyses:
            all_topics.extend(analysis.primary_topics)

        # Count topic frequencies
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return {
            "total_articles": len(analyses),
            "average_bias_score": (
                sum(bias_scores) / len(bias_scores) if bias_scores else 0
            ),
            "average_sentiment": (
                sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            ),
            "average_controversy": (
                sum(controversy_levels) / len(controversy_levels)
                if controversy_levels
                else 0
            ),
            "bias_distribution": bias_distribution,
            "top_topics": sorted(
                topic_counts.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "sentiment_range": {
                "min": min(sentiment_scores) if sentiment_scores else 0,
                "max": max(sentiment_scores) if sentiment_scores else 0,
            },
        }


def get_trending_topics(user=None, days=7):
    """Get trending topics from recent analyses"""
    from django.utils import timezone
    from datetime import timedelta

    since_date = timezone.now() - timedelta(days=days)

    # Get recent analyses
    analyses_query = SentimentAnalysis.objects.filter(created_at__gte=since_date)
    if user:
        analyses_query = analyses_query.filter(user=user)

    # Collect all topics
    all_topics = []
    for analysis in analyses_query:
        all_topics.extend(analysis.primary_topics)

    # Count and sort topics
    topic_counts = {}
    for topic in all_topics:
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    return sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
