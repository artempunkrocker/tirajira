# TiraJira - Jira Task Automation

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

## Installation

For regular users (recommended):
```bash
pip3 install tirajira
```

For developers:
```bash
git clone https://github.com/your-login/tirajira.git
cd tirajira
poetry install
```

[More about installation](installation.md)

## Jira Connection Setup

TiraJira supports two authentication modes:
- **Jira Cloud** - Basic Auth (email + API token)
- **Jira Server/Data Center** - Personal Access Token

[More about connection setup](configuration.md)

## Preparing a Task File

Supported formats: JSON, YAML, CSV, Excel, XML

Minimal example (JSON):
```json
[
  {
    "project": {"key": "PROJ"},
    "summary": "My first task",
    "issuetype": {"name": "Task"}
  }
]
```

[More about file formats](file_formats.md)

## Commands

- `import` - Create tasks from file
- `resume` - Resume execution from report
- `extract-failed` - Extract failed tasks from report

[More about commands](commands.md)

## Detailed Documentation

- [🔧 Installation and Setup](installation.md)
- [🔐 Jira Connection Setup](configuration.md)
- [📝 Preparing Task Files](file_formats.md)
- [🧰 Commands and Options](commands.md)
- [💡 Practical Examples](examples.md)
- [📋 Supported Task Fields](fields.md)
- [🛑 Request Rate Limiting Management](rate_limiting.md)
- [❓ Solving Common Problems](troubleshooting.md)
- [🤔 Frequently Asked Questions](faq.md)
- [📊 Report Format](reports.md)
- [👥 Contributing](contributing.md)
- [🆘 Support](support.md)
