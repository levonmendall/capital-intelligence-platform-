"""Initialize the Capital Intelligence Platform."""

from core.database import initialize_database
from core.seed import seed_mandates


def main() -> None:
    """Initialize the database and configured mandates."""

    print("Initializing Capital Intelligence Platform...")

    initialize_database()
    mandate_count = seed_mandates()

    print(f"Platform initialized with {mandate_count} mandates.")


if __name__ == "__main__":
    main()
