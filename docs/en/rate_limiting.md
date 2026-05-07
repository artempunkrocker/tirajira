# Rate Limiting Management

TiraJira uses a rate limiting mechanism to prevent exceeding Jira API limits. This is especially important when creating tasks in bulk to avoid having your account or IP address blocked by the Jira server.

## Rate Limiting Approach

TiraJira implements a modular architecture for managing rate limiting, consisting of four main components:

1. **RateLimitController** - manages timing delays between requests
2. **TaskProcessor** - processes individual Jira tasks
3. **ConcurrencyManager** - manages concurrent task processing
4. **JiraClientInterface** - interface for interacting with Jira API

This architecture ensures clear separation of responsibilities between components, making it easier to test, extend, and maintain the rate limiting system. More information about the architecture can be found in [architecture documentation](architecture_refactor.md).

## Rate Limiting System Components

### RateLimitController

**Responsibility:** Managing the minimum interval between requests to Jira API.

This component ensures compliance with the minimum time interval between sequential requests to the Jira API. It uses a thread-safe lock to coordinate access to the last request time and waits when necessary before sending the next request.

**Usage example:**
```python
from tirajira.rate_limit_controller import RateLimitController

controller = RateLimitController(min_request_interval=2.0)
controller.wait_if_needed()  # Waits if necessary to maintain the interval
```

### TaskProcessor

**Responsibility:** Processing individual Jira tasks considering rate limits.

This component is responsible for creating tasks in the Jira API and linking them to epics when necessary. It interacts with RateLimitController to comply with time constraints between requests and provides detailed information about processing results for report generation.

**Usage example:**
```python
from tirajira.task_processor import TaskProcessor
from tirajira.rate_limit_controller import RateLimitController

processor = TaskProcessor(jira_client)
controller = RateLimitController(min_request_interval=1.0)

task_detail, success = processor.process_single_issue(
    issue_data, 0, controller
)
```

### ConcurrencyManager

**Responsibility:** Managing concurrent task processing with different error handling strategies.

This component manages concurrent task processing considering the maximum number of simultaneous requests. It supports two error handling strategies:
- Stop on first error (`stop_on_error=True`)
- Continue processing despite errors (`stop_on_error=False`)

**Usage example:**
```python
from tirajira.concurrency_manager import ConcurrencyManager

manager = ConcurrencyManager(
    max_concurrent_requests=5,
    verbose=True
)

successful_count, processing_details = manager.process(
    issues=issues_list,
    processor_func=process_func,
    stop_on_error=False
)
```

### JiraClientInterface

**Responsibility:** Abstract interface for interacting with Jira API.

This interface allows creating tasks and linking them to epics. It is used by all other components to interact with the Jira API, which simplifies testing and makes it easy to replace the implementation.

## Main Parameters

### max_concurrent_requests

Defines the maximum number of simultaneous requests to Jira API.

- **Purpose**: Control parallelism when creating tasks
- **Type**: Integer
- **Default**: 10

### min_request_interval

Specifies the minimum interval between sequential requests to Jira API in seconds.

- **Purpose**: Prevent exceeding request frequency
- **Type**: Floating point number (seconds)
- **Default**: 1.0

## Default Values and Justification

Conservative default values are chosen to minimize the risk of exceeding Jira API limits:

- `max_concurrent_requests: 10` - moderate level of parallelism that allows efficient task creation without excessive server load
- `min_request_interval: 1.0` - safe 1-second interval between requests to comply with most standard Jira API limits

These values ensure reliable operation in most Jira configurations without requiring additional configuration.

## Usage Examples

### Basic usage with default parameters

```bash
tirajira import tasks.json
```

### Reducing parallelism for sensitive systems

```bash
tirajira import tasks.json --max-concurrent-requests 3
```

### Increasing interval between requests

```bash
tirajira import tasks.json --min-request-interval 5.0
```

### Combined configuration for large imports

```bash
tirajira import large_tasks.json --max-concurrent-requests 5 --min-request-interval 2.0
```

### Configuration when resuming execution

```bash
tirajira resume report.json --max-concurrent-requests 3 --min-request-interval 5.0
```

## Configuration Recommendations

### For Jira Cloud

- Start with default parameters
- If "API rate limit exceeded" errors occur, reduce `max_concurrent_requests` or increase `min_request_interval`
- For large imports, it's recommended to use higher intervals

### For Jira Server/Data Center

- More aggressive settings can be used
- Check your server's internal rate limiting policies
- Experiment with increasing `max_concurrent_requests` for better performance

### General Recommendations

1. **Start with default values** - they are tested and safe
2. **Change one parameter at a time** - this will help determine optimal settings
3. **Use verbose mode (`--verbose`) for monitoring** - you'll be able to see how parameters affect performance
4. **Document successful configurations** - save commands that work well in your environment

## Troubleshooting

### "API rate limit exceeded"

This error indicates exceeding Jira API limits. Solutions:

1. Reduce the number of concurrent requests:
   ```bash
   tirajira import tasks.json --max-concurrent-requests 3
   ```

2. Increase the interval between requests:
   ```bash
   tirajira import tasks.json --min-request-interval 5.0
   ```

3. Use a combination of both approaches:
   ```bash
   tirajira import tasks.json --max-concurrent-requests 3 --min-request-interval 5.0
   ```

### Slow execution

If import is too slow:

1. Make sure you're not using overly conservative settings
2. Gradually increase `max_concurrent_requests` (up to 10-15)
3. Decrease `min_request_interval` (but no less than 0.5 seconds)
4. Monitor for errors when changing parameters

### Monitoring Recommendations

- Use the `--verbose` parameter to view detailed logs
- Pay attention to API error messages
- For large numbers of tasks, consider using reports to resume execution after errors

## Programmatic Usage

In addition to the command line, the rate limiting system can be used programmatically:

```python
from tirajira.rate_limiter import RateLimiter
from tirajira.jira_client import JiraClient

jira_client = JiraClient(...)  # Configure Jira connection
rate_limiter = RateLimiter(
    jira_client=jira_client,
    max_concurrent_requests=5,
    min_request_interval=2.0
)

issues = [
    {"project": {"key": "PROJ"}, "summary": "Task 1", "issuetype": {"name": "Task"}},
    {"project": {"key": "PROJ"}, "summary": "Task 2", "issuetype": {"name": "Task"}}
]

successful_count, processing_details = rate_limiter.process(issues)
```

For detailed information about the internal architecture of the rate limiting system, including component interaction diagrams and usage examples, see [architecture documentation](architecture_refactor.md).