from abc import ABC, abstractmethod


class AgentInterface(ABC):
    """
    Abstract base class for interacting with AI SRE agents.
    Provides a standard way for the evaluation pipeline to interact with any agent.
    """

    def __init__(self, agent_config):
        """
        Initializes the AgentInterface with agent-specific configuration.

        Args:
            agent_config (dict): Configuration specific to the agent (e.g., API key, endpoint).
        """
        self.agent_config = agent_config

    @abstractmethod
    def interact_with_agent(self, scenario_data: dict) -> dict:
        """
        Translates structured scenario data into agent-specific input,
        calls the agent, and translates the agent's response back into
        a standard structured format.

        Args:
            scenario_data (dict): Structured data from the ScenarioLoader
                                  (specifically description and state).

        Returns:
            dict: A standard structured object representing the agent's identified
                  root cause, causal chain, and proposed/executed resolution.
                  Expected keys: 'root_cause', 'causal_chain', 'resolution'.
        """
        pass


class LLMAgentAdapter(AgentInterface):
    """
    Concrete implementation of AgentInterface for interacting with an LLM agent.
    """

    def interact_with_agent(self, scenario_data: dict) -> dict:
        """
        Crafts a prompt for an LLM using scenario data and parses the response.

        Args:
            scenario_data (dict): Structured data from the ScenarioLoader.

        Returns:
            dict: Standardized agent output.
        """
        print("LLMAgentAdapter: Crafting prompt and interacting with LLM...")
        # Placeholder for prompt crafting and LLM API call logic
        # This is where you would format scenario_data into a prompt string
        # and send it to an LLM API (e.g., OpenAI, Gemini, etc.)

        # Simulate agent response parsing
        # In a real implementation, you would parse the LLM's text response
        # to extract the root cause, causal chain, and resolution.
        simulated_agent_output = {
            "root_cause": "Simulated root cause from LLM.",
            "causal_chain": ["step1", "step2"],
            "resolution": "Simulated resolution from LLM.",
        }

        print("LLMAgentAdapter: Received and parsed simulated LLM response.")
        return simulated_agent_output


# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Example scenario data structure (simplified)
    example_scenario_data = {
        "description": "This is a test scenario.",
        "state": {
            "logs": [{"timestamp": "...", "message": "..."}],
            "metrics": {"cpu": [...], "memory": [...]},
            # ... other state data
        },
    }

    # Example agent configuration
    example_agent_config = {
        "model_name": "gpt-4o",
        "api_key": "sk-...",  # In a real app, load from config/env vars, not hardcoded
    }

    # Instantiate and use the adapter
    llm_adapter = LLMAgentAdapter(agent_config=example_agent_config)
    agent_results = llm_adapter.interact_with_agent(example_scenario_data)

    print("\nSimulated Agent Results:")
    print(agent_results)
