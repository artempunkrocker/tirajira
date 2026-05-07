# Frequently Asked Questions

## Can TiraJira be used with Jira Server and Jira Cloud?

Yes, TiraJira supports both types of Jira:
- **Jira Cloud** - via Basic Auth (email + API token)
- **Jira Server/Data Center** - via Personal Access Token

## What file formats are supported?

5 formats are supported:
- JSON (recommended for complex structures)
- YAML (human-readable format)
- CSV (simple tables)
- Excel (XLSX, for Office users)
- XML (for integrations)

## How to find custom field IDs in Jira?

1. Go to "Jira Administration" → "Issues" → "Custom Fields"
2. Find the required field and hover over it with your mouse
3. The ID will be displayed in the URL or tooltip
4. Or use the Jira REST API: `GET /rest/api/2/field`

## Can subtasks be created?

Yes, specify the parent task via the `parent.key` field:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Subtask",
  "issuetype": {"name": "Sub-task"},
  "parent": {"key": "PROJ-123"}
}
```

## How does epic linking work?

After creating a task, TiraJira automatically links it to an epic if the `epic_key` field is specified:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Task in epic",
  "issuetype": {"name": "Task"},
  "epic_key": "PROJ-100"  // ← Will be automatically linked to the epic
}
```

## Can existing tasks be updated?

In the current version, TiraJira only supports creating new tasks. To update existing tasks, use other tools or the Jira REST API directly.

## How to manage request rate limiting?

By default, a limit of 5 concurrent requests with a 10-second interval is used. Change the rate limiting parameters:

```bash
# Decrease the number of concurrent requests
tirajira import tasks.json --max-concurrent-requests 3

# Increase the interval between requests
tirajira import tasks.json --min-request-interval 15.0
```

⚠️ Too aggressive settings may lead to API errors when exceeding Jira limits.

## How to debug task creation problems?

1. Enable verbose logging:
   ```bash
   tirajira import tasks.json --verbose
   ```

2. Check that the file format matches the examples

3. Make sure all required fields are filled

4. Check project access rights in Jira

## Can TiraJira be used in automated scripts?

Yes, TiraJira is well-suited for automation. You can:
- Integrate it into CI/CD pipelines
- Use it in bash/python scripts
- Run it on schedule via cron
- Integrate with other systems through reports

## How are errors handled when creating tasks?

TiraJira by default continues processing even when individual tasks fail. You can:
- Use `--stop-on-error` to stop at the first error
- Review reports for error analysis
- Use the `resume` command to reprocess failed tasks
- Use the `extract-failed` command to extract failed tasks to a separate file

## Where are reports stored by default?

If the report filename is not explicitly specified, a JSON format with an automatically generated filename of the form `tirajira_report_YYYYMMDD_HHMMSS.json` is used.

## Can the report format be changed?

Yes, the report format is determined by the extension of the specified file:
- `.json` - JSON format
- `.csv` - CSV format
- `.xlsx` - Excel format
- `.yaml` - YAML format
- `.xml` - XML format

## What permissions does the Jira user need to work with TiraJira?

The user must have permissions to:
- Create tasks in specified projects
- View and edit used fields
- Create links with epics (if `epic_key` is used)
- Create subtasks (if subtasks are created)