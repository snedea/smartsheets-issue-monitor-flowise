#!/usr/bin/env python3
"""
Generate complete Flowise workflow JSON for SmartSheets Issue Monitor
This script creates a single, complete JSON file with all 10 nodes inline.
"""

import json

# Agent specifications (from architecture.md)
AGENTS = [
    {
        "id": 1,
        "label": "Agent.DataFetcher",
        "position": {"x": 1100, "y": -200},
        "persona": "<p><em>You are an expert SmartSheets API integration agent.</em> You fetch sheet data from the SmartSheets REST API v2.0, handle OAuth authentication, implement pagination for large datasets, respect rate limits (300 requests/minute), and parse column metadata. You return structured JSON snapshots of the sheet state including all rows, columns, and metadata. If API calls fail, you implement exponential backoff and retry logic. You do NOT analyze or interpret data - you only fetch and structure it.</p>",
        "temperature": 0.3,
        "memory_type": "windowSize",
        "memory_window": 10
    },
    {
        "id": 2,
        "label": "Agent.ChangeDetector",
        "position": {"x": 1100, "y": 50},
        "persona": "<p><em>You are an expert change detection and snapshot comparison agent.</em> You compare the current SmartSheets data snapshot against the most recent previous snapshot to identify all changes. You detect: (1) New issues created (capture creator, timestamp), (2) Status transitions (from/to), (3) Assignee changes, (4) Priority changes, (5) Description/title updates, (6) Deleted issues. You categorize changes by type and severity. You return structured change reports with before/after values. You focus ONLY on detecting what changed, not analyzing why or making predictions.</p>",
        "temperature": 0.3,
        "memory_type": "allMessages",
        "memory_window": None
    },
    {
        "id": 3,
        "label": "Agent.HeatMapAnalyzer",
        "position": {"x": 1100, "y": 300},
        "persona": "<p><em>You are an expert update frequency and velocity analysis agent.</em> You track how often each issue is updated over time. You identify \"heating up\" issues (>3 updates in 24 hours) and calculate velocity metrics (updates per day). You detect thrashing (status changes back and forth multiple times). You maintain frequency counters per issue and flag anomalies (update frequency >3x baseline). You return ranked lists of hot issues with context (what's changing frequently). You focus on quantitative metrics, not qualitative analysis.</p>",
        "temperature": 0.4,
        "memory_type": "windowSize",
        "memory_window": 20
    },
    {
        "id": 4,
        "label": "Agent.StatusTransitionTracker",
        "position": {"x": 1100, "y": 550},
        "persona": "<p><em>You are an expert status transition and workflow metrics agent.</em> You track the full lifecycle of issues through status changes. You calculate transition counts (how many New→InProgress, InProgress→Resolved, etc.), average time in each status, and identify bottlenecks (issues stuck in one status for >7 days). You detect backward transitions (Resolved→InProgress indicates re-opening) and thrashing patterns. You return comprehensive status transition reports with metrics and insights into workflow health. You understand issue lifecycle patterns and flag anomalies.</p>",
        "temperature": 0.4,
        "memory_type": "allMessages",
        "memory_window": None
    },
    {
        "id": 5,
        "label": "Agent.ReportGenerator",
        "position": {"x": 1100, "y": 800},
        "persona": "<p><em>You are an expert report generation and data synthesis agent.</em> You create comprehensive, human-friendly reports in Markdown format summarizing SmartSheets activity. Your reports include: (1) Executive summary, (2) New issues created count, (3) Issues resolved count, (4) Status transition breakdown, (5) Top 5 heating up issues with context, (6) Most active contributors, (7) Blocked/stalled issues list. You write in clear, concise natural language, use bullet points and tables effectively, and highlight key insights. You transform raw metrics into actionable intelligence. You do NOT just dump data - you tell the story of what's happening.</p>",
        "temperature": 0.7,
        "memory_type": "conversationSummary",
        "memory_window": None
    },
    {
        "id": 6,
        "label": "Agent.QueryHandler",
        "position": {"x": 1100, "y": 1050},
        "persona": "<p><em>You are an expert query handling and drill-down analysis agent.</em> You answer specific user questions about issues in the SmartSheets log. You can: (1) Retrieve details for specific issue IDs, (2) Show full update history for an issue, (3) Compare multiple issues, (4) Answer \"why\" questions using change history, (5) Provide trend context for individual issues. You search snapshots and metrics to find requested information. You respond conversationally and helpfully. If data is unavailable, you clearly state what's missing and suggest alternatives.</p>",
        "temperature": 0.6,
        "memory_type": "windowSize",
        "memory_window": 10
    },
    {
        "id": 7,
        "label": "Agent.AlertManager",
        "position": {"x": 1100, "y": 1300},
        "persona": "<p><em>You are an expert alert management and threshold monitoring agent.</em> You continuously monitor issue metrics against defined thresholds and flag critical situations. You detect: (1) Blocked issues (status=Blocked for >3 days), (2) Stalled issues (no updates in >7 days + status=InProgress), (3) Thrashing issues (>5 status changes in 24h), (4) High-priority issues with no activity (priority=High + no updates in >3 days). You generate clear, actionable alerts with context and severity levels. You avoid alert spam by tracking recently alerted issues. You prioritize alerts by business impact.</p>",
        "temperature": 0.3,
        "memory_type": "windowSize",
        "memory_window": 5
    },
    {
        "id": 8,
        "label": "Agent.TrendAnalyzer",
        "position": {"x": 1100, "y": 1550},
        "persona": "<p><em>You are an expert trend analysis and predictive insights agent.</em> You analyze long-term patterns in SmartSheets issue data. You perform week-over-week comparisons (e.g., \"5 issues created this week vs 12 last week - 58% decrease\"), identify anomalies (values >2 std dev from mean), and generate predictive insights (e.g., \"Based on current velocity, sprint goal may be at risk\"). You detect patterns like \"Issues assigned to John resolve 30% faster than average\" or \"Average resolution time increased 20% this week\". You use historical baselines and statistical analysis. You communicate insights in business-friendly language with quantitative backing.</p>",
        "temperature": 0.5,
        "memory_type": "conversationSummary",
        "memory_window": None
    }
]

# Standard tools configuration (from AGENT-NODE-TEMPLATE.json)
STANDARD_TOOLS = [
    {
        "agentSelectedTool": "currentDateTime",
        "agentSelectedToolRequiresHumanInput": "",
        "agentSelectedToolConfig": {
            "agentSelectedTool": "currentDateTime"
        }
    },
    {
        "agentSelectedTool": "searXNG",
        "agentSelectedToolRequiresHumanInput": "",
        "agentSelectedToolConfig": {
            "apiBase": "https://s.llam.ai",
            "toolName": "searxng-search",
            "toolDescription": "Federated web/meta search. Use when you need fresh facts or sources. Provide a natural-language query; returns a ranked, de-duplicated JSON list of result metadata for follow-up browsing and citation.",
            "headers": "",
            "format": "json",
            "categories": "",
            "engines": "",
            "language": "",
            "pageno": "",
            "time_range": "",
            "safesearch": "",
            "agentSelectedTool": "searXNG"
        }
    }
]

def create_agent_node(agent_spec):
    """Create a complete agent node with all required parameters"""
    node_id = f"agentAgentflow_{agent_spec['id']}"

    # Base memory config
    memory_config = {
        "agentEnableMemory": True,
        "agentMemoryType": agent_spec['memory_type']
    }

    # Add window size if applicable
    if agent_spec['memory_window'] is not None:
        memory_config["agentMemoryWindowSize"] = agent_spec['memory_window']

    return {
        "id": node_id,
        "position": agent_spec['position'],
        "data": {
            "id": node_id,
            "label": agent_spec['label'],
            "version": 2.2,
            "name": "agentAgentflow",
            "type": "Agent",
            "color": "#4DD0E1",
            "baseClasses": ["Agent"],
            "category": "Agent Flows",
            "description": "Dynamically choose and utilize tools during runtime, enabling multi-step reasoning",
            "inputParams": create_agent_input_params(node_id),
            "inputAnchors": [],
            "inputs": {
                "agentModel": "chatOpenAI",
                "agentModelConfig": {
                    "cache": "",
                    "modelName": "gpt-4o-mini",
                    "temperature": agent_spec['temperature'],
                    "streaming": True,
                    "maxTokens": "",
                    "topP": "",
                    "frequencyPenalty": "",
                    "presencePenalty": "",
                    "timeout": "",
                    "strictToolCalling": "",
                    "stopSequence": "",
                    "basepath": "",
                    "proxyUrl": "",
                    "baseOptions": "",
                    "allowImageUploads": "",
                    "imageResolution": "low",
                    "reasoning": "",
                    "reasoningEffort": "",
                    "reasoningSummary": "",
                    "agentModel": "chatOpenAI"
                },
                "agentMessages": [
                    {
                        "role": "system",
                        "content": agent_spec['persona']
                    }
                ],
                "agentToolsBuiltInOpenAI": "",
                "agentTools": STANDARD_TOOLS,
                "agentKnowledgeDocumentStores": "",
                "agentKnowledgeVSEmbeddings": "",
                **memory_config,
                "agentUserMessage": "",
                "agentReturnResponseAs": "userMessage",
                "agentUpdateState": ""
            },
            "outputAnchors": [
                {
                    "id": f"{node_id}-output-agentAgentflow-Agent|AgentExecutor",
                    "name": "agentAgentflow",
                    "label": "Agent",
                    "description": "Agent",
                    "type": "Agent | AgentExecutor"
                }
            ],
            "outputs": {},
            "selected": False
        },
        "type": "agentFlow",
        "width": 300,
        "height": 500,
        "selected": False,
        "positionAbsolute": agent_spec['position'],
        "dragging": False
    }

def create_agent_input_params(node_id):
    """Create the inputParams array for an agent node"""
    return [
        {
            "label": "Model",
            "name": "agentModel",
            "type": "asyncOptions",
            "loadMethod": "listModels",
            "loadConfig": True,
            "id": f"{node_id}-input-agentModel-asyncOptions",
            "display": True
        },
        {
            "label": "Messages",
            "name": "agentMessages",
            "type": "array",
            "optional": True,
            "acceptVariable": True,
            "array": [
                {
                    "label": "Role",
                    "name": "role",
                    "type": "options",
                    "options": [
                        {"label": "System", "name": "system"},
                        {"label": "Assistant", "name": "assistant"},
                        {"label": "Developer", "name": "developer"},
                        {"label": "User", "name": "user"}
                    ]
                },
                {
                    "label": "Content",
                    "name": "content",
                    "type": "string",
                    "acceptVariable": True,
                    "generateInstruction": True,
                    "rows": 4
                }
            ],
            "id": f"{node_id}-input-agentMessages-array",
            "display": True
        },
        {
            "label": "Tools",
            "name": "agentTools",
            "type": "array",
            "optional": True,
            "id": f"{node_id}-input-agentTools-array",
            "display": True
        },
        {
            "label": "Enable Memory",
            "name": "agentEnableMemory",
            "type": "boolean",
            "default": True,
            "id": f"{node_id}-input-agentEnableMemory-boolean",
            "display": True
        },
        {
            "label": "Memory Type",
            "name": "agentMemoryType",
            "type": "options",
            "options": [
                {"label": "All Messages", "name": "allMessages"},
                {"label": "Window Size", "name": "windowSize"},
                {"label": "Conversation Summary", "name": "conversationSummary"}
            ],
            "default": "allMessages",
            "id": f"{node_id}-input-agentMemoryType-options",
            "display": True
        },
        {
            "label": "Memory Window Size",
            "name": "agentMemoryWindowSize",
            "type": "number",
            "optional": True,
            "id": f"{node_id}-input-agentMemoryWindowSize-number"
        }
    ]

def create_start_node():
    """Create the start node"""
    return {
        "id": "startAgentflow_0",
        "position": {"x": 300, "y": 400},
        "data": {
            "id": "startAgentflow_0",
            "label": "SmartSheets Issue Monitor",
            "version": 1.2,
            "name": "startAgentflow",
            "type": "StartAgent",
            "color": "#81c784",
            "baseClasses": ["StartAgent"],
            "category": "Agent Flows",
            "description": "Start agent for workflow with form inputs",
            "inputParams": [
                {
                    "label": "Form Title",
                    "name": "formTitle",
                    "type": "string",
                    "placeholder": "SmartSheets Issue Monitor",
                    "id": "startAgentflow_0-input-formTitle-string"
                },
                {
                    "label": "Form Description",
                    "name": "formDescription",
                    "type": "string",
                    "rows": 3,
                    "placeholder": "Intelligent issue log monitoring with change detection, heat mapping, and analytics reporting.",
                    "id": "startAgentflow_0-input-formDescription-string"
                },
                {
                    "label": "Form Input Types",
                    "name": "formInputTypes",
                    "type": "datagrid",
                    "datagrid": [
                        {"field": "type", "headerName": "Type", "type": "singleSelect", "valueOptions": ["string", "number", "boolean", "date", "file"]},
                        {"field": "name", "headerName": "Name", "editable": True},
                        {"field": "label", "headerName": "Label", "editable": True}
                    ],
                    "id": "startAgentflow_0-input-formInputTypes-datagrid"
                }
            ],
            "inputAnchors": [],
            "inputs": {
                "formTitle": "SmartSheets Issue Monitor",
                "formDescription": "Intelligent issue log monitoring with change detection, heat mapping, and analytics reporting. Ask me about changes, hot issues, status transitions, comprehensive reports, specific issues, alerts, or trends.",
                "formInputTypes": [
                    {"type": "string", "name": "query", "label": "What would you like to know about your issue log?"}
                ]
            },
            "outputAnchors": [
                {
                    "id": "startAgentflow_0-output-startAgentflow-StartAgent",
                    "name": "startAgentflow",
                    "label": "StartAgent",
                    "description": "StartAgent",
                    "type": "StartAgent"
                }
            ],
            "outputs": {},
            "selected": False
        },
        "type": "agentFlow",
        "width": 300,
        "height": 500,
        "selected": False,
        "positionAbsolute": {"x": 300, "y": 400},
        "dragging": False
    }

def create_condition_node():
    """Create the condition/router node"""
    return {
        "id": "conditionAgentAgentflow_0",
        "position": {"x": 700, "y": 400},
        "data": {
            "id": "conditionAgentAgentflow_0",
            "label": "Intent Router",
            "version": 1.1,
            "name": "conditionAgentAgentflow",
            "type": "ConditionAgent",
            "color": "#ff8fab",
            "baseClasses": ["ConditionAgent"],
            "category": "Agent Flows",
            "description": "Route user to appropriate agent based on detected intention",
            "inputParams": [
                {
                    "label": "Model",
                    "name": "conditionAgentModel",
                    "type": "asyncOptions",
                    "loadMethod": "listModels",
                    "loadConfig": True,
                    "id": "conditionAgentAgentflow_0-input-conditionAgentModel-asyncOptions"
                },
                {
                    "label": "Instructions",
                    "name": "conditionAgentInstructions",
                    "type": "string",
                    "rows": 4,
                    "placeholder": "Analyze the user input and route to the appropriate agent...",
                    "id": "conditionAgentAgentflow_0-input-conditionAgentInstructions-string"
                },
                {
                    "label": "Input",
                    "name": "conditionAgentInput",
                    "type": "string",
                    "acceptVariable": True,
                    "id": "conditionAgentAgentflow_0-input-conditionAgentInput-string"
                },
                {
                    "label": "Scenarios",
                    "name": "conditionAgentScenarios",
                    "type": "array",
                    "array": [{"label": "Scenario", "name": "scenario", "type": "string", "rows": 2}],
                    "id": "conditionAgentAgentflow_0-input-conditionAgentScenarios-array"
                }
            ],
            "inputAnchors": [],
            "inputs": {
                "conditionAgentModel": "chatOpenAI",
                "conditionAgentModelConfig": {
                    "modelName": "gpt-4o-mini",
                    "temperature": 0.2,
                    "streaming": True,
                    "agentModel": "chatOpenAI"
                },
                "conditionAgentInstructions": "Analyze the user's query and determine their primary intent. Route to the appropriate specialized agent:\n\nKEYWORDS MAPPING:\n- \"fetch\", \"refresh\", \"get data\", \"pull SmartSheets\" → Data Fetcher (Scenario 0)\n- \"changes\", \"deltas\", \"what changed\", \"compare\" → Change Detector (Scenario 1)\n- \"hot issues\", \"heating up\", \"frequent updates\", \"velocity\" → Heat Map Analyzer (Scenario 2)\n- \"status transitions\", \"workflow metrics\", \"state changes\" → Status Transition Tracker (Scenario 3)\n- \"report\", \"summary\", \"daily\", \"comprehensive\" → Report Generator (Scenario 4)\n- \"show issue\", \"details\", \"query\", specific issue ID → Query Handler (Scenario 5)\n- \"alerts\", \"critical\", \"blocked\", \"stalled\" → Alert Manager (Scenario 6)\n- \"trends\", \"patterns\", \"week over week\", \"predictive\" → Trend Analyzer (Scenario 7)\n\nIf multiple intents detected, choose the PRIMARY intent based on main verb/action. If unclear, default to Report Generator (comprehensive overview).",
                "conditionAgentInput": "{{question}}",
                "conditionAgentScenarios": [
                    {"scenario": "User needs to fetch latest SmartSheets data"},
                    {"scenario": "User wants to see what changed since last check"},
                    {"scenario": "User wants to identify heating up issues with high update frequency"},
                    {"scenario": "User wants status transition metrics and workflow analysis"},
                    {"scenario": "User wants a comprehensive daily/periodic report"},
                    {"scenario": "User has a specific question about an issue or wants details"},
                    {"scenario": "User needs critical alerts for blocked or stalled issues"},
                    {"scenario": "User wants trend analysis and predictive insights"}
                ]
            },
            "outputAnchors": [
                {"id": f"conditionAgentAgentflow_0-output-{i}", "label": i, "name": i, "description": f"Condition {i}", "type": "number"}
                for i in range(8)
            ],
            "outputs": {},
            "selected": False
        },
        "type": "agentFlow",
        "width": 300,
        "height": 500,
        "selected": False,
        "positionAbsolute": {"x": 700, "y": 400},
        "dragging": False
    }

def create_edges():
    """Create all edge connections"""
    edges = []

    # Edge 1: Start → Router
    edges.append({
        "source": "startAgentflow_0",
        "sourceHandle": "startAgentflow_0-output-startAgentflow-StartAgent",
        "target": "conditionAgentAgentflow_0",
        "targetHandle": "conditionAgentAgentflow_0",
        "data": {
            "sourceColor": "#81c784",
            "targetColor": "#ff8fab",
            "edgeLabel": "",
            "isHumanInput": False
        },
        "type": "agentFlow",
        "id": "startAgentflow_0-startAgentflow_0-output-startAgentflow-StartAgent-conditionAgentAgentflow_0-conditionAgentAgentflow_0"
    })

    # Edges 2-9: Router → Agents
    for i in range(8):
        agent_id = i + 1
        edges.append({
            "source": "conditionAgentAgentflow_0",
            "sourceHandle": f"conditionAgentAgentflow_0-output-{i}",
            "target": f"agentAgentflow_{agent_id}",
            "targetHandle": f"agentAgentflow_{agent_id}",
            "data": {
                "sourceColor": "#ff8fab",
                "targetColor": "#4DD0E1",
                "edgeLabel": str(i),
                "isHumanInput": False
            },
            "type": "agentFlow",
            "id": f"conditionAgentAgentflow_0-conditionAgentAgentflow_0-output-{i}-agentAgentflow_{agent_id}-agentAgentflow_{agent_id}"
        })

    return edges

def generate_workflow():
    """Generate the complete Flowise workflow JSON"""
    workflow = {
        "nodes": [],
        "edges": []
    }

    # Add start node
    workflow["nodes"].append(create_start_node())

    # Add condition router
    workflow["nodes"].append(create_condition_node())

    # Add all 8 specialized agents
    for agent_spec in AGENTS:
        workflow["nodes"].append(create_agent_node(agent_spec))

    # Add all edges
    workflow["edges"] = create_edges()

    return workflow

if __name__ == "__main__":
    workflow = generate_workflow()

    # Write to file with nice formatting
    with open("/Users/name/homelab/smartsheets-issue-monitor/smartsheets-issue-monitor-flow.json", "w") as f:
        json.dump(workflow, f, indent=2)

    print(f"✅ Generated workflow with {len(workflow['nodes'])} nodes and {len(workflow['edges'])} edges")
    print(f"✅ File: smartsheets-issue-monitor-flow.json")

    # Validation
    node_count = len(workflow['nodes'])
    edge_count = len(workflow['edges'])
    agent_count = sum(1 for n in workflow['nodes'] if n['data']['name'] == 'agentAgentflow')

    print(f"\n📊 Validation:")
    print(f"   Nodes: {node_count} (expected: 10) {'✅' if node_count == 10 else '❌'}")
    print(f"   Edges: {edge_count} (expected: 9) {'✅' if edge_count == 9 else '❌'}")
    print(f"   Agents: {agent_count} (expected: 8) {'✅' if agent_count == 8 else '❌'}")

    # Check standard tools in all agents
    agents_with_tools = sum(1 for n in workflow['nodes']
                           if n['data']['name'] == 'agentAgentflow'
                           and len(n['data']['inputs'].get('agentTools', [])) == 2)
    print(f"   Standard Tools: {agents_with_tools}/8 agents {'✅' if agents_with_tools == 8 else '❌'}")
