"""
loader.py — Opus Opportunity Tracker
Responsible for reading and parsing opportunity data from a CSV file.

Data structure decision:
    Each opportunity is stored as a dictionary, chosen for its O(1) key-based
    lookup performance. This is more efficient than a list (O(n) search) when
    retrieving specific opportunities by ID during validation and updates.
    (Cormen et al., 2022)
"""

import csv
import os


# Tuple used for valid status values — immutable by design, as these are
# fixed business rules that should not change at runtime. Tuples also offer
# slightly faster iteration than lists for fixed collections. (Lutz, 2013)
VALID_STATUSES = ("pipeline", "signed", "closed")


def load_opportunities(filepath: str) -> list:
    """
    Reads opportunity data from a CSV file and returns a list of dictionaries.

    Each row is parsed into a dictionary where required_roles and assigned_staff
    are converted to lists, allowing individual role and staff comparisons
    during validation.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        list: A list of opportunity dictionaries.

    Raises:
        FileNotFoundError: If the CSV file does not exist at the given path.
        ValueError: If the CSV file is empty or missing required headers.
    """

    # Defensive check before attempting to open — prevents a generic
    # FileNotFoundError from propagating without a clear message to the user
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Data file not found at '{filepath}'. "
            "Please ensure opportunities.csv exists in the data/ directory."
        )

    opportunities = []

    try:
        with open(filepath, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate that required headers are present before processing rows
            required_headers = {
                "opportunity_id", "name", "status",
                "budget", "required_roles", "assigned_staff"
            }

            if not required_headers.issubset(set(reader.fieldnames or [])):
                raise ValueError(
                    "CSV file is missing one or more required headers: "
                    f"{required_headers}"
                )

            for row in reader:
                opportunity = _parse_row(row)
                opportunities.append(opportunity)

    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")

    if not opportunities:
        raise ValueError(
            "No opportunities found in the CSV file. "
            "Please check the file contains data rows."
        )

    return opportunities


def _parse_row(row: dict) -> dict:
    """
    Parses a single CSV row into a structured opportunity dictionary.

    Pipe-separated values for roles and staff are split into lists,
    enabling individual comparison during staffing validation.
    Empty strings are normalised to empty lists for consistency.

    Args:
        row (dict): A raw row from the CSV DictReader.

    Returns:
        dict: A structured opportunity dictionary.
    """

    # Split pipe-separated roles and staff into lists.
    # Lists are used here (not sets) because order may matter for
    # role-to-staff mapping in future iterations, and duplicates
    # are meaningful (e.g. two developers required). (Lutz, 2013)
    required_roles = (
        [role.strip() for role in row["required_roles"].split("|")]
        if row["required_roles"].strip()
        else []
    )

    assigned_staff = (
        [staff.strip() for staff in row["assigned_staff"].split("|")]
        if row["assigned_staff"].strip()
        else []
    )

    # Budget is stored as a float where present, or None where missing.
    # None is preferred over 0 to distinguish "no budget set" from
    # "budget is zero" — an important distinction for validation logic.
    budget = None
    if row["budget"].strip():
        try:
            budget = float(row["budget"].strip())
        except ValueError:
            budget = None  # Non-numeric budget treated as missing

    return {
        "opportunity_id": row["opportunity_id"].strip(),
        "name": row["name"].strip(),
        "status": row["status"].strip().lower(),
        "budget": budget,
        "required_roles": required_roles,
        "assigned_staff": assigned_staff,
    }
