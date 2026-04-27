"""
test_validator.py — Opus Opportunity Tracker
Unit tests for validator.py using Python's built-in unittest framework.

Testing approach:
    Tests follow the Arrange → Act → Assert pattern, where each test
    sets up data, runs the function, and checks the result independently.
    Unit testing at the function level allows issues to be isolated and
    diagnosed quickly, without requiring the full application to run.
    (Sommerville, 2016)

    Tests cover:
        - Normal (expected) inputs
        - Edge cases (boundary conditions)
        - Invalid inputs (unexpected or malformed data)

Usage:
    python -m pytest tests/test_validator.py -v
    or
    python -m unittest tests/test_validator.py
"""

import unittest
import sys
import os

# Add parent directory to path so validator module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validator import validate_opportunities, build_opportunity_index, _validate_single


class TestValidateSingleOpportunity(unittest.TestCase):
    """Tests for the _validate_single function."""

    # --- Normal Cases ---

    def test_signed_fully_staffed_returns_no_issues(self):
        """A signed opportunity with budget and full staffing should pass."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP001",
            "name": "Project Alpha",
            "status": "signed",
            "budget": 50000.0,
            "required_roles": ["developer", "analyst"],
            "assigned_staff": ["Jane Smith", "Tom Brown"],
        }
        # Act
        issues = _validate_single(opportunity)
        # Assert
        self.assertEqual(issues, [], "Fully staffed signed opportunity should have no issues")

    def test_pipeline_opportunity_returns_no_issues(self):
        """A pipeline opportunity should not be subject to staffing rules."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP003",
            "name": "Project Gamma",
            "status": "pipeline",
            "budget": 75000.0,
            "required_roles": ["developer"],
            "assigned_staff": [],
        }
        # Act
        issues = _validate_single(opportunity)
        # Assert
        self.assertEqual(issues, [], "Pipeline opportunities should not be flagged for staffing")

    def test_closed_opportunity_returns_no_issues(self):
        """A closed opportunity should not trigger any validation rules."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP006",
            "name": "Project Zeta",
            "status": "closed",
            "budget": 45000.0,
            "required_roles": ["developer"],
            "assigned_staff": ["Alice Green"],
        }
        # Act
        issues = _validate_single(opportunity)
        # Assert
        self.assertEqual(issues, [], "Closed opportunities should not be flagged")

    # --- Edge Cases ---

    def test_signed_missing_budget_flagged(self):
        """A signed opportunity with no budget should be flagged."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP004",
            "name": "Project Delta",
            "status": "signed",
            "budget": None,
            "required_roles": ["analyst"],
            "assigned_staff": ["Sarah Jones"],
        }
        # Act
        issues = _validate_single(opportunity)
        # Assert
        self.assertTrue(len(issues) > 0, "Missing budget on signed opportunity should be flagged")
        self.assertTrue(any("budget" in issue.lower() for issue in issues))

    def test_signed_no_staff_flagged(self):
        """A signed opportunity with no assigned staff should be flagged."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP002",
            "name": "Project Beta",
            "status": "signed",
            "budget": 30000.0,
            "required_roles": ["developer"],
            "assigned_staff": [],
        }
        # Act
        issues = _validate_single(opportunity)
        # Assert
        self.assertTrue(len(issues) > 0, "Unstaffed signed opportunity should be flagged")
        self.assertTrue(any("staff" in issue.lower() for issue in issues))

    def test_signed_partially_staffed_flagged(self):
        """A signed opportunity where staff count is less than roles required."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP009",
            "name": "Project Iota",
            "status": "signed",
            "budget": 20000.0,
            "required_roles": ["developer", "analyst", "manager"],
            "assigned_staff": ["Jane Smith"],  # Only 1 of 3 roles filled
        }
        # Act
        issues = _validate_single(opportunity)
        # Assert
        self.assertTrue(len(issues) > 0, "Partially staffed opportunity should be flagged")
        self.assertTrue(any("partially" in issue.lower() for issue in issues))

    # --- Invalid Input Cases ---

    def test_invalid_status_flagged(self):
        """An unrecognised status value should be flagged immediately."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP008",
            "name": "Project Theta",
            "status": "invalid_status",
            "budget": 10000.0,
            "required_roles": ["developer"],
            "assigned_staff": ["Dan Grey"],
        }
        # Act
        issues = _validate_single(opportunity)
        # Assert
        self.assertTrue(len(issues) > 0, "Invalid status should be flagged")
        self.assertTrue(any("unrecognised" in issue.lower() for issue in issues))

    def test_signed_multiple_issues_all_flagged(self):
        """A signed opportunity missing both budget and staff should report both issues."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP010",
            "name": "Project Kappa",
            "status": "signed",
            "budget": None,
            "required_roles": ["developer"],
            "assigned_staff": [],
        }
        # Act
        issues = _validate_single(opportunity)
        # Assert
        self.assertEqual(len(issues), 2, "Should flag both missing budget and missing staff")


class TestValidateOpportunities(unittest.TestCase):
    """Tests for the validate_opportunities function."""

    def test_returns_correct_healthy_and_flagged_split(self):
        """validate_opportunities should correctly separate healthy and flagged records."""
        # Arrange
        opportunities = [
            {
                "opportunity_id": "OPP001",
                "name": "Healthy",
                "status": "signed",
                "budget": 50000.0,
                "required_roles": ["developer"],
                "assigned_staff": ["Jane"],
            },
            {
                "opportunity_id": "OPP002",
                "name": "Flagged",
                "status": "signed",
                "budget": None,
                "required_roles": ["developer"],
                "assigned_staff": [],
            },
        ]
        # Act
        healthy, flagged, _ = validate_opportunities(opportunities)
        # Assert
        self.assertEqual(len(healthy), 1)
        self.assertEqual(len(flagged), 1)

    def test_all_staff_set_contains_unique_names(self):
        """The all_staff set should contain unique names only."""
        # Arrange — same staff member appears in two opportunities
        opportunities = [
            {
                "opportunity_id": "OPP001",
                "name": "Alpha",
                "status": "signed",
                "budget": 50000.0,
                "required_roles": ["developer"],
                "assigned_staff": ["Jane"],
            },
            {
                "opportunity_id": "OPP002",
                "name": "Beta",
                "status": "pipeline",
                "budget": 30000.0,
                "required_roles": ["developer"],
                "assigned_staff": ["Jane"],  # Same person
            },
        ]
        # Act
        _, _, all_staff = validate_opportunities(opportunities)
        # Assert — set should deduplicate Jane
        self.assertEqual(len(all_staff), 1)
        self.assertIn("Jane", all_staff)


class TestBuildOpportunityIndex(unittest.TestCase):
    """Tests for the build_opportunity_index function."""

    def test_index_keys_match_opportunity_ids(self):
        """Index dictionary keys should match opportunity IDs."""
        # Arrange
        opportunities = [
            {"opportunity_id": "OPP001", "name": "Alpha", "status": "pipeline",
             "budget": None, "required_roles": [], "assigned_staff": []},
            {"opportunity_id": "OPP002", "name": "Beta", "status": "pipeline",
             "budget": None, "required_roles": [], "assigned_staff": []},
        ]
        # Act
        index = build_opportunity_index(opportunities)
        # Assert
        self.assertIn("OPP001", index)
        self.assertIn("OPP002", index)
        self.assertEqual(len(index), 2)

    def test_index_values_are_correct_opportunities(self):
        """Index values should map correctly to their opportunity dictionaries."""
        # Arrange
        opportunity = {
            "opportunity_id": "OPP001",
            "name": "Project Alpha",
            "status": "signed",
            "budget": 50000.0,
            "required_roles": ["developer"],
            "assigned_staff": ["Jane"],
        }
        # Act
        index = build_opportunity_index([opportunity])
        # Assert
        self.assertEqual(index["OPP001"]["name"], "Project Alpha")


if __name__ == "__main__":
    unittest.main(verbosity=2)
