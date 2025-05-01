"""
Main entry point for the SRE Benchmark evaluation pipeline.
"""

import json
import os
from eval_pipeline.scenario_loader import ScenarioLoader
from basic_agent.basic_agent_adapter import BasicLLMAgentAdapter
from eval_pipeline.result_comparator import ResultComparator
from eval_pipeline.efficiency_evaluator import EfficiencyEvaluator
from eval_pipeline.scenario_evaluator_orchestrator import (
    ScenarioEvaluatorOrchestrator,
)
import llm_provider

# Define the base path for scenarios relative to the project root
SCENARIOS_BASE_PATH = "scenarios"


def main():
    """
    Orchestrates the SRE Benchmark evaluation pipeline.

    Initializes necessary components, loads a scenario, runs the evaluation,
    and prints the results.
    """
    print("Starting SRE Benchmark Evaluation Pipeline...")

    # --- Configuration ---
    # Ensure the base path is correct relative to the project root
    storage_config = {"base_path": SCENARIOS_BASE_PATH}
    # Placeholder agent config - replace with actual configuration if needed

    # --- Component Instantiation ---
    try:
        print("Initializing evaluation components...")
        loader = ScenarioLoader(storage_config=storage_config)
        llm = llm_provider.setup_llm()
        # Replace LLMAgentAdapter if a different agent implementation is required
        agent_config = {"llm": llm}
        agent_adapter = BasicLLMAgentAdapter(agent_config=agent_config)
        comparator = ResultComparator()
        evaluator = EfficiencyEvaluator()

        orchestrator = ScenarioEvaluatorOrchestrator(
            scenario_loader=loader,
            agent_interface=agent_adapter,
            result_comparator=comparator,
            efficiency_evaluator=evaluator,
        )
        print("Components initialized successfully.")

    except Exception as e:
        print(f"Error initializing components: {e}")
        # Consider more specific exception handling if needed
        return  # Exit if components fail to initialize

    # --- Scenario Selection ---
    # TODO: Implement logic to dynamically select or iterate through scenarios.
    # Using a default scenario ID for this example.
    scenario_id_to_evaluate = "scenario_cpu_limit_001"
    print(f"Selected scenario for evaluation: {scenario_id_to_evaluate}")

    # --- Run Evaluation ---
    try:
        print(f"\nRunning evaluation for scenario: {scenario_id_to_evaluate}...")
        evaluation_results = orchestrator.evaluate_scenario(scenario_id_to_evaluate)
        print("Evaluation completed.")

        # --- Display Results ---
        print("\n--- Evaluation Results ---")
        # Use json.dumps for pretty printing the results dictionary
        print(json.dumps(evaluation_results, indent=2))
        print(json.dumps)
        print("--- End of Results ---")

    except FileNotFoundError:
        abs_path = os.path.abspath(SCENARIOS_BASE_PATH)
        print(f"\nError: Scenario '{scenario_id_to_evaluate}' not found.")
        print(f"Looked in directory: {abs_path}")
        print("Please ensure the scenario exists and the path is correct.")
    except Exception as e:
        # Catch other potential errors during evaluation
        print(f"\nAn error occurred during evaluation: {e}")

    print("\nSRE Benchmark Evaluation Pipeline finished.")


if __name__ == "__main__":
    main()
