"""
Tests for the IssueLink data structure.
"""

from tirajira.core.issue_link import IssueLink


def test_issue_link_creation_with_defaults():
    """Test: IssueLink can be instantiated with default values."""
    link = IssueLink()
    assert link.target_key is None
    assert link.link_type is None


def test_issue_link_creation_with_values():
    """Test: IssueLink can be instantiated with specific values."""
    link = IssueLink(target_key="PROJ-123", link_type="relates to")
    assert link.target_key == "PROJ-123"
    assert link.link_type == "relates to"


def test_issue_link_field_access():
    """Test: IssueLink fields can be accessed and modified."""
    link = IssueLink()
    link.target_key = "PROJ-456"
    link.link_type = "blocks"

    assert link.target_key == "PROJ-456"
    assert link.link_type == "blocks"
