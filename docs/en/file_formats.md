# Preparing Task Files

Create a file with tasks in any of the supported formats. Below are minimal examples for each format:

## Minimal Example (JSON)

Create a file `tasks.json`:

```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "My first task",
    "issuetype": {"name": "Task"}
  },
  {
    "project": {"key": "PROJ"},
    "summary": "Bug fix",
    "issuetype": {"name": "Bug"},
    "priority": {"name": "High"}
  }
]
```

## Extended Example (JSON)

```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "Setting up CI/CD",
    "description": "Set up continuous integration for the project",
    "issuetype": {"name": "Task"},
    "assignee": {"emailAddress": "developer@company.com"},
    "priority": {"name": "High"},
    "epic_key": "PROJ-100",
    "labels": ["devops", "ci-cd"],
    "customfield_10001": "Backend Team"
  }
]
```

## Examples of Other Formats

### YAML

```yaml
- project:
    key: PROJ
  summary: My first task
  issuetype:
    name: Task
- project:
    key: PROJ
  summary: Bug fix
  issuetype:
    name: Bug
  priority:
    name: High
```

### CSV

```csv
project.key,summary,issuetype.name
PROJ,My first task,Task
PROJ,Bug fix,Bug
```

### Excel

Create an Excel table with headers in the first row:
| project.key | summary | issuetype.name |
|-------------|---------|----------------|
| PROJ | My first task | Task |
| PROJ | Bug fix | Bug |

Ready examples are located in the `examples/` directory of the project.

## Required Fields

Each task must contain at least:
- `project.key` - project key in Jira
- `summary` - task name
- `issuetype.name` - task type (Task, Bug, Story, etc.)

## Useful Fields

- `description` - task description
- `assignee.emailAddress` - assignee email
- `priority.name` - priority (Highest, High, Medium, Low, Lowest)
- `epic_key` - epic key for automatic linking
- `labels` - array of labels (in JSON/YAML) or via dot notation in CSV
- Custom fields: `customfield_XXXXX` (where XXXXX is the field ID in Jira)

## Subtasks

To create subtasks, specify the parent task through the `parent.key` field:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Subtask",
  "issuetype": {"name": "Sub-task"},
  "parent": {"key": "PROJ-123"}
}
```

## Epic Linking

After creating a task, TiraJira automatically links it to an epic if the `epic_key` field is specified:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Task in epic",
  "issuetype": {"name": "Task"},
  "epic_key": "PROJ-100"  // ← Will be automatically linked to the epic
}
```

## Creating Links Between Tasks

TiraJira supports creating links between new and existing tasks using the `linking` field. This feature allows automatically creating various types of links between tasks after their creation.

### JSON

In JSON format, link information is specified in the `linking` field:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Task with link",
  "issuetype": {"name": "Task"},
  "linking": {
    "target_key": "PROJ-123",
    "link_type": "relates to"
  }
}
```

You can also specify multiple links:

```json
{
  "project": {"key": "PROJ"},
  "summary": "Task with multiple links",
  "issuetype": {"name": "Task"},
  "linking": [
    {
      "target_key": "PROJ-123",
      "link_type": "relates to"
    },
    {
      "target_key": "PROJ-456",
      "link_type": "blocks"
    }
  ]
}
```

### YAML

In YAML format, the structure is similar to JSON:

```yaml
project:
  key: PROJ
summary: Task with link
issuetype:
  name: Task
linking:
  target_key: PROJ-123
  link_type: relates to
```

Multiple links:

```yaml
project:
  key: PROJ
summary: Task with multiple links
issuetype:
  name: Task
linking:
  - target_key: PROJ-123
    link_type: relates to
  - target_key: PROJ-456
    link_type: blocks
```

### CSV

In CSV format, dot notation is used to specify link information:

```csv
project.key,summary,issuetype.name,linking.target_key,linking.link_type
PROJ,Task with link,Task,PROJ-123,relates to
```

For multiple links, indexing can be used:

```csv
project.key,summary,issuetype.name,linking.0.target_key,linking.0.link_type,linking.1.target_key,linking.1.link_type
PROJ,Task with multiple links,Task,PROJ-123,relates to,PROJ-456,blocks
```

### Excel

In Excel format, dot notation is also used in column headers:

| project.key | summary | issuetype.name | linking.target_key | linking.link_type |
|-------------|---------|----------------|--------------------|-------------------|
| PROJ | Task with link | Task | PROJ-123 | relates to |

For multiple links:

| project.key | summary | issuetype.name | linking.0.target_key | linking.0.link_type | linking.1.target_key | linking.1.link_type |
|-------------|---------|----------------|----------------------|---------------------|----------------------|---------------------|
| PROJ | Task with multiple links | Task | PROJ-123 | relates to | PROJ-456 | blocks |

### XML

In XML format, link information is specified inside the `linking` element:

```xml
<issue>
  <project>
    <key>PROJ</key>
  </project>
  <summary>Task with link</summary>
  <issuetype>
    <name>Task</name>
  </issuetype>
  <linking>
    <target_key>PROJ-123</target_key>
    <link_type>relates to</link_type>
  </linking>
</issue>
```

Multiple links:

```xml
<issue>
  <project>
    <key>PROJ</key>
  </project>
  <summary>Task with multiple links</summary>
  <issuetype>
    <name>Task</name>
  </issuetype>
  <linking>
    <link>
      <target_key>PROJ-123</target_key>
      <link_type>relates to</link_type>
    </link>
    <link>
      <target_key>PROJ-456</target_key>
      <link_type>blocks</link_type>
    </link>
  </linking>
</issue>
```

## Link Types and Validation

TiraJira automatically validates link types before creation. The application retrieves a list of valid link types from your Jira instance and compares them with those specified in the file. If connection to Jira is unavailable, a set of common link types is used:

- Blocks / Is Blocked By
- Relates / Is Related To
- Clones / Is Cloned By
- Duplicate / Is Duplicate Of
- Depends / Is Dependent On
- Parent / Child

If the specified link type is not found in the list of valid types, the link will not be created, but this will not cause an error in the entire task creation operation.