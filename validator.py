"""
validator.py — Opus Opportunity Tracker
Responsible for validating opportunity data against defined business rules.

Defensive programming approach:
    Validation is performed proactively before data is processed, rather than
    relying solely on exception handling. This approach improves reliability
    and produces clearer, more actionable error messages. (McConnell, 2004)

Data structure decision:
    A set is used to track unique staff IDs across all opportunities.
    # Trade-off:
# Sets do not preserve order, unlike lists. However, ordering is not
# required in this context, making a set more suitable for enforcing
# uniqueness efficiently. (Cormen et al., 2022)
"""

from loader import VALID_STATUSES


def validate_opportunities(opportunities: list) -> tuple:
    """
    Validates all opportunities against business rules and returns
    two separate lists: healthy records and flagged records.

    Validation rules applied:
        1. Status must be a recognised value (pipeline, signed, closed)
        2. Signed opportunities must have a budget recorded
        3. Signed opportunities must have at least one staff member assigned
        4. Signed opportunities must not have fewer staff than required roles

    Args:
        opportunities (list): List of opportunity dictionaries from loader.py

    Returns:
        tuple: (healthy list, flagged list) where each flagged item
               includes a 'flags' key listing all issues found.
    """

    healthy = []
    flagged = []

    # Set used to collect unique staff names across all opportunities.
    # This provides an organisation-wide view of deployed staff,
    # which could support future capacity planning features.
    all_assigned_staff = set()

    for opportunity in opportunities:
        issues = _validate_single(opportunity)

        # Collect unique staff names — set automatically removes duplicates
        for staff_member in opportunity["assigned_staff"]:
            if staff_member:
                all_assigned_staff.add(staff_member)

        if issues:
            # Add flags to a copy of the opportunity dict so the original
            # data is not mutated — important for maintaining data integrity
            flagged_opportunity = dict(opportunity)
            flagged_opportunity["flags"] = issues
            flagged.append(flagged_opportunity)
        else:
            healthy.append(opportunity)

    return healthy, flagged, all_assigned_staff


def _validate_single(opportunity: dict) -> list:
    """
    Validates a single opportunity and returns a list of issue strings.
    Returns an empty list if the opportunity passes all checks.

    Checks are ordered from most to least critical, so that the most
    important issues appear first in the output report.

    Args:
        opportunity (dict): A single opportunity dictionary.

    Returns:
        list: A list of issue description strings. Empty if no issues found.
    """
# Defensive access prevents runtime crashes if fields are missing
    issues = []
    status = opportunity["status"]
    budget = opportunity["budget"]
    required_roles = opportunity["required_roles"]
    assigned_staff = opportunity["assigned_staff"]

    # Rule 1: Status must be a recognised value
    # Checked first as an invalid status means other rules may not apply
    if status not in VALID_STATUSES:
        issues.append(
            f"Unrecognised status '{status}'. "
            f"Expected one of: {', '.join(VALID_STATUSES)}"
        )
        return issues # Early return prevents further validation on unreliable data, improving both performance and accuracy of results

    # Rules 2-4 only apply to signed opportunities
    if status == "signed":

        # Rule 2: Signed opportunities must have a budget
        if budget is None:
            issues.append(
                "Signed opportunity is missing a budget. "
                "Financial approval cannot be confirmed."
            )

        # Rule 3: Signed opportunities must have at least one staff member
        if not assigned_staff:
            issues.append(
                "Signed opportunity has no assigned staff. "
                "Resourcing must be confirmed before delivery begins."
            )

        # Rule 4: Staff count must meet or exceed required role count
        elif len(assigned_staff) < len(required_roles):
            missing_count = len(required_roles) - len(assigned_staff)
            issues.append(
                f"Signed opportunity is partially staffed. "
                f"{missing_count} role(s) still require assignment: "
                f"{', '.join(required_roles[len(assigned_staff):])}"
            )

    return issues


def build_opportunity_index(opportunities: list) -> dict:
    """
    Builds a dictionary index of opportunities keyed by opportunity_id.

    A dictionary is used here specifically for O(1) lookup by ID,
    which is significantly more efficient than iterating through a list
    when updating or retrieving a specific opportunity. (Cormen et al., 2022)

    Args:
        opportunities (list): Full list of opportunity dictionaries.

    Returns:
        dict: Dictionary mapping opportunity_id -> opportunity dict.
    """

    # Dictionary comprehension for concise, readable index construction
    return {opp["opportunity_id"]: opp for opp in opportunities}
