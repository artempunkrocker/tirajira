# Project overview

TiraJira - tool for automating mass task creation in Jira. It allows creating tasks from files with epic linking and logging support.

Key features:
- Creating tasks from JSON/YAML/CSV/XML/Excel files
- Support for linking tasks to epics
- Logging the task creation process
- Request rate limiting to prevent exceeding API limits
- Support for custom Jira fields

The project is written in Python 3.8+ and uses the official `jira` package to work with the API.

# Development setup

## Requirements
- Python 3.8+
- Poetry 1.2+
- Git 2.20+

Supported OS: Linux, macOS, Windows (WSL2)

## Installation
```bash
# Installing dependencies
poetry install

# Activating virtual environment
poetry shell
```

Main dependencies are defined in pyproject.toml.

# Code standards

## Formatting
- Formatting via Ruff (configured in pyproject.toml)
- Maximum line length: 88 characters
- Import sorting: isort

## Naming conventions
- Variables and functions: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Private elements: _private_attribute

## Documentation
- All public functions, classes and methods must have docstrings in Russian
- Following Google Python Style Guide format
- Complex logic should be commented

## Design patterns
- Using factories for object creation
- Applying strategy for algorithms
- Following SOLID, DRY, KISS principles

# Project structure

```
src/tirajira/
├── auth/               # Jira API authentication
├── commands/           # CLI commands
├── core/               # Core system components
├── file_loaders/       # Loaders for different file formats
├── integrations/       # Integrations with external systems
├── processing/         # Task processing and report generation
├── report_writers/     # Report generators
├── utils/              # Utility functions
├── exceptions.py           # Project-wide exceptions
├── logger.py               # Logging
└── main.py                 # Entry point
```

# Testing

## Framework
- pytest for testing
- coverage.py for measuring coverage
- Minimum coverage: 90% (see pyproject.toml)

## Best practices
- One assert per test
- Using mocks for external dependencies
- Using mocks when working with the file system
- Using mocks for console calls (print, logging, etc.)
- Tests follow the src/ structure
- All new functions must have tests

## Commands
```bash
# Running tests
pytest

# Checking coverage
pytest --cov=.

# Linting
ruff check .
```

## Testing Components with Timers

When testing components that use timers or time functions (`time.time()`, `time.sleep()`), it's important to properly mock them to ensure deterministic and fast test execution.

### Recommendations for mocking time functions

1. Always use mocks for `time.time()` and `time.sleep()` in tests for time-dependent components
2. Set `min_request_interval=0` in tests to eliminate artificial delays
3. Use `@patch("time.time")` and `@patch("time.sleep")` decorators to replace real functions

### Examples of proper mock usage

```python
# Proper mock usage for time.time()
@patch("time.time")
def test_rate_limiter_with_time_mock(self, mock_time):
    # Setting a fixed time value
    mock_time.return_value = 1000.0
    
    # Creating RateLimiter with minimum interval 0 for tests
    limiter = RateLimiter(min_request_interval=0)
    
    # Running the test
    result = limiter.process()
    
    # Checking the result
    self.assertIsNotNone(result)

# Proper mock usage for time.sleep()
@patch("time.sleep")
def test_rate_limiter_sleep_behavior(self, mock_sleep):
    # Creating RateLimiter with minimum interval 0 for tests
    limiter = RateLimiter(min_request_interval=0)
    
    # Running the test
    limiter.process()
    
    # Checking that sleep was not called
    mock_sleep.assert_not_called()
```

### Best practices

- Never use real time values in tests - always mock `time.time()`
- Set fixed values for time mocks for reproducible tests
- Use `min_request_interval=0` in tests for faster execution
- Check component behavior at different time values by changing mock return values
- Always check that mocks were called with the correct arguments

# Workflow

## Data flow
1. User runs command with file
2. main.py determines file type and creates loader
3. file_loader loads tasks
4. rate_limiter (from core/) controls request rate through jira_client (from integrations/)
5. task_creator (from processing/) collects results and saves reports
6. Results are logged

## Security

### Best practices
- Don't store credentials in code
- Use environment variables
- Don't commit .env files
- Don't write tokens to logs

## Performance

### Optimization
- Use generators to save memory
- Optimize packet size
- Minimize API calls
- Use caching