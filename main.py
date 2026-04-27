"""
main.py — Opus Opportunity Tracker
Entry point for the Opus application.

Opus is a command-line backend tool designed to manage the lifecycle of
commercial opportunities within a technology services organisation. It
validates opportunity and resourcing data, flags mismatches, and produces
an actionable pipeline report.

Architecture:
    Opus follows a modular single-responsibility design, where each module
    handles one concern: loading, validating, reporting, or updating data.
    This separation of concerns improves maintainability and testability,
    as individual modules can be tested and modified independently without
    affecting the rest of the system. (Bass, Clements and Kazman, 2021)

Usage:
    python main.py

Requirements:
    Python 3.10+
    No external dependencies required.
"""

from loader import load_opportunities
from validator import validate_opportunities, build_opportunity_index
from reporter import print_report, save_report
from updater import prompt_for_update


# Configuration stored as a tuple — immutable, as these paths are fixed
# application settings that should not be modified at runtime
CONFIG = (
    "data/opportunities.csv",   # Input file path
    "output/report.json",       # Output file path
)

DATA_FILE, OUTPUT_FILE = CONFIG


def main():
    """
    Main application loop for Opus.

    Orchestrates the full pipeline:
        1. Load opportunity data from CSV
        2. Validate all records against business rules
        3. Display and save the pipeline report
        4. Offer the user the option to update opportunity statuses
        5. Re-validate and regenerate the report after any updates
    """

    print("\n" + "=" * 50)
    print("         OPUS — Opportunity Tracker")
    print("         Version 1.0")
    print("=" * 50)

    # --- Step 1: Load Data ---
    print(f"\n  Loading opportunity data from '{DATA_FILE}'...")

    try:
        opportunities = load_opportunities(DATA_FILE)
        print(f"  ✓ {len(opportunities)} opportunities loaded successfully.\n")

    except FileNotFoundError as e:
        # Specific exception caught first — more informative than a general error
        print(f"\n  ✗ File error: {e}")
        print("  Opus cannot continue without data. Please check the file path.")
        return

    except ValueError as e:
        print(f"\n  ✗ Data error: {e}")
        print("  Please review the CSV file and try again.")
        return

    # --- Step 2: Validate ---
    healthy, flagged, all_staff = validate_opportunities(opportunities)

    # --- Step 3: Report ---
    print_report(healthy, flagged, all_staff)
    save_report(healthy, flagged, all_staff, OUTPUT_FILE)

    # --- Step 4: Interactive Update Loop ---
    # Build a dictionary index for O(1) opportunity lookup during updates
    opportunity_index = build_opportunity_index(opportunities)

    while True:
        update_choice = input("\n  Would you like to update an opportunity? (yes/no): ").strip().lower()

        if update_choice in ("no", "n"):
            print("\n  Exiting Opus. Goodbye.\n")
            break

        elif update_choice in ("yes", "y"):
            updated = prompt_for_update(opportunity_index)

            if updated:
                # Re-validate all opportunities after the update to reflect changes
                healthy, flagged, all_staff = validate_opportunities(opportunities)
                print_report(healthy, flagged, all_staff)
                save_report(healthy, flagged, all_staff, OUTPUT_FILE)

        else:
            # Handles unexpected input gracefully without crashing
            print("  Please enter 'yes' or 'no'.")


if __name__ == "__main__":
    main()
