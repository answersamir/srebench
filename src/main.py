"""
Main entry point for the SRE Benchmark evaluation pipeline.
"""

import json
import logging
import os

from orechestrator_builder import initialize_evaluation_components

# Define the base path for scenarios relative to the project root
SCENARIOS_BASE_PATH = "scenarios"


def main():
    """
    Orchestrates the SRE Benchmark evaluation pipeline.

    Initializes necessary components, loads a scenario, runs the evaluation,
    and prints the results.
    """
    print("Starting SRE Benchmark Evaluation Pipeline...")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    # --- Initialize Components ---
    try:
        orchestrator = initialize_evaluation_components(base_path=SCENARIOS_BASE_PATH)
    except Exception as e:
        print(f"Fatal Error: Could not initialize evaluation components: {e}")
        return  # Exit if components fail to initialize

    # --- Scenario Selection ---
    # TODO: Implement logic to dynamically select or iterate through scenarios.
    # Using a default scenario ID for this example.
    scenario_id_to_evaluate = "scenario_001"
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
