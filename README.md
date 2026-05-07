# TiraJira - Jira Task Automation

[![PyPI Version](https://badge.fury.io/py/tirajira.svg)](https://badge.fury.io/py/tirajira)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Tired of manually creating dozens or hundreds of tasks in Jira?** TiraJira is your solution!

TiraJira is a powerful command-line utility for automating mass task creation in Jira. Just prepare tasks in a file (JSON, YAML, CSV, Excel or XML), and TiraJira will do the rest - create all your tasks in minutes instead of hours of manual work.

## Key Features

- 🚀 **Mass Task Creation** - create dozens and hundreds of tasks in one operation
- 📁 **Support for Different Formats** - use familiar formats JSON, YAML, CSV, Excel or XML
- 🔗 **Automatic Epic Linking** - link tasks to epics without additional actions
- 🔗 **Creating Links Between Tasks** - automatically create links between new and existing tasks
- ⚡ **Batch Processing** - optimized task submission for maximum performance
- 🛠️ **Full Custom Field Support** - use all your Jira fields, including custom ones
- 📊 **Detailed Logging** - track the task creation process in real time
- 🛑 **Error Stop Mode** - stop processing when errors occur (--stop-on-error)
- 📋 **Report Generation** - get machine-readable reports in JSON, CSV, Excel, YAML, XML formats
- 🔁 **Execution Resumption** - continue from where you left off when errors occur
- 🔒 **Protection Against Directory Traversal Attacks** - preventing access to files outside the working directory

## Quick Start

1. Install TiraJira:
   ```bash
   pip3 install tirajira
   ```

2. Prepare a task file in JSON format:
   ```json
   [
     {
       "project": {"key": "PROJ"},
       "summary": "First task",
       "description": "Description of the first task",
       "issuetype": {"name": "Task"}
     }
   ]
   ```

3. Create tasks in Jira:
   ```bash
   tirajira import tasks.json
   ```

Done! Your tasks are created in Jira.

## System Requirements

- Python 3.10 or higher
- Access to Jira Server
- API token for Jira access

## Documentation

- 🇺🇸 [English Documentation](docs/en/index.md)
- 🇷🇺 [Документация на русском языке](docs/ru/index.md)

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.