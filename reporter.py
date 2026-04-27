"""
reporter.py — Opus Opportunity Tracker
Responsible for generating output — both to the console and as a JSON file.

Output format decision:
    JSON was chosen as the output format over CSV because it preserves
    nested data structures (lists of roles, lists of staff) without
    requiring additional parsing on read. JSON is also the standard
    interchange format for APIs and enterprise systems, making Opus
    output directly consumable by downstream tools. (Crockford, 2008)
"""

import json
import os
from datetime import datetime


def print_report(healthy: list, flagged: list, all_staff: set) -> None:
    """
    Prints a formatted validation report to the console.

    Args:
        healthy (list): Opportunities that passed all validation checks.
        flagged (list): Opportunities with one or more issues.
        all_staff (set): Unique set of all assigned staff across opportunities.
    """

    print("\n" + "=" * 50)
    print("       OPUS — Opportunity Pipeline Report")
    print("=" * 50)

    # --- Flagged Section ---
    if flagged:
        print(f"\n⚠  FLAGGED FOR ACTION ({len(flagged)} issue(s) found)\n")
        print("-" * 50)

        for opp in flagged:
            print(f"\n  [{opp['opportunity_id']}] {opp['name']}")
            print(f"  Status : {opp['status'].upper()}")
            print(f"  Budget : {'£' + str(opp['budget']) if opp['budget'] else 'NOT SET'}")
            print(f"  Roles  : {', '.join(opp['required_roles']) if opp['required_roles'] else 'None specified'}")
            print(f"  Staff  : {', '.join(opp['assigned_staff']) if opp['assigned_staff'] else 'UNASSIGNED'}")
            print(f"\n  Issues:")
            for issue in opp["flags"]:
                print(f"    → {issue}")
    else:
        print("\n✓  No issues found. All opportunities are healthy.")

    # --- Healthy Section ---
    print(f"\n\n✓  HEALTHY OPPORTUNITIES ({len(healthy)})\n")
    print("-" * 50)

    for opp in healthy:
        staff_display = ", ".join(opp["assigned_staff"]) if opp["assigned_staff"] else "—"
        print(f"  [{opp['opportunity_id']}] {opp['name']:<25} "
              f"[{opp['status'].upper()}]   Staff: {staff_display}")

    # --- Summary Section ---
    total = len(healthy) + len(flagged)
    signed_healthy = sum(1 for o in healthy if o["status"] == "signed")
    pipeline_count = sum(1 for o in healthy + flagged if o["status"] == "pipeline")
    closed_count = sum(1 for o in healthy + flagged if o["status"] == "closed")

    print(f"\n\n{'=' * 50}")
    print("  SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Total opportunities   : {total}")
    print(f"  Signed & healthy      : {signed_healthy}")
    print(f"  Flagged for action    : {len(flagged)}")
    print(f"  In pipeline           : {pipeline_count}")
    print(f"  Closed                : {closed_count}")
    print(f"  Unique staff deployed : {len(all_staff)}")
    print(f"{'=' * 50}\n")


def save_report(healthy: list, flagged: list, all_staff: set,
                output_path: str = "output/report.json") -> None:
    """
    Saves the validation report to a JSON file.

    The output directory is created if it does not already exist,
    ensuring the program does not crash on first run in a clean environment.

    Args:
        healthy (list): Opportunities that passed validation.
        flagged (list): Opportunities with issues.
        all_staff (set): Unique staff set — converted to list for JSON serialisation.
        output_path (str): File path for the JSON output.
    """

    # Ensure the output directory exists before writing
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    report_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": len(healthy) + len(flagged),
            "healthy": len(healthy),
            "flagged": len(flagged),
            "unique_staff_deployed": len(all_staff),
        },
        "flagged_opportunities": flagged,
        "healthy_opportunities": healthy,
        # Sets are not JSON serialisable — converted to sorted list for
        # deterministic output ordering across runs
        "all_assigned_staff": sorted(list(all_staff)),
    }

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)
        print(f"  ✓ Report saved to {output_path}")

    except IOError as e:
        print(f"  ✗ Failed to save report: {e}")
