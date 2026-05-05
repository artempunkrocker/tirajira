# TiraJira Commands

## Main Commands

### `import` - Task Creation

Creates tasks from a file:

```bash
# Basic usage
tirajira import tasks.json

# All formats are supported
tirajira import tasks.yaml
tirajira import tasks.csv
tirajira import tasks.xlsx
tirajira import tasks.xml
```

### `resume` - Resume Execution

Continues execution from a report, processing only failed tasks:

```bash
tirajira resume report.json
```

### `extract-failed` - Extract Failed Tasks

Extracts failed tasks from a report to a new file:

```bash
# Extract in JSON format
tirajira extract-failed report.json failed_tasks.json

# Extract in YAML format
tirajira extract-failed report.json failed_tasks.yaml

# Extract in CSV format
tirajira extract-failed report.json failed_tasks.csv
```

## Command Options

### Rate Limit Control

```bash
# Maximum concurrent requests to Jira API (default: 5)
--max-concurrent-requests N, -mcr N

# Minimum interval between requests in seconds (default: 10.0)
--min-request-interval SECONDS, -mri SECONDS

# Quota reset time on inactivity in seconds (default: 60.0)
--inactivity-reset-time SECONDS, -irt SECONDS
```

### Deprecated Batch Processing Options

The following options are deprecated and will be removed in future versions:

```bash
# Batch size (deprecated)
--batch-size N, -b N

# Delay between batches in seconds (deprecated)
--delay SECONDS, -d SECONDS
```

### Reports and Logging

```bash
# Save report (automatic filename)
--report

# Save report with specified name
--report report.json

# Verbose logging
--verbose, -v
```

### Error Handling

```bash
# Stop on first error
--stop-on-error
```

## Practical Examples

```bash
# Create tasks with verbose logging
tirajira import tasks.json --verbose

# Create tasks with rate limiting
tirajira import tasks.json --max-concurrent-requests 3 --min-request-interval 15.0

# Create tasks with stop-on-error and report saving
tirajira import tasks.json --stop-on-error --report

# Create tasks with Excel format report
tirajira import tasks.json --report report.xlsx

# Resume execution with rate limiting
tirajira resume report.json --max-concurrent-requests 3 --min-request-interval 15.0

# Resume execution with verbose logging
tirajira resume report.json --verbose

# Resume execution with stop-on-error
tirajira resume report.json --stop-on-error
```

## Getting Help

```bash
# Program version
tirajira --version

# Help for all commands
tirajira --help

# Help for specific command
tirajira import --help
tirajira resume --help
tirajira extract-failed --help
```