from src.runners.dev.newsletter.run_query_search import main as search_queries
from src.runners.dev.newsletter.run_article_selector import main as select_articles
from src.runners.dev.newsletter.run_relevance_evaluator import main as evaluate_relevance
from src.runners.dev.newsletter.run_newsletter_builder import main as build_newsletters

def main() -> None:
    search_queries()
    select_articles()
    evaluate_relevance()
    build_newsletters()

if __name__ == "__main__":
    main()