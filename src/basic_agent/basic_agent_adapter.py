import os
from eval_pipeline.agent_interface import AgentInterface
from basic_agent.basic_agent import BasicLLMAgent


class BasicLLMAgentAdapter(AgentInterface):
    """
    Adapter for BasicLLMAgent to conform to the AgentInterface.
    """

    def __init__(self, agent_config: dict):
        """
        Initializes the adapter and the underlying BasicLLMAgent.

        Args:
            agent_config (dict): Configuration specific to the agent.
                                 Expected to contain 'model_name'.
        """
        super().__init__(agent_config)
        model_name = self.agent_config.get("model_name", "gpt-4o")
        self.basic_agent = BasicLLMAgent(model_name=model_name)

    def interact_with_agent(self, scenario_data: dict) -> dict:
        """
        Translates structured scenario data into BasicLLMAgent input,
        calls the agent, and returns the agent's response.

        Args:
            scenario_data (dict): Structured data from the ScenarioLoader
                                  (specifically description and state).

        Returns:
            dict: A standard structured object representing the agent's identified
                  root cause, causal chain, and proposed/executed resolution.
                  Expected keys: 'root_cause', 'causal_chain', 'resolution'.
        """
        # The BasicLLMAgent expects the scenario state directly.
        # We extract the 'state' part from the scenario_data.
        scenario_state = scenario_data.get("state", {})

        # Call the underlying BasicLLMAgent
        agent_output = self.basic_agent.process_scenario_state(scenario_state)

        # The BasicLLMAgent is designed to return output in the desired format,
        # so we can return it directly.
        return agent_output


if __name__ == "__main__":
    # Example Usage (for testing purposes)
    # Set the OPENAI_API_KEY environment variable before running this example
    # os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

    example_scenario_data = {
        "description": "This is a test scenario.",
        "state": {
            "logs": [{"timestamp": "...", "message": "CPU usage high"}],
            "metrics": {"cpu": [90, 95, 98], "memory": [40, 42, 45]},
            "topology": {"service_a": "running", "service_b": "running"},
        },
    }

    example_agent_config = {
        "model_name": "gpt-4o",
        # "api_key": "sk-...", # API key should be in environment variables
    }

    try:
        adapter = BasicLLMAgentAdapter(agent_config=example_agent_config)
        agent_results = adapter.interact_with_agent(example_scenario_data)

        print("\nAgent Results:")
        print(agent_results)

    except ValueError as e:
        print(f"Error: {e}")
        print("Please set the OPENAI_API_KEY environment variable.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
