"""
updater.py — Opus Opportunity Tracker
Handles interactive user input for updating opportunity statuses and staff.

Input validation approach:
    All user input is validated before processing. This reflects the
    defensive programming principle that user input should never be
    trusted implicitly, as it is a primary source of runtime errors.
    (McConnell, 2004)
"""

from loader import VALID_STATUSES


def prompt_for_update(opportunity_index: dict) -> dict | None:
    """
    Interactively prompts the user to update an opportunity's status
    and/or assigned staff via console input.

    The opportunity index (dictionary) is used here for O(1) lookup
    of the target opportunity by ID, avoiding the need to iterate
    through the full list. (Cormen et al., 2022)

    Args:
        opportunity_index (dict): Dictionary of opportunity_id -> opportunity.

    Returns:
        dict: The updated opportunity if a valid update was made.
        None: If the user cancels or enters an invalid ID.
    """

    print("\n" + "-" * 50)
    opp_id = input("  Enter Opportunity ID to update (or 'cancel'): ").strip().upper()

    if opp_id.lower() == "cancel":
        print("  Update cancelled.")
        return None

    # Validate that the entered ID exists before proceeding
    if opp_id not in opportunity_index:
        print(f"  ✗ Opportunity ID '{opp_id}' not found. Please check the ID and try again.")
        return None

    opportunity = opportunity_index[opp_id]
    print(f"\n  Updating: [{opp_id}] {opportunity['name']}")
    print(f"  Current status : {opportunity['status']}")
    print(f"  Current staff  : {', '.join(opportunity['assigned_staff']) if opportunity['assigned_staff'] else 'None'}")

    # --- Status Update ---
    new_status = _get_valid_status()
    if new_status is None:
        return None

    # --- Staff Update ---
    new_staff = _get_updated_staff(opportunity["assigned_staff"])

    # Apply updates to the opportunity dictionary
    opportunity["status"] = new_status
    opportunity["assigned_staff"] = new_staff

    print(f"\n  ✓ [{opp_id}] updated successfully.")
    print(f"    New status : {new_status}")
    print(f"    New staff  : {', '.join(new_staff) if new_staff else 'None'}")

    return opportunity


def _get_valid_status() -> str | None:
    """
    Prompts the user for a valid status value and validates input.

    Uses the VALID_STATUSES tuple from loader.py as the source of truth
    for acceptable values, ensuring consistency across modules.

    Returns:
        str: A valid status string, or None if the user cancels.
    """

    valid_options = ", ".join(VALID_STATUSES)
    new_status = input(f"\n  Enter new status ({valid_options}) or 'cancel': ").strip().lower()

    if new_status == "cancel":
        print("  Update cancelled.")
        return None

    # Validate against the fixed tuple of accepted status values
    if new_status not in VALID_STATUSES:
        print(f"  ✗ Invalid status '{new_status}'. Must be one of: {valid_options}")
        return None

    return new_status


def _get_updated_staff(current_staff: list) -> list:
    """
    Prompts the user to update assigned staff for an opportunity.

    Staff names are entered as a pipe-separated string and split
    into a list, consistent with the input format used by loader.py.

    Args:
        current_staff (list): The current list of assigned staff.

    Returns:
        list: Updated list of staff names.
    """

    print(f"\n  Current staff: {', '.join(current_staff) if current_staff else 'None'}")
    staff_input = input(
        "  Enter updated staff (pipe-separated, e.g. Jane|Tom) or press Enter to keep current: "
    ).strip()

    if not staff_input:
        # User pressed Enter — keep existing staff unchanged
        return current_staff

    # Split and clean the new staff list
    new_staff = [name.strip() for name in staff_input.split("|") if name.strip()]

    return new_staff
