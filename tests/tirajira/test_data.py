"""
Shared test data fixtures for TiraJira tests.
"""

COMMON_REPORT_DATA = {
    "metadata": {
        "generated_at": "2023-12-01T15:30:45",
        "source_file": "test.json",
        "total_tasks": 2,
        "successful_tasks": 1,
        "failed_tasks": 1,
    },
    "tasks": [
        {
            "id": 0,
            "status": "success",
            "issue_key": "PROJ-123",
            "issue_data": {"summary": "Test task"},
            "processed_at": "2023-12-01T15:30:45",
        },
        {
            "id": 1,
            "status": "failure",
            "error_message": "Connection error",
            "issue_data": {"summary": "Another task"},
            "processed_at": "2023-12-01T15:30:46",
        },
    ],
}
