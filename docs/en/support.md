# Support

If you have problems using TiraJira or need help, here are several ways to get support.

## Documentation

Before seeking help, please review the available documentation:

- [README](../README.md) - Basic project information
- [Installation](installation.md) - Detailed installation guide
- [Jira Connection Setup](configuration.md) - How to configure connection to Jira
- [File Formats](file_formats.md) - More about supported file formats
- [Commands](commands.md) - Complete description of all commands
- [Practical Examples](examples.md) - Usage examples
- [Supported Task Fields](fields.md) - How to work with various task fields
- [Troubleshooting](troubleshooting.md) - Solutions for common problems
- [Frequently Asked Questions](faq.md) - Answers to frequently asked questions
- [Report Format](reports.md) - How to work with reports
- [Contributing](contributing.md) - How to contribute to the project

## Getting Help

### Installation Issues

If you're having trouble installing TiraJira:

1. Make sure you have Python 3.10 or higher installed:
   ```bash
   python3 --version
   ```

2. Check if Poetry is installed:
   ```bash
   poetry --version
   ```

3. If errors occur when installing dependencies, try:
   ```bash
   pip3 install --upgrade pip
   pip3 install tirajira
   ```

### Jira Connection Issues

If TiraJira cannot connect to Jira:

1. Check that the Jira URL is correct in the configuration
2. Make sure the credentials are correct
3. Check that the user has permissions to create tasks
4. Make sure the API is available and not blocked by a firewall

### File Format Issues

If tasks are not being created due to file format problems:

1. Check that the file format matches the examples in the documentation
2. Make sure the file does not contain syntax errors
3. Try starting with a minimal example and gradually adding complexity
4. Use the `--verbose` flag to get detailed error information

## Troubleshooting

### Version Check

Check the installed version of TiraJira:
```bash
tirajira --version
```

### Verbose Logging

Use the `--verbose` flag to get detailed information:
```bash
tirajira import tasks.json --verbose
```

### Configuration Check

Make sure environment variables are set correctly:
```bash
# For Jira Cloud
echo $JIRA_SERVER
echo $JIRA_USER
echo $JIRA_API_TOKEN

# For Jira Server
echo $JIRA_SERVER
echo $JIRA_TOKEN
```

## Reporting Bugs

When reporting bugs, be sure to provide:

1. TiraJira version (`tirajira --version`)
2. Python version (`python3 --version`)
3. Operating system
4. Complete steps to reproduce the error
5. Task file (without confidential information)
6. Full error text
7. Execution logs (with `--verbose` flag if possible)

## Improvement Suggestions

We always welcome suggestions for improving TiraJira. If you have ideas:

1. Create an issue in GitHub with a description of the suggestion
2. Explain why this improvement is useful
3. If possible, describe how it can be implemented
4. Be prepared to discuss implementation details

Thank you for using TiraJira!