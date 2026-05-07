# Practical Usage Examples

## Creating Simple Tasks

Create a file `simple_tasks.json`:

```json
[
  {
    "project": {"key": "MYPRJ"},
    "summary": "Set up system monitoring",
    "issuetype": {"name": "Task"}
  },
  {
    "project": {"key": "MYPRJ"},
    "summary": "Fix authorization error",
    "issuetype": {"name": "Bug"},
    "priority": {"name": "High"}
  }
]
```

Create tasks:

```bash
tirajira import simple_tasks.json
```

## Creating Tasks Linked to an Epic

```json
[
  {
    "project": {"key": "DEV"},
    "summary": "Implement data export function",
    "issuetype": {"name": "Story"},
    "epic_key": "DEV-123"
  }
]
```

## Creating Tasks for Different Assignees

```json
[
  {
    "project": {"key": "BACK"},
    "summary": "Optimize DB queries",
    "issuetype": {"name": "Task"},
    "assignee": {"emailAddress": "backend-dev@company.com"}
  },
  {
    "project": {"key": "FRONT"},
    "summary": "Fix form display",
    "issuetype": {"name": "Bug"},
    "assignee": {"emailAddress": "frontend-dev@company.com"}
  }
]
```

## Creating Tasks with Custom Fields

```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "Task with custom fields",
    "issuetype": {"name": "Task"},
    "customfield_10001": "High",
    "customfield_10002": "Backend"
  }
]
```

To find custom field IDs, open field settings in Jira or use the Jira API.

## Working with Reports

```bash
# Create tasks with report saving
tirajira import tasks.json --report

# Resume execution of failed tasks
tirajira resume tirajira_report_20231201_153045.json

# Extract failed tasks to a new file
tirajira extract-failed report.json failed_tasks.json
```

## Bulk Task Creation

For creating a large number of tasks, it's recommended to:

1. Split tasks into files of 50-100 items
2. Use rate limiting controls:

```bash
tirajira import large_tasks.json --max-concurrent-requests 5 --min-request-interval 2.0
```

## Creating Bugs

```json
[
  {
    "project": {"key": "QA"},
    "summary": "Fix authorization bug",
    "description": "Fix user authorization issue in mobile app",
    "issuetype": {"name": "Bug"},
    "assignee": {"emailAddress": "developer@company.com"},
    "priority": {"name": "Critical"},
    "epic_key": "QA-50",
    "labels": ["bug", "auth", "mobile"]
  }
]
```