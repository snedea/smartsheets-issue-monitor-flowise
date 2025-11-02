# SmartSheets Issue Monitor - Integration Guide

Complete step-by-step guide for importing and configuring the SmartSheets Issue Monitor workflow in Flowise.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Import Workflow](#import-workflow)
3. [Standard Tools Setup](#standard-tools-setup)
4. [Custom Tools Configuration](#custom-tools-configuration)
5. [SmartSheets API Integration](#smartsheets-api-integration)
6. [Data Storage Setup](#data-storage-setup)
7. [Notification Configuration](#notification-configuration)
8. [Testing & Validation](#testing--validation)
9. [Scheduling Setup](#scheduling-setup)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- **Flowise instance** (v1.4.0 or later)
  - Self-hosted: https://docs.flowiseai.com/getting-started
  - Cloud: https://flowiseai.com
- **SmartSheets account** with API access
- **Sheet ID** of your issue tracker
- **Node.js 18+** (for file system tools)

### Optional
- **Slack workspace** (for alert notifications)
- **GitHub account** (for automated scheduling via Actions)
- **AWS account** (for EventBridge scheduling)

---

## Import Workflow

### Step 1: Import JSON File

1. Open your Flowise instance
2. Navigate to **Workflows** (left sidebar)
3. Click **Import** button (top right)
4. Select `smartsheets-issue-monitor-flow.json`
5. Click **Import**

**Expected Result**:
- 10 nodes appear on canvas
- 1 green start node (SmartSheets Issue Monitor)
- 1 pink router node (Intent Router)
- 8 teal agent nodes (Agent.DataFetcher, Agent.ChangeDetector, etc.)
- All nodes connected with edges

### Step 2: Verify Import Success

**Visual Check**:
- ✅ All nodes visible and organized
- ✅ No validation errors shown
- ✅ Edge connections visible from router to all 8 agents

**Open each agent** (double-click):
- ✅ Model configuration visible (gpt-4o-mini)
- ✅ System message (persona) visible
- ✅ Tools section shows 2 items (currentDateTime, searXNG)
- ✅ Memory configuration visible

**Common Import Issues**:
- ❌ Blank tool fields: Expected - custom tools configured later
- ❌ "Tool not found": Standard tools need to be created (see next section)
- ❌ Disconnected node warning: Check that router has 8 output connections

---

## Standard Tools Setup

The workflow auto-includes 2 standard tools in EVERY agent. These tools must exist in your Flowise instance.

### Tool 1: currentDateTime

**Purpose**: Provides current date and time for temporal awareness.

**Create in Flowise**:
1. Go to **Tools** → **Custom Tools** → **Add Tool**
2. Configuration:
   - **Name**: `currentDateTime`
   - **Description**: "Returns current date and time in ISO format"
   - **Type**: JavaScript function
   - **Code**:
     ```javascript
     return {
       currentDateTime: new Date().toISOString(),
       timestamp: Date.now(),
       date: new Date().toDateString(),
       time: new Date().toTimeString()
     };
     ```
3. Click **Save**

**Test**:
```javascript
// Expected output:
{
  "currentDateTime": "2025-01-14T12:30:00.000Z",
  "timestamp": 1705235400000,
  "date": "Fri Jan 14 2025",
  "time": "12:30:00 GMT+0000 (UTC)"
}
```

### Tool 2: searXNG

**Purpose**: Federated web search for real-time information and context.

**Create in Flowise**:
1. Go to **Tools** → **Custom Tools** → **Add Tool**
2. Configuration:
   - **Name**: `searXNG`
   - **Description**: "Federated web/meta search. Use when you need fresh facts or sources."
   - **Type**: HTTP API
   - **Method**: GET
   - **Base URL**: `https://s.llam.ai`
   - **Endpoint**: `/search`
   - **Parameters**:
     * `q` (string, required): Natural language search query
     * `format` (string, optional, default: "json"): Response format
     * `language` (string, optional, default: "en"): Language code
     * `pageno` (number, optional, default: 1): Page number
3. Click **Save**

**Test**:
```
Query: "SmartSheets API rate limits"
Expected: JSON array of search results with titles, URLs, content excerpts
```

---

## Custom Tools Configuration

These tools are specific to SmartSheets monitoring and must be created manually.

### Tool 3: smartsheets-api

**Purpose**: Fetch data from SmartSheets REST API v2.0.

**Prerequisites**:
- SmartSheets OAuth 2.0 app OR API token
- Sheet ID of your issue tracker

**Create in Flowise**:
1. Go to **Tools** → **Custom Tools** → **Add Tool**
2. Configuration:
   - **Name**: `smartsheets-api`
   - **Description**: "Fetch SmartSheets data with OAuth authentication and pagination"
   - **Type**: HTTP API
   - **Method**: GET
   - **Base URL**: `https://api.smartsheet.com/2.0`
   - **Authentication**: Bearer Token
     * Add credential: SmartSheets API token
   - **Endpoints**:
     * `/sheets/{sheetId}` - Get full sheet
     * `/sheets/{sheetId}/rows` - Get rows with pagination
     * `/sheets/{sheetId}/columns` - Get column metadata

3. **Rate Limiting Configuration**:
   - Add custom header: `X-RateLimit-Limit: 300`
   - Implement exponential backoff (retry after 429 response)
   - Page size: 100 rows per request

4. Click **Save**

**OAuth 2.0 Setup** (Alternative to API token):
1. Create app: https://developers.smartsheet.com/
2. Get Client ID and Client Secret
3. Redirect URI: `https://your-flowise-instance.com/oauth/callback`
4. Add OAuth credential in Flowise
5. Configure tool to use OAuth credential

**Test**:
```
GET /sheets/{your-sheet-id}
Expected: JSON with sheet metadata, columns array, rows array
```

### Tool 4: file-system-read

**Purpose**: Read previous snapshots and metrics from data/ directory.

**Create in Flowise**:
1. Create Node.js custom tool:
   ```javascript
   // file-system-read.js
   const fs = require('fs').promises;
   const path = require('path');

   async function readFile(filePath) {
     try {
       const fullPath = path.join(__dirname, '../data', filePath);
       const content = await fs.readFile(fullPath, 'utf-8');
       return JSON.parse(content);
     } catch (error) {
       if (error.code === 'ENOENT') {
         return { error: 'File not found', path: filePath };
       }
       throw error;
     }
   }

   module.exports = { run: readFile };
   ```

2. Add to Flowise:
   - **Name**: `file-system-read`
   - **Description**: "Read JSON snapshots and metrics from data/ directory"
   - **Type**: Custom Node.js
   - **Input**: `filePath` (string)
   - **Output**: JSON object

### Tool 5: file-system-write

**Purpose**: Write snapshots, reports, and metrics to data/ directory.

**Create in Flowise**:
1. Create Node.js custom tool:
   ```javascript
   // file-system-write.js
   const fs = require('fs').promises;
   const path = require('path');

   async function writeFile({ filePath, content, format = 'json' }) {
     const fullPath = path.join(__dirname, '../data', filePath);
     const dir = path.dirname(fullPath);

     // Ensure directory exists
     await fs.mkdir(dir, { recursive: true });

     if (format === 'json') {
       await fs.writeFile(fullPath, JSON.stringify(content, null, 2));
     } else {
       await fs.writeFile(fullPath, content);
     }

     return { success: true, path: filePath };
   }

   module.exports = { run: writeFile };
   ```

2. Add to Flowise:
   - **Name**: `file-system-write`
   - **Description**: "Write snapshots, reports, and metrics to data/ directory"
   - **Type**: Custom Node.js
   - **Inputs**: `filePath` (string), `content` (any), `format` (string)
   - **Output**: Success status

### Tool 6: notification-webhook

**Purpose**: Send alerts to Slack or email.

**Create in Flowise** (Slack example):
1. Get Slack webhook URL:
   - Go to https://api.slack.com/apps
   - Create app → Incoming Webhooks
   - Add webhook to channel
   - Copy webhook URL

2. Configure in Flowise:
   - **Name**: `notification-webhook`
   - **Description**: "Send alerts to Slack channel"
   - **Type**: HTTP API
   - **Method**: POST
   - **URL**: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
   - **Body Template**:
     ```json
     {
       "text": "🚨 {{alertType}}: {{message}}",
       "blocks": [
         {
           "type": "section",
           "text": {
             "type": "mrkdwn",
             "text": "*{{alertType}}*\n{{message}}"
           }
         },
         {
           "type": "context",
           "elements": [
             {
               "type": "mrkdwn",
               "text": "Source: SmartSheets Issue Monitor | {{timestamp}}"
             }
           ]
         }
       ]
     }
     ```
   - **Requires Human Input**: true (for critical alerts)

### Tools 7-9: Analytics Tools

**frequency-calculator**, **transition-analyzer**, **trend-calculator**

These are optional statistical analysis tools. Can be implemented as:
- Python scripts called via HTTP API
- JavaScript functions in Flowise
- External analytics service integration

**Example: frequency-calculator (Python)**:
```python
from flask import Flask, request, jsonify
from collections import Counter
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/calculate-frequency', methods=['POST'])
def calculate_frequency():
    data = request.json
    issue_id = data['issue_id']
    updates = data['updates']  # List of update timestamps

    # Calculate frequency in last 24h
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    recent_updates = [u for u in updates if datetime.fromisoformat(u) > yesterday]

    velocity = len(recent_updates) / 1  # updates per day
    is_hot = len(recent_updates) > 3

    return jsonify({
        'issue_id': issue_id,
        'total_updates': len(updates),
        'updates_24h': len(recent_updates),
        'velocity': velocity,
        'is_hot': is_hot
    })

if __name__ == '__main__':
    app.run(port=5001)
```

Deploy as microservice and add HTTP API tool pointing to `http://localhost:5001/calculate-frequency`.

---

## SmartSheets API Integration

### Step 1: Get API Credentials

**Option A: API Token** (Simpler):
1. Go to SmartSheets Account
2. **Personal Settings** → **API Access**
3. **Generate new access token**
4. Copy token (save securely - shown only once)

**Option B: OAuth 2.0** (Recommended for production):
1. Go to https://developers.smartsheet.com/
2. **Create app** → Enter app details
3. Note **Client ID** and **Client Secret**
4. Set **Redirect URI**: `https://your-flowise.com/oauth/callback`

### Step 2: Find Sheet ID

1. Open your issue tracker sheet in SmartSheets
2. Look at URL: `https://app.smartsheet.com/sheets/XXXXXXXXX`
3. `XXXXXXXXX` is your Sheet ID
4. Copy Sheet ID for tool configuration

### Step 3: Test API Access

```bash
# Using API token
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     "https://api.smartsheet.com/2.0/sheets/YOUR_SHEET_ID"

# Expected: JSON response with sheet data
```

### Step 4: Configure Credential in Flowise

1. Go to **Credentials** → **Add Credential**
2. **Type**: Bearer Token (or OAuth 2.0)
3. **Name**: `SmartSheets API`
4. **Token**: Paste your API token
5. Click **Save**

### Step 5: Assign Credential to Tool

1. Go to **Tools** → Find `smartsheets-api`
2. **Edit** → **Authentication** section
3. **Select credential**: SmartSheets API
4. Click **Save**

---

## Data Storage Setup

### Directory Structure

Create data directories for snapshots, reports, and metrics:

```bash
mkdir -p data/snapshots
mkdir -p data/reports
mkdir -p data/metrics
```

**Permissions**:
```bash
chmod 755 data
chmod 755 data/snapshots data/reports data/metrics
```

### Snapshot Format

**File naming**: `smartsheet-{timestamp}.json`

**Example**: `data/snapshots/smartsheet-2025-01-14-06-00.json`

```json
{
  "timestamp": "2025-01-14T06:00:00Z",
  "sheetId": "12345678",
  "sheetName": "Issue Tracker",
  "totalRows": 245,
  "rows": [
    {
      "issueId": "ABC123",
      "title": "Fix login bug",
      "status": "In Progress",
      "assignee": "john@example.com",
      "priority": "High",
      "createdDate": "2025-01-10",
      "updatedDate": "2025-01-14T05:30:00Z",
      "updatedBy": "jane@example.com"
    }
  ],
  "columnMetadata": {
    "status": ["New", "In Progress", "Blocked", "Resolved", "Closed"],
    "priority": ["High", "Medium", "Low"]
  }
}
```

### Report Format

**File naming**: `daily-report-{date}.md`

**Example**: `data/reports/daily-report-2025-01-14.md`

```markdown
# SmartSheets Issue Monitor - Daily Report
**Date**: January 14, 2025 06:00 UTC
**Period**: Last 24 hours

## Executive Summary
5 new issues created, 8 issues resolved. 3 issues are "heating up" with frequent updates. No critical alerts.

## New Issues (5)
- **ABC123**: Fix login bug (Priority: High, Assigned: john@example.com)
- **ABC124**: Update documentation (Priority: Medium, Assigned: jane@example.com)
...

## Resolved Issues (8)
- **XYZ789**: Performance improvement (Resolved by: alice@example.com)
...

## Top 5 Heating Up Issues
1. **ABC125**: 6 updates in 24h (Status changed 3 times: New→InProgress→Blocked→InProgress)
...

## Status Transitions
- New → InProgress: 7 transitions
- InProgress → Resolved: 8 transitions
- Resolved → Closed: 5 transitions

## Most Active Contributors
1. jane@example.com: 12 updates
2. john@example.com: 8 updates
...

## Blocked/Stalled Issues (2)
- **DEF456**: Blocked for 5 days (Priority: High)
- **GHI789**: No updates in 9 days (Status: InProgress)
```

---

## Notification Configuration

### Slack Integration

See Tool 6: notification-webhook above for Slack webhook setup.

**Alert Types**:
- 🔥 **Hot Issue**: >3 updates in 24h
- 🚫 **Blocked**: Status=Blocked for >3 days
- ⏸️ **Stalled**: No updates in >7 days + Status=InProgress
- ⚠️ **High Priority No Activity**: Priority=High + no updates in >3 days

**Alert Throttling**:
- Agent.AlertManager uses window size = 5 memory
- Prevents duplicate alerts for same issue within 24h

### Email Integration (Alternative)

Use SMTP webhook tool:
1. Configure SMTP server details
2. Create email template
3. Add as alternative to Slack webhook

---

## Testing & Validation

### Test 1: Standard Tools

**Query each agent individually**:
```
Agent.DataFetcher: "What's the current time?"
Expected: Uses currentDateTime tool, returns ISO timestamp
```

```
Agent.TrendAnalyzer: "Search for normal issue resolution velocity"
Expected: Uses searXNG tool, returns search results
```

### Test 2: SmartSheets API

**Trigger Data Fetcher**:
```
Query: "Fetch latest SmartSheets data"
Expected:
- Agent calls smartsheets-api tool
- Returns JSON snapshot
- Saves to data/snapshots/
```

### Test 3: Change Detection

**Run twice with different data**:
```
First run: "Fetch latest data"
Second run: "What changed since last check?"
Expected:
- Agent compares snapshots
- Reports deltas (new issues, status changes, etc.)
```

### Test 4: Intent Routing

**Test all routing scenarios**:
```
"Generate daily report" → Agent.ReportGenerator ✓
"Show hot issues" → Agent.HeatMapAnalyzer ✓
"Status transitions" → Agent.StatusTransitionTracker ✓
"Tell me about issue ABC123" → Agent.QueryHandler ✓
"Show alerts" → Agent.AlertManager ✓
"Trends this week" → Agent.TrendAnalyzer ✓
"Refresh data" → Agent.DataFetcher ✓
"What changed?" → Agent.ChangeDetector ✓
```

### Test 5: Report Generation

**Full end-to-end test**:
1. Fetch SmartSheets data
2. Wait 1 hour, make changes in SmartSheets
3. Fetch data again
4. Query: "Generate comprehensive daily report"
5. Verify: Markdown report created in data/reports/

---

## Scheduling Setup

### Option 1: GitHub Actions (Recommended)

**File**: `.github/workflows/smartsheets-monitor.yml`

```yaml
name: SmartSheets Issue Monitor
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
  workflow_dispatch:  # Manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Flowise Workflow
        run: |
          curl -X POST "${{ secrets.FLOWISE_API_URL }}/api/v1/prediction/${{ secrets.WORKFLOW_ID }}" \
            -H "Authorization: Bearer ${{ secrets.FLOWISE_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "question": "Generate daily report and check for alerts",
              "overrideConfig": {}
            }'
```

**Secrets to add**:
- `FLOWISE_API_URL`: Your Flowise instance URL
- `FLOWISE_API_KEY`: API key from Flowise settings
- `WORKFLOW_ID`: Workflow ID from Flowise (in URL)

### Option 2: AWS EventBridge

```json
{
  "ScheduleExpression": "rate(6 hours)",
  "Target": {
    "Arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:TriggerFlowise",
    "Input": "{\"workflowId\": \"YOUR_WORKFLOW_ID\", \"query\": \"Generate daily report\"}"
  }
}
```

### Option 3: Cron (Self-Hosted)

**File**: `trigger-workflow.sh`

```bash
#!/bin/bash
FLOWISE_URL="https://your-flowise-instance.com"
WORKFLOW_ID="your-workflow-id"
API_KEY="your-api-key"

curl -X POST "$FLOWISE_URL/api/v1/prediction/$WORKFLOW_ID" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Generate daily report and check for alerts"
  }'
```

**Crontab**:
```bash
# Run every 6 hours
0 */6 * * * /path/to/trigger-workflow.sh >> /var/log/smartsheets-monitor.log 2>&1
```

---

## Troubleshooting

### Issue: "Tool not found: currentDateTime"

**Cause**: Standard tools don't exist in Flowise instance

**Solution**:
1. Follow "Standard Tools Setup" section above
2. Create currentDateTime and searXNG tools
3. Re-open agents in workflow - tools should now be visible

### Issue: Agents show blank tool fields after import

**Cause**: This is EXPECTED behavior. Custom tools are not included in JSON.

**Solution**:
1. This is intentional (avoids phantom tool references)
2. Custom tools (smartsheets-api, file-system, etc.) must be created manually
3. Follow "Custom Tools Configuration" section above
4. After creating tools, you can assign them to agents in Flowise UI

### Issue: SmartSheets API returns 401 Unauthorized

**Cause**: Invalid or expired API token

**Solution**:
1. Regenerate API token in SmartSheets Account → API Access
2. Update credential in Flowise
3. Test with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_NEW_TOKEN" \
        "https://api.smartsheet.com/2.0/users/me"
   ```

### Issue: Rate limit exceeded (429 error)

**Cause**: SmartSheets API limit is 300 requests/minute

**Solution**:
1. Check for duplicate scheduled runs
2. Implement exponential backoff in smartsheets-api tool
3. Reduce query frequency (e.g., 8-hour intervals instead of 6)
4. Use pagination efficiently (100 rows per request max)

### Issue: Snapshots not saving

**Cause**: File system permissions or directory doesn't exist

**Solution**:
```bash
# Create directories
mkdir -p data/snapshots data/reports data/metrics

# Set permissions
chmod 755 data data/snapshots data/reports data/metrics

# Test write access
touch data/snapshots/test.txt && rm data/snapshots/test.txt
```

### Issue: Intent router sends to wrong agent

**Cause**: Query keywords don't match routing instructions

**Solution**:
1. Open condition router node
2. Review routing instructions
3. Add custom keywords for your use case
4. Test with specific queries to verify routing

### Issue: Workflow slow to respond

**Cause**: Large SmartSheets dataset or expensive analytics

**Solution**:
1. Optimize SmartSheets API queries (use filters, pagination)
2. Cache frequently accessed data
3. Run analytics tools asynchronously
4. Consider using smaller snapshot windows (7 days instead of 30)

---

## Next Steps

1. ✅ Complete all tool configurations
2. ✅ Test each agent individually
3. ✅ Run full end-to-end test with real SmartSheets data
4. ✅ Set up automated scheduling
5. ✅ Configure notification channels (Slack/email)
6. ✅ Monitor first few scheduled runs for issues
7. ✅ Adjust thresholds and alerting rules as needed

---

## Additional Resources

- **Flowise Documentation**: https://docs.flowiseai.com/
- **SmartSheets API Docs**: https://smartsheet.redoc.ly/
- **SearXNG Documentation**: https://docs.searxng.org/
- **GitHub Actions Docs**: https://docs.github.com/actions

---

**Need Help?**
- Check tool-configs/ directory for detailed tool setup guides
- Review examples/ directory for sample data formats
- Refer to README.md for feature overview and use cases

---

**Built with ❤️ by Context Foundry**
