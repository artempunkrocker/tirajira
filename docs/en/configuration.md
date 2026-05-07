# Jira Connection Setup

TiraJira supports two authentication modes depending on your Jira type:

| Jira Type | Authentication Mode | Environment Variables |
|----------|---------------------|------------------|
| Jira Cloud | Basic Auth | `JIRA_SERVER`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |
| Jira Server/Data Center | Personal Access Token | `JIRA_SERVER`, `JIRA_PAT_TOKEN` |

## Setup for Jira Cloud

1. Create a `.env` file in the working directory:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in the parameters:
   ```env
   JIRA_SERVER=https://your-company.atlassian.net
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=your-api-token-here
   ```

3. Obtaining an API token:
   - Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Copy the token and paste it in `.env`

## Setup for Jira Server/Data Center

1. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Fill in the parameters:
   ```env
   JIRA_SERVER=https://your-jira-server.company.com
   JIRA_PAT_TOKEN=your-personal-access-token-here
   ```

3. Obtaining a PAT:
   - In Jira go to "Profile" → "Personal Access Tokens"
   - Click "Create token"
   - Specify name and expiration date
   - Copy the token and paste it in `.env`

## Environment Variable Priority

⚠️ **Important:** The `JIRA_PAT_TOKEN` variable takes precedence over Basic Auth. If specified, PAT will be used.

## Connection Testing

After setting up the environment variables, you can test the connection by attempting to create one test task with the `--verbose` option:

```bash
tirajira import test_task.json --verbose
```

## Security

- Do not store credentials in code
- Use environment variables
- Do not commit .env files
- Do not write tokens to logs