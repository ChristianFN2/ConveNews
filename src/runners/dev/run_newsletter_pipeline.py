from runners.dev.profile.run_profile_initializer import main as initialize_profile
from runners.dev.newsletter.run_newsletter_generator import main as generate_newsletter

def main() -> None:
    initialize_profile()
    generate_newsletter()

if __name__ == "__main__":
    main()