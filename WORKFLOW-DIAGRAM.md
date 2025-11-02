```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#4DD0E1','primaryTextColor':'#000','primaryBorderColor':'#0097A7','lineColor':'#757575','secondaryColor':'#ff8fab','tertiaryColor':'#7EE787'}}}%%
graph TD
    startAgentflow_0([SmartSheets Issue Monitor])
    style startAgentflow_0 fill:#7EE787,stroke:#333,stroke-width:2px
    conditionAgentAgentflow_0{&Intent Router&#}
    style conditionAgentAgentflow_0 fill:#ff8fab,stroke:#333,stroke-width:2px
    agentAgentflow_1[Agent.DataFetcher]
    style agentAgentflow_1 fill:#4DD0E1,stroke:#333,stroke-width:2px
    agentAgentflow_2[Agent.ChangeDetector]
    style agentAgentflow_2 fill:#4DD0E1,stroke:#333,stroke-width:2px
    agentAgentflow_3[Agent.HeatMapAnalyzer]
    style agentAgentflow_3 fill:#4DD0E1,stroke:#333,stroke-width:2px
    agentAgentflow_4[Agent.StatusTransitionTracker]
    style agentAgentflow_4 fill:#4DD0E1,stroke:#333,stroke-width:2px
    agentAgentflow_5[Agent.ReportGenerator]
    style agentAgentflow_5 fill:#4DD0E1,stroke:#333,stroke-width:2px
    agentAgentflow_6[Agent.QueryHandler]
    style agentAgentflow_6 fill:#4DD0E1,stroke:#333,stroke-width:2px
    agentAgentflow_7[Agent.AlertManager]
    style agentAgentflow_7 fill:#4DD0E1,stroke:#333,stroke-width:2px
    agentAgentflow_8[Agent.TrendAnalyzer]
    style agentAgentflow_8 fill:#4DD0E1,stroke:#333,stroke-width:2px

    startAgentflow_0 --> conditionAgentAgentflow_0
    conditionAgentAgentflow_0 -->|S0| agentAgentflow_1
    conditionAgentAgentflow_0 -->|S1| agentAgentflow_2
    conditionAgentAgentflow_0 -->|S2| agentAgentflow_3
    conditionAgentAgentflow_0 -->|S3| agentAgentflow_4
    conditionAgentAgentflow_0 -->|S4| agentAgentflow_5
    conditionAgentAgentflow_0 -->|S5| agentAgentflow_6
    conditionAgentAgentflow_0 -->|S6| agentAgentflow_7
    conditionAgentAgentflow_0 -->|S7| agentAgentflow_8
```

<details>
<summary><b>🔍 View Agent Details (Click to Expand)</b></summary>

| Agent | Type | Description |
|-------|------|-------------|
| SmartSheets Issue Monitor | StartAgent | Start agent for workflow with form inputs |
| Intent Router | ConditionAgent | Route user to appropriate agent based on detect... |
| Agent.DataFetcher | Agent | Dynamically choose and utilize tools during run... |
| Agent.ChangeDetector | Agent | Dynamically choose and utilize tools during run... |
| Agent.HeatMapAnalyzer | Agent | Dynamically choose and utilize tools during run... |
| Agent.StatusTransitionTracker | Agent | Dynamically choose and utilize tools during run... |
| Agent.ReportGenerator | Agent | Dynamically choose and utilize tools during run... |
| Agent.QueryHandler | Agent | Dynamically choose and utilize tools during run... |
| Agent.AlertManager | Agent | Dynamically choose and utilize tools during run... |
| Agent.TrendAnalyzer | Agent | Dynamically choose and utilize tools during run... |

</details>
