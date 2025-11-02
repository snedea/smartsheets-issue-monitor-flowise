# SmartSheets Issue Monitor - Flowise Multi-Agent System

Intelligent SmartSheets issue log monitoring system built as a Flowise multi-agent workflow. Automatically detects changes, identifies "heating up" issues, tracks status transitions, and generates actionable analytics reports.

**Status**: Production-ready Flowise workflow
**Agents**: 8 specialized agents + intelligent intent router
**Deployment**: Importable JSON workflow for Flowise

---

## ✨ Features

### 🔄 Automated Change Detection
- **Real-time monitoring**: Track all changes to your SmartSheets issue log
- **Delta analysis**: Identify new issues, status changes, assignee updates, priority shifts
- **Smart comparison**: Compare current state vs. previous snapshots automatically

### 🔥 "Heating Up" Issues Detection
- **Frequency tracking**: Monitor update velocity per issue
- **Anomaly detection**: Flag issues with >3 updates in 24 hours
- **Thrashing detection**: Identify issues changing status repeatedly
- **Heat metrics**: Calculate updates per day, acceleration rates

### 📊 Status Transition Analytics
- **Workflow metrics**: Track New→InProgress→Resolved→Closed transitions
- **Bottleneck detection**: Find issues stuck in one status for >7 days
- **Backward transitions**: Identify re-opened issues (Resolved→InProgress)
- **Lifecycle analysis**: Average time in each status

### 📝 Intelligent Reporting
- **Human-friendly summaries**: Natural language reports, not data dumps
- **Key metrics**: New issues, resolved issues, active contributors
- **Top 5 hot issues**: Ranked by update frequency with context
- **Blocked/stalled alerts**: Issues needing attention
- **Trend analysis**: Week-over-week comparisons, predictive insights

### 🎯 Multi-Agent Architecture
1. **Data Fetcher** - SmartSheets API integration with rate limiting
2. **Change Detector** - Snapshot comparison and delta identification
3. **Heat Map Analyzer** - Update frequency and velocity analysis
4. **Status Transition Tracker** - Workflow metrics and lifecycle tracking
5. **Report Generator** - Comprehensive Markdown report creation
6. **Query Handler** - Ad-hoc questions and drill-down analysis
7. **Alert Manager** - Threshold monitoring and critical issue flagging
8. **Trend Analyzer** - Pattern recognition and predictive insights

---

## 🚀 Quick Start

### Prerequisites
- [Flowise](https://flowiseai.com/) instance running (local or cloud)
- SmartSheets account with API access
- OAuth 2.0 credentials or API token for SmartSheets

### Installation

1. **Import workflow to Flowise**:
   - Open your Flowise instance
   - Go to Workflows → Import
   - Upload `smartsheets-issue-monitor-flow.json`
   - Verify all nodes appear on canvas with no errors

2. **Configure custom tools** (see [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)):
   - SmartSheets API tool (OAuth authentication)
   - File system tools (snapshot storage)
   - Notification webhook (Slack/email alerts)
   - Analytics tools (frequency, transition, trend calculators)

3. **Set up scheduling** (optional):
   - Use GitHub Actions, AWS EventBridge, or cron
   - See `scheduling/` directory for examples
   - Call Flowise API endpoint every 6 hours (4x daily)

4. **Test the workflow**:
   - Open workflow in Flowise
   - Send test query: "Generate daily report"
   - Verify agent responds with appropriate summary

---

## 📖 Usage

### Query Examples

**Get status update**:
```
"What changed today?"
"Generate daily report"
```
→ Routes to **Report Generator** for comprehensive summary

**Find hot issues**:
```
"Show me heating up issues"
"Which issues are being updated frequently?"
```
→ Routes to **Heat Map Analyzer** for velocity analysis

**Status transitions**:
```
"Show status transition metrics"
"How many issues moved to In Progress?"
```
→ Routes to **Status Transition Tracker** for workflow analytics

**Issue details**:
```
"Tell me about issue ABC123"
"Show update history for issue XYZ789"
```
→ Routes to **Query Handler** for drill-down details

**Alerts**:
```
"Show me blocked issues"
"Which critical issues need attention?"
```
→ Routes to **Alert Manager** for threshold violations

**Trends**:
```
"Compare this week to last week"
"What patterns do you see in resolution time?"
```
→ Routes to **Trend Analyzer** for predictive insights

**Fetch latest data**:
```
"Refresh SmartSheets data"
"Pull latest issue log"
```
→ Routes to **Data Fetcher** for API sync

**Changes**:
```
"What changed since yesterday?"
"Show me the deltas"
```
→ Routes to **Change Detector** for diff analysis

---

## 📂 Project Structure

```
smartsheets-issue-monitor/
├── smartsheets-issue-monitor-flow.json   # ⭐ Main Flowise workflow (import this)
├── README.md                             # This file
├── INTEGRATION_GUIDE.md                  # Detailed setup instructions
├── tool-configs/                         # Custom tool configuration guides
│   ├── smartsheets-api-tool.md
│   ├── file-system-tool.md
│   ├── notification-webhook-tool.md
│   └── analytics-tools.md
├── examples/                             # Sample data formats
│   ├── sample-snapshot.json
│   ├── sample-report.md
│   └── sample-metrics.json
├── scheduling/                           # Automated scheduling examples
│   ├── github-actions-workflow.yml
│   ├── aws-eventbridge-config.json
│   └── cron-example.sh
└── generate_workflow.py                  # Workflow generation script (used during build)
```

---

## 🛠️ Technical Architecture

### Node Structure
- **1 Start Node**: Entry point with form input
- **1 Intent Router**: Intelligent routing based on query intent (8 scenarios)
- **8 Specialized Agents**: Domain-specific expertise
- **9 Edge Connections**: 1 start→router + 8 router→agents

### Agent Capabilities

| Agent | Purpose | Tools | Memory |
|-------|---------|-------|--------|
| Data Fetcher | SmartSheets API integration | currentDateTime, searXNG, smartsheets-api | Window (10) |
| Change Detector | Snapshot comparison | currentDateTime, searXNG, file-system | All Messages |
| Heat Map Analyzer | Update frequency analysis | currentDateTime, searXNG, frequency-calc | Window (20) |
| Status Transition Tracker | Workflow metrics | currentDateTime, searXNG, transition-analyzer | All Messages |
| Report Generator | Human-friendly reports | currentDateTime, searXNG, file-system | Summary |
| Query Handler | Ad-hoc questions | currentDateTime, searXNG, file-system | Window (10) |
| Alert Manager | Threshold monitoring | currentDateTime, searXNG, notification-webhook | Window (5) |
| Trend Analyzer | Pattern recognition | currentDateTime, searXNG, trend-calculator | Summary |

### Standard Tools (Auto-Included)
All agents include these 2 tools:
- **currentDateTime**: Temporal awareness for data freshness evaluation
- **searXNG**: Federated web search for context and benchmarks

### Custom Tools (User-Configured)
Required tools to create in Flowise after import:
- **smartsheets-api**: SmartSheets REST API v2.0 integration
- **file-system-read/write**: Snapshot and report storage
- **notification-webhook**: Slack/email alert delivery
- **frequency-calculator**: Update velocity computation
- **transition-analyzer**: Status change metrics
- **trend-calculator**: Statistical analysis (mean, std dev, regression)

---

## ⚙️ Configuration

### SmartSheets API Setup
1. Go to SmartSheets Developer Portal: https://developers.smartsheet.com/
2. Create OAuth 2.0 application or generate API token
3. Note Sheet ID for your issue tracker
4. Configure in Flowise custom tool (see INTEGRATION_GUIDE.md)

### Scheduling (4x Daily Monitoring)
The workflow should run automatically 4 times per day (every 6 hours):

**GitHub Actions** (Recommended):
```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
```

**AWS EventBridge**:
```
rate(6 hours)
```

**Cron**:
```bash
0 */6 * * * /path/to/trigger-workflow.sh
```

See `scheduling/` directory for complete examples.

### Data Persistence
- **Snapshots**: Stored in `data/snapshots/` directory (JSON)
- **Reports**: Stored in `data/reports/` directory (Markdown + JSON)
- **Metrics**: Stored in `data/metrics/` directory (per-issue frequency)
- **Retention**: 30 days (automatic pruning)

---

## 🧪 Testing

### Import Validation
After importing to Flowise:
1. ✅ All 10 nodes visible on canvas
2. ✅ No "disconnected node" warnings
3. ✅ Open each agent - no blank required fields
4. ✅ Router has 8 output connections
5. ✅ Standard tools (currentDateTime, searXNG) show in all agents

### Functional Testing
1. **Intent routing**: Send various queries, verify correct agent handles each
2. **Data fetching**: Trigger "Refresh SmartSheets data", verify API call succeeds
3. **Change detection**: Run twice, verify deltas detected
4. **Report generation**: Request "daily report", verify Markdown output
5. **Alerts**: Check for blocked/stalled issues, verify threshold detection

---

## 📚 Documentation

- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Complete setup walkthrough with custom tool configuration
- **[tool-configs/](tool-configs/)** - Detailed configuration for each custom tool
- **[examples/](examples/)** - Sample data formats and output examples
- **[scheduling/](scheduling/)** - Automated scheduling configuration examples

---

## 💡 Use Cases

### Development Team Lead
- **Morning routine**: Check "heating up" issues from overnight
- **Sprint planning**: Review status transition metrics to identify bottlenecks
- **Team health**: Analyze trends in resolution time and contributor activity

### Project Manager
- **Daily standup**: Generate comprehensive report showing yesterday's activity
- **Risk management**: Review alerts for blocked/stalled issues
- **Forecasting**: Use trend analysis for sprint goal predictions

### QA Engineer
- **Issue tracking**: Monitor which issues are being re-opened (Resolved→InProgress)
- **Pattern detection**: Identify thrashing issues that may indicate instability
- **Velocity tracking**: Compare current bug resolution rate to historical baseline

### Product Owner
- **Prioritization**: Use heat map to see which issues are actively discussed
- **Stakeholder updates**: Generate natural language summaries for non-technical audiences
- **Trend spotting**: Week-over-week comparisons to understand team capacity

---

## 🔒 Security & Privacy

- **API credentials**: Stored securely in Flowise credential manager
- **Data retention**: 30-day snapshot history (configurable)
- **Alert throttling**: Prevents spam with recent alert tracking
- **Human-in-the-loop**: Notification webhooks require approval for sensitive alerts

---

## 🤝 Contributing

This workflow was autonomously generated by Context Foundry. To contribute:

1. Import workflow to Flowise
2. Make modifications in Flowise UI
3. Export updated workflow JSON
4. Submit PR with changes and rationale

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Flowise**: Open-source LLM orchestration framework
- **SmartSheets**: Collaborative work management platform
- **Context Foundry**: Autonomous build system for multi-agent workflows

---

## 🚨 Troubleshooting

### "Tool not found" error on import
**Solution**: Standard tools (currentDateTime, searXNG) must exist in your Flowise instance. See INTEGRATION_GUIDE.md for tool creation.

### Agents show blank tool fields
**Solution**: This is expected - custom tools (smartsheets-api, etc.) must be created manually after import. Follow INTEGRATION_GUIDE.md custom tool setup section.

### Intent routing sends to wrong agent
**Solution**: Check routing instructions in condition router. Keywords may need adjustment for your specific queries.

### SmartSheets API rate limit exceeded
**Solution**: Workflow respects 300 req/min limit. If exceeded, check for duplicate scheduled runs or reduce query frequency.

### Snapshots not saving
**Solution**: Verify file-system tools are configured correctly with write permissions to data/ directory.

---

## 📞 Support

- **Documentation**: See INTEGRATION_GUIDE.md for detailed setup
- **Issues**: Check tool-configs/ for troubleshooting specific tools
- **Examples**: Reference examples/ directory for expected data formats

---

**Built with ❤️ by Context Foundry**

🤖 *This workflow was autonomously generated, tested, and documented by Context Foundry's multi-agent build system.*
