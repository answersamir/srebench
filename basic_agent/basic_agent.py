import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough


class BasicLLMAgent:
    """
    A basic LLM agent using Langchain to process scenario state and generate
    ground truth output (root cause, causal chain, resolution).
    """

    def __init__(self, model_name: str = "gpt-4o", llm=None):
        """
        Initializes the BasicLLMAgent with a specific LLM model.

        Args:
            model: The LLM model to use.

        Args:
            model_name (str): The name of the LLM model to use.
        """
        # Ensure API key is loaded from environment variables
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        self.model = llm or ChatOpenAI(model=model_name)

        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages(
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

        # Define the Langchain processing chain
        self.chain = (
            {"scenario_state": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )

    def process_scenario_state(self, scenario_state: dict) -> dict:
        """
        Processes the scenario state using the LLM and returns the structured output.

        Args:
            scenario_state (dict): The structured scenario state data.

        Returns:
            dict: A dictionary containing 'root_cause', 'causal_chain', and 'resolution'.
        """
        # Convert scenario_state dict to a string for the prompt
        scenario_state_str = str(scenario_state)

        # Invoke the Langchain chain
        llm_output_str = self.chain.invoke({"scenario_state": scenario_state_str})

        # TODO: Implement robust parsing of the LLM output string into the desired JSON format.
        # This is a placeholder and needs proper error handling and parsing logic.
        try:
            # Assuming the LLM output is a valid JSON string
            import json

            parsed_output = json.loads(llm_output_str)
            return parsed_output
        except json.JSONDecodeError:
            print(f"Warning: Could not parse LLM output as JSON: {llm_output_str}")
            # Return a default or error structure if parsing fails
            return {
                "root_cause": "Parsing failed.",
                "causal_chain": [],
                "resolution": "Parsing failed.",
            }


if __name__ == "__main__":
    # Example Usage (for testing purposes)
    # Set the OPENAI_API_KEY environment variable before running this example
    # os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

    example_scenario_state = {
        "logs": [{"timestamp": "...", "message": "CPU usage high"}],
        "metrics": {"cpu": [90, 95, 98], "memory": [40, 42, 45]},
        "topology": {"service_a": "running", "service_b": "running"},
    }

    try:
        agent = BasicLLMAgent()
        results = agent.process_scenario_state(example_scenario_state)
        print("\nAgent Results:")
        print(results)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set the OPENAI_API_KEY environment variable.")
