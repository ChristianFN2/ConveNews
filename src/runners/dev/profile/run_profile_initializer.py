from runners.dev.profile.run_interest_summarizer import main as summarize_interests
from runners.dev.profile.run_query_generator import main as generate_queries

def main() -> None:
    summarize_interests()
    generate_queries()

if __name__ == "__main__":
    main()