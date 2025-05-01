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
  "root_cause": "string",
  "causal_chain": ["string", "string", ...],
  "resolution": "string"
}}
""",
        ),
    ]
)
