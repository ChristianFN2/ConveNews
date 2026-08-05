from datetime import timedelta

from src.models.articles import ExtractedArticle
from src.utils.datetime_utils import utc_now, parse_datetime

def get_expired_articles(
        unfiltered_articles: list[ExtractedArticle], 
        expiry_days: int
    ) -> list[ExtractedArticle]:
    cutoff = utc_now() - timedelta(days=expiry_days)

    return [
        article
        for article in unfiltered_articles
        if parse_datetime(article.published) < cutoff
    ]