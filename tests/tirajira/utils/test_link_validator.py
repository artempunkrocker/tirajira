"""
Tests for the LinkTypeValidator utility.
"""

import time
from unittest.mock import Mock, patch

from tirajira.utils.link_validator import LinkTypeValidator


class TestLinkTypeValidator:
    """Test suite for LinkTypeValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_jira_client = Mock()
        self.validator = LinkTypeValidator(self.mock_jira_client, cache_ttl=1)

    def test_init(self):
        """Test: LinkTypeValidator can be instantiated with required parameters."""
        assert isinstance(self.validator, LinkTypeValidator)
        assert self.validator.jira_client == self.mock_jira_client
        assert self.validator.cache_ttl == 1

    def test_is_valid_link_type_with_valid_type_from_jira(self):
        """Test: Valid link type from JIRA is recognized."""
        # Setup mock to return valid link types
        self.mock_jira_client.get_issue_link_types.return_value = ["Blocks", "Relates"]

        # Test valid link type
        assert self.validator.is_valid_link_type("Blocks") is True
        assert self.validator.is_valid_link_type("Relates") is True

    def test_is_valid_link_type_with_invalid_type_from_jira(self):
        """Test: Invalid link type from JIRA is rejected."""
        # Setup mock to return valid link types
        self.mock_jira_client.get_issue_link_types.return_value = ["Blocks", "Relates"]

        # Test invalid link type
        assert self.validator.is_valid_link_type("InvalidType") is False

    def test_is_valid_link_type_with_fallback_defaults(self):
        """Test: Valid link type from fallback defaults is recognized."""
        # Setup mock to raise exception (simulate JIRA API failure)
        self.mock_jira_client.get_issue_link_types.side_effect = Exception("API Error")

        # Test valid link type from defaults
        assert self.validator.is_valid_link_type("Blocks") is True
        assert self.validator.is_valid_link_type("Relates") is True
        assert self.validator.is_valid_link_type("Clones") is True

    def test_is_valid_link_type_with_invalid_type_from_defaults(self):
        """Test: Invalid link type from fallback defaults is rejected."""
        # Setup mock to raise exception (simulate JIRA API failure)
        self.mock_jira_client.get_issue_link_types.side_effect = Exception("API Error")

        # Test invalid link type
        assert self.validator.is_valid_link_type("InvalidType") is False

    def test_is_valid_link_type_caching(self):
        """Test: Link types are cached to avoid repeated API calls."""
        # Setup mock to return valid link types
        self.mock_jira_client.get_issue_link_types.return_value = ["Blocks"]

        # First call should hit the API
        assert self.validator.is_valid_link_type("Blocks") is True
        assert self.mock_jira_client.get_issue_link_types.call_count == 1

        # Second call within cache TTL should not hit the API again
        assert self.validator.is_valid_link_type("Blocks") is True
        assert self.mock_jira_client.get_issue_link_types.call_count == 1

    def test_is_valid_link_type_cache_expiration(self):
        """Test: Cache expires after TTL and refreshes from API."""
        # Setup mock to return valid link types
        self.mock_jira_client.get_issue_link_types.return_value = ["Blocks"]

        # First call should hit the API
        assert self.validator.is_valid_link_type("Blocks") is True
        assert self.mock_jira_client.get_issue_link_types.call_count == 1

        # Patch time to simulate cache expiration
        with patch("time.time", return_value=time.time() + 2):
            # This call should hit the API again due to expired cache
            assert self.validator.is_valid_link_type("Blocks") is True
            assert self.mock_jira_client.get_issue_link_types.call_count == 2

    def test_is_valid_link_type_empty_string(self):
        """Test: Empty string is rejected as invalid link type."""
        assert self.validator.is_valid_link_type("") is False

    def test_is_valid_link_type_none(self):
        """Test: None is rejected as invalid link type."""
        assert self.validator.is_valid_link_type(None) is False

    def test_get_valid_link_types_fallback_on_exception(self):
        """Test: Falls back to defaults when JIRA API raises exception."""
        # Setup mock to raise exception
        self.mock_jira_client.get_issue_link_types.side_effect = Exception("API Error")

        # Should return default link types
        valid_types = self.validator._get_valid_link_types()
        assert "Blocks" in valid_types
        assert "Relates" in valid_types
        assert "Clones" in valid_types

    def test_get_valid_link_types_empty_result_fallback(self):
        """Test: Falls back to defaults when JIRA API returns empty list."""
        # Setup mock to return empty list
        self.mock_jira_client.get_issue_link_types.return_value = []

        # Should return default link types
        valid_types = self.validator._get_valid_link_types()
        assert "Blocks" in valid_types
        assert "Relates" in valid_types
        assert "Clones" in valid_types
