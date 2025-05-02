from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an AI SRE agent. Analyze the provided scenario state and identify the root cause, causal chain, and resolution.",
        ),
        (
            "human",
            """Analyze the following scenario state and provide the root cause, causal chain, and resolution in the specified JSON format.

Scenario State:
{scenario_state}

Output Format:
{{
  "root_cause": {{
    "type": "string",
    "resource_type": "string", // e.g., CPU, Memory, Disk
    "component": {{
      "kind": "string", // e.g., Deployment, Pod, Service
      "name": "string", // Name of the component
      "namespace": "string" // Kubernetes namespace
    }},
    "details": "string" // Text description of the root cause
  }},
  "causal_graph": {{
    "nodes": [
      {{
        "id": "string", // Unique node identifier
        "label": "string", // Human-readable label for the node
        "type": "string" // e.g., Configuration, Symptom, ResourceState, UserImpact
      }}
      // ... more nodes
    ],
    "edges": [
      {{
        "source": "string", // ID of the source node
        "target": "string", // ID of the target node
        "relation": "string" // e.g., CAUSES, CONTRIBUTES_TO
      }}
      // ... more edges
    ]
  }},
  "resolution": {{
    "action_type": "string", // e.g., Update Configuration, Restart Pod, Scale Deployment
    "target_component": {{
      "kind": "string",
      "name": "string",
      "namespace": "string"
    }},
    "details": "string" // Text description of the resolution steps
  }}
}}
""",
        ),
    ]
)
