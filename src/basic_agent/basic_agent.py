"""
BasicLLMAgent Class
"""

import json
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from prompts.basic_agent_prompts import prompt as basic_agent_prompt


class BasicLLMAgent:
    """
    A basic LLM agent using Langchain to process scenario state and generate
    ground truth output (root cause, causal chain, resolution).
    """

    def __init__(self, llm=None):
        """
        Initializes the BasicLLMAgent with a specific LLM model.

        Args:
            llm: A pre-initialized LLM instance.
        """
        self.model = llm

        # Use the imported prompt template
        self.prompt = basic_agent_prompt

        # Define the Langchain processing chain
        self.chain = (
            {"scenario_state": RunnablePassthrough()}
            | self.prompt  # Use the imported prompt
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
            # Clean potential markdown code fences
            if llm_output_str.startswith("```json"):
                llm_output_str = llm_output_str.strip()[7:-3].strip()
            elif llm_output_str.startswith("```"):
                llm_output_str = llm_output_str.strip()[3:-3].strip()

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
    # Set the GOOGLE_GENAI_API_KEY environment variable before running this example
    # os.environ["GOOGLE_GENAI_API_KEY"] = "YOUR_API_KEY"

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
        print("Please set the GOOGLE_GENAI_API_KEY environment variable.")
