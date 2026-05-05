"""
Tests for TaskCreator with reporting functionality.
"""

import os
from unittest.mock import Mock, mock_open, patch

import pytest

from tirajira import TaskCreator
from tirajira.exceptions import TaskCreatorError


class TestTaskCreatorIntegration:
    """Integration tests for TaskCreator."""

    @pytest.fixture
    def mock_loader(self):
        """Fixture for mocking file loader."""
        mock_loader = Mock()
        mock_loader.load_issues.return_value = [
            {"summary": "Test 1", "project": {"key": "PROJ"}},
            {"summary": "Test 2", "project": {"key": "PROJ"}},
        ]
        return mock_loader

    @pytest.fixture
    def mock_rate_limiter_success(self):
        """Fixture for mocking rate limiter with successful result."""
        mock_rate_limiter_instance = Mock()
        mock_rate_limiter_instance.process.return_value = (
            2,  # successful_count
            [
                {
                    "id": 0,
                    "status": "success",
                    "issue_key": "PROJ-123",
                    "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
                    "processed_at": "2023-12-01T15:30:45",
                },
                {
                    "id": 1,
                    "status": "success",
                    "issue_key": "PROJ-124",
                    "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
                    "processed_at": "2023-12-01T15:30:46",
                },
            ],
        )
        return mock_rate_limiter_instance

    @patch("tirajira.processing.task_creator.get_logger")
    @patch("tirajira.processing.report_generator.get_logger")
    @patch("tirajira.processing.task_creator.create_file_loader")
    @patch("tirajira.processing.task_creator.JiraClient")
    @patch("tirajira.processing.task_creator.RateLimiter")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    @patch("os.path.exists")
    def test_task_creator_create_from_file_integration(
        self,
        mock_exists,
        mock_file,
        mock_rate_limiter,
        mock_jira_client,
        mock_create_file_loader,
        mock_report_logger,
        mock_task_logger,
        mock_loader,
        mock_rate_limiter_success,
    ):
        """Test: integration task creation from file."""
        # Mock loggers so they don't output to console
        mock_task_logger_instance = Mock()
        mock_task_logger_instance.info = Mock()
        mock_task_logger_instance.success = Mock()
        mock_task_logger_instance.error = Mock()
        mock_task_logger.return_value = mock_task_logger_instance

        mock_report_logger_instance = Mock()
        mock_report_logger_instance.info = Mock()
        mock_report_logger_instance.success = Mock()
        mock_report_logger_instance.error = Mock()
        mock_report_logger.return_value = mock_report_logger_instance

        mock_exists.return_value = True
        mock_create_file_loader.return_value = mock_loader
        mock_rate_limiter.return_value = mock_rate_limiter_success

        task_creator = TaskCreator()

        with patch.dict(os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}):
            result = task_creator.create_from_file(
                file_path="test.json", report_file=True
            )

            assert result == 2

            mock_create_file_loader.assert_called_once()
            mock_loader.load_issues.assert_called_once_with("test.json")
            mock_rate_limiter_success.process.assert_called_once()

    @patch("tirajira.processing.task_creator.get_logger")
    @patch("tirajira.processing.report_generator.get_logger")
    @patch("tirajira.processing.task_creator.create_file_loader")
    @patch("tirajira.processing.task_creator.JiraClient")
    @patch("tirajira.processing.task_creator.RateLimiter")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "data"}')
    @patch("os.path.exists")
    @pytest.mark.parametrize(
        "report_file,should_generate_report",
        [
            (True, True),
            ("report.json", True),
            (None, False),
        ],
    )
    def test_task_creator_report_file_options(
        self,
        mock_exists,
        mock_file,
        mock_rate_limiter,
        mock_jira_client,
        mock_create_file_loader,
        mock_report_logger,
        mock_task_logger,
        mock_loader,
        mock_rate_limiter_success,
        report_file,
        should_generate_report,
    ):
        """Test: various report saving options."""
        from tirajira.processing.report_generator import ReportGenerator

        # Mock loggers so they don't output to console
        mock_task_logger_instance = Mock()
        mock_task_logger_instance.info = Mock()
        mock_task_logger_instance.success = Mock()
        mock_task_logger_instance.error = Mock()
        mock_task_logger.return_value = mock_task_logger_instance

        mock_report_logger_instance = Mock()
        mock_report_logger_instance.info = Mock()
        mock_report_logger_instance.success = Mock()
        mock_report_logger_instance.error = Mock()
        mock_report_logger.return_value = mock_report_logger_instance

        mock_exists.return_value = True
        mock_create_file_loader.return_value = mock_loader
        mock_rate_limiter.return_value = mock_rate_limiter_success

        with patch.object(ReportGenerator, "generate_report") as mock_generate_report:
            task_creator = TaskCreator()

            with patch.dict(os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}):
                result = task_creator.create_from_file(
                    file_path="test.json", report_file=report_file
                )

                assert result == 2

                if should_generate_report:
                    mock_generate_report.assert_called_once()
                else:
                    mock_generate_report.assert_not_called()

    @patch("tirajira.processing.task_creator.get_logger")
    @patch("tirajira.processing.task_creator.create_file_loader")
    @patch("tirajira.processing.task_creator.JiraClient")
    @patch("tirajira.processing.task_creator.RateLimiter")
    def test_task_creator_create_from_file_exception_handling(
        self, mock_rate_limiter, mock_jira_client, mock_create_file_loader, mock_logger
    ):
        """Test: exception handling in create_from_file."""
        # Mock logger so it doesn't output to console
        mock_logger_instance = Mock()
        mock_logger_instance.info = Mock()
        mock_logger_instance.success = Mock()
        mock_logger_instance.error = Mock()
        mock_logger.return_value = mock_logger_instance

        # Configure mock for file loader to throw an exception
        mock_create_file_loader.side_effect = Exception("Error loading file")

        # Create TaskCreator
        task_creator = TaskCreator()

        # Check that TaskCreatorError is raised when an exception occurs
        with pytest.raises(TaskCreatorError):
            task_creator.create_from_file("test.json")

    @patch("tirajira.processing.task_creator.get_logger")
    def test_task_creator_save_report_issue_urls_generation(self, mock_logger):
        """Test: issue URL generation in reports."""
        # Mock logger so it doesn't output to console
        mock_logger_instance = Mock()
        mock_logger_instance.info = Mock()
        mock_logger_instance.success = Mock()
        mock_logger_instance.error = Mock()
        mock_logger.return_value = mock_logger_instance

        # Create mocks
        mock_jira_client = Mock()
        mock_rate_limiter = Mock()

        # Create task creator
        task_creator = TaskCreator(
            jira_client=mock_jira_client,
            rate_limiter=mock_rate_limiter,
            verbose=False,
        )

        # Data for report with multiple issues
        processing_details = [
            {
                "id": 0,
                "status": "success",
                "issue_key": "PROJ-123",
                "issue_data": {"summary": "Test 1", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:45",
            },
            {
                "id": 1,
                "status": "success",
                "issue_key": "PROJ-124",
                "issue_data": {"summary": "Test 2", "project": {"key": "PROJ"}},
                "processed_at": "2023-12-01T15:30:46",
            },
        ]

        # Mock create_report_writer and open, but not generate_report
        # This will allow us to check that URLs are added to processing_details
        with patch("tirajira.processing.report_generator.create_report_writer"), patch(
            "builtins.open", mock_open()
        ), patch.dict(os.environ, {"JIRA_SERVER": "https://test.atlassian.net"}):
            # Call the report saving method
            task_creator._save_report(
                "tasks.json", processing_details, "report.json", 2, 2
            )

            # Check that issue_url is added to processing_details
            assert "issue_url" in processing_details[0]
            assert (
                processing_details[0]["issue_url"]
                == "https://test.atlassian.net/browse/PROJ-123"
            )
            assert "issue_url" in processing_details[1]
            assert (
                processing_details[1]["issue_url"]
                == "https://test.atlassian.net/browse/PROJ-124"
            )

    @patch("tirajira.processing.task_creator.get_logger")
    def test_transform_linking_to_issue_links_single_object(self, mock_logger):
        """Test: transformation of single linking object to IssueLink."""
        # Mock logger so it doesn't output to console
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        # Create task creator
        task_creator = TaskCreator()

        # Prepare issue data with empty linking list
        issues = [{"summary": "Test task", "project": {"key": "PROJ"}, "linking": []}]

        # Call the transformation method
        task_creator._transform_linking_to_issue_links(issues)

        # Check that linking is deleted but issue_links is not added
        assert "linking" not in issues[0]
        assert "issue_links" not in issues[0]

    @patch("tirajira.processing.task_creator.get_logger")
    def test_transform_linking_invalid_data_type(self, mock_logger):
        """Test: transformation of linking with invalid data type."""

        # Mock logger so it doesn't output to console
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        # Create task creator
        task_creator = TaskCreator()

        # Prepare issue data with invalid linking type
        issues = [
            {
                "summary": "Test task",
                "project": {"key": "PROJ"},
                "linking": "invalid_type",  # String instead of dictionary or list
            }
        ]

        # Call the transformation method
        task_creator._transform_linking_to_issue_links(issues)

        # Check that linking is deleted but issue_links is not added
        assert "linking" not in issues[0]
        assert "issue_links" not in issues[0]

    @patch("tirajira.processing.task_creator.get_logger")
    def test_transform_linking_to_issue_links_falsy_values(self, mock_logger):
        """Test: transformation of linking with falsy values."""

        # Mock logger so it doesn't output to console
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        # Create task creator
        task_creator = TaskCreator()

        # Prepare issue data with falsy values
        issues = [
            {
                "summary": "Test task",
                "project": {"key": "PROJ"},
                "linking": [
                    {
                        "target_key": "",  # Empty string
                        "link_type": "relates to",
                    },
                    {
                        "target_key": "PROJ-100",
                        "link_type": "",  # Empty string
                    },
                    {"target_key": "PROJ-101", "link_type": "blocks"},
                ],
            }
        ]

        # Call the transformation method
        task_creator._transform_linking_to_issue_links(issues)

        # Check that only complete objects are transformed
        assert "linking" not in issues[0]
        assert "issue_links" in issues[0]
        assert len(issues[0]["issue_links"]) == 1
        assert issues[0]["issue_links"][0].target_key == "PROJ-101"
        assert issues[0]["issue_links"][0].link_type == "blocks"
