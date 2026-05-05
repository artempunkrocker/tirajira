"""
Tests for the Jira API client interface.
"""

from abc import ABC
from typing import Any, Dict, List

import pytest

from tirajira.integrations.jira_client_interface import JiraClientInterface


def test_jira_client_interface_is_abstract():
    """Test: JiraClientInterface is an abstract class."""
    # Check that the class is abstract
    assert issubclass(JiraClientInterface, ABC)

    # Check that we cannot create an instance of the abstract class
    with pytest.raises(TypeError):
        JiraClientInterface()


def test_jira_client_interface_has_required_methods():
    """Test: JiraClientInterface has the required abstract methods."""
    # Get all abstract methods
    abstract_methods = getattr(JiraClientInterface, "__abstractmethods__", set())

    # Check that create_issue and link_to_epic methods exist
    assert "create_issue" in abstract_methods
    assert "link_to_epic" in abstract_methods
    # Check that new methods for working with task links exist
    assert "create_issue_link" in abstract_methods
    assert "get_issue_link_types" in abstract_methods


class ConcreteJiraClient(JiraClientInterface):
    """Concrete implementation for testing the interface."""

    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of the task creation method."""
        return {"success": True, "issue_key": "TEST-1"}

    def link_to_epic(self, issue_key: str, epic_key: str) -> Dict[str, Any]:
        """Implementation of the epic linking method."""
        return {"success": True}

    def create_issue_link(
        self, link_type: str, inward_issue: str, outward_issue: str
    ) -> Dict[str, Any]:
        """Implementation of the method for creating links between tasks."""
        return {"success": True}

    def get_issue_link_types(self) -> List[str]:
        """Implementation of the method for getting link types between tasks."""
        return ["Blocks", "Relates", "Duplicates"]


def test_concrete_implementation_can_be_instantiated():
    """Test: Concrete implementation of the interface can be instantiated."""
    # This should work without errors
    client = ConcreteJiraClient()
    assert isinstance(client, JiraClientInterface)

    # Check that methods can be called
    result = client.create_issue({"summary": "Test"})
    assert result["success"] is True
    assert result["issue_key"] == "TEST-1"

    result = client.link_to_epic("TEST-1", "EPIC-1")
    assert result["success"] is True

    result = client.create_issue_link("Blocks", "TEST-1", "TEST-2")
    assert result["success"] is True

    link_types = client.get_issue_link_types()
    assert isinstance(link_types, list)
    assert "Blocks" in link_types


def test_concrete_implementation_method_signatures():
    """Test: Concrete implementation has correct method signatures."""
    client = ConcreteJiraClient()

    # Check the signature of the create_issue method
    assert hasattr(client, "create_issue")
    assert callable(client.create_issue)

    # Check the signature of the link_to_epic method
    assert hasattr(client, "link_to_epic")
    assert callable(client.link_to_epic)

    # Check the signature of the create_issue_link method
    assert hasattr(client, "create_issue_link")
    assert callable(client.create_issue_link)

    # Check the signature of the get_issue_link_types method
    assert hasattr(client, "get_issue_link_types")
    assert callable(client.get_issue_link_types)


if __name__ == "__main__":
    pytest.main()
