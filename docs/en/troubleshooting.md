# Troubleshooting Common Issues

## "Error creating issue: You must specify a summary of the issue"

**Cause:** Missing required `summary` field in the issue.

**Solution:** Ensure that each issue has a `summary` field with a non-empty value:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Issue title",  // ← Required field
  "issuetype": {"name": "Task"}
}
```

## "Error creating issue: Project key is required"

**Cause:** Missing or incorrect project key.

**Solution:** Check that each issue has a `project.key` field with an existing project key in Jira:

```json
{
  "project": {"key": "PROJ"},  // ← Check the project key in Jira
  "summary": "Issue title",
  "issuetype": {"name": "Task"}
}
```

## "Error creating issue: Issue type is required"

**Cause:** Missing or incorrect issue type.

**Solution:** Ensure that each issue specifies the issue type in the `issuetype.name` field:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Issue title",
  "issuetype": {"name": "Task"}  // ← Can be Task, Bug, Story, etc.
}
```

## "Authentication Error"

**Cause:** Incorrect Jira connection parameters.

**Solution:**
1. Check the correctness of the Jira server URL
2. Ensure that the email and API token are valid
3. For Jira Server, check that the PAT token is valid

```env
# For Jira Cloud
JIRA_SERVER=https://your-company.atlassian.net  # ← Check URL
JIRA_EMAIL=your-email@company.com               # ← Check email
JIRA_API_TOKEN=your-valid-api-token             # ← Check token

# For Jira Server
JIRA_SERVER=https://your-jira-server.company.com # ← Check URL
JIRA_PAT_TOKEN=your-valid-pat-token             # ← Check token
```

## "File not found"

**Cause:** Invalid path to the tasks file.

**Solution:** Check the correctness of the file path:

```bash
# Check that the file exists
ls -la tasks.json

# Use absolute or relative path
tirajira import ./tasks.json
tirajira import /full/path/to/tasks.json
```

## "Path outside allowed directory"

**Cause:** Attempt to access a file outside the current working directory (protection against directory traversal attacks).

**Solution:** Ensure that the tasks file is located in the current working directory or its subdirectories:

```bash
# Check the current directory
pwd

# Ensure that the file is in the current directory or its subdirectories
ls -la ./path/to/tasks.json

# Use relative path to the file
tirajira import ./tasks.json
tirajira import ./subdirectory/tasks.json
```

TiraJira implements protection against directory traversal attacks, blocking access to files outside the current working directory. This prevents the possibility of accessing system files or other files outside the working directory.

## "Connection refused" or "Timeout"

**Cause:** Network connectivity issues with Jira.

**Solution:**
1. Check Jira server availability in the browser
2. Ensure there are no network or VPN issues
3. Check firewall settings

## "Custom field not found"

**Cause:** Specified custom field ID does not exist.

**Solution:**
1. Check custom field IDs in Jira settings
2. Ensure you are using the correct format:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Issue with custom field",
  "issuetype": {"name": "Task"},
  "customfield_10001": "Field value"  // ← Check field ID
}
```

## "Insufficient permissions"

**Cause:** User does not have sufficient rights to create issues in the project.

**Solution:**
1. Check user permissions in Jira
2. Ensure the user can create issues in the specified project
3. Check that the issue type is allowed in the project

## "API rate limit exceeded"

**Cause:** Jira API limits exceeded.

**Solution:**
Use the new rate limiting control parameters:

1. Reduce the number of concurrent requests:
   ```bash
   tirajira import tasks.json --max-concurrent-requests 3
   ```

2. Increase the interval between requests:
   ```bash
   tirajira import tasks.json --min-request-interval 15.0
   ```

3. Use both parameters together for a more conservative approach:
   ```bash
   tirajira import tasks.json --max-concurrent-requests 3 --min-request-interval 15.0
   ```

For more information, see [Rate Limiting Documentation](rate_limiting.md).

## How to Enable Verbose Logging

To diagnose issues, enable verbose logging:

```bash
tirajira import tasks.json --verbose
```

This will help you understand at which stage the error occurs.