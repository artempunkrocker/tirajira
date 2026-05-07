# Supported Issue Fields

## Standard Jira Fields

- `project.key` - project key (required)
- `summary` - issue summary (required)
- `description` - issue description
- `issuetype.name` - issue type (Task, Bug, Story, etc.)
- `assignee.emailAddress` - assignee email
- `priority.name` - priority (Highest, High, Medium, Low, Lowest)
- `labels` - labels (array for JSON/YAML, dots for CSV)
- `epic_key` - epic key (special TiraJira field, used for automatic linking of the issue to an epic after creation)
- `parent.key` - parent issue key (for subtasks)

## Custom Fields

You can use any custom fields from your Jira by specifying their ID:

- `customfield_10001`
- `customfield_10002`
- etc.

### Custom Field Formats

Different types of custom fields require different formats:

#### Text Fields
```json
"customfield_10001": "Text value"
```

#### Select Fields
```json
"customfield_10002": {"value": "Selected value"}
```

#### Multi-select Fields
```json
"customfield_10003": [{"value": "Value 1"}, {"value": "Value 2"}]
```

#### User Fields
```json
"customfield_10004": {"accountId": "user-account-id"}
```

#### Date Fields
```json
"customfield_10005": "2023-12-01"
```

## How to Find Field IDs

1. Go to "Jira Administration" → "Issues" → "Custom Fields"
2. Find the desired field and hover over it
3. The ID will be displayed in the URL or tooltip
4. Or use the Jira REST API: `GET /rest/api/2/field`

## Example Issue with All Field Types

```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "Issue with various fields",
    "description": "Complete example of using all field types",
    "issuetype": {"name": "Task"},
    "assignee": {"emailAddress": "user@company.com"},
    "priority": {"name": "High"},
    "epic_key": "PROJ-100",
    "labels": ["example", "documentation"],
    "customfield_10001": "Text value",
    "customfield_10002": {"value": "Selected value"},
    "customfield_10003": [{"value": "Value 1"}, {"value": "Value 2"}]
  }
]
```