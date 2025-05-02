"""
ScenarioEvaluatorOrchestrator orchestrates the evaluation process for a single scenario.
It calls the ScenarioLoader, passes data to the AgentInterface,
and feeds results into the ResultComparator and EfficiencyEvaluator.
"""

import json

from .scenario_loader import ScenarioLoader
from .agent_interface import AgentInterface
from .result_comparator import ResultComparator
from .efficiency_evaluator import EfficiencyEvaluator
from .agent_interface import LLMAgentAdapter  # Using the concrete adapter
from .evaluation_writer import ScenarioEvaluationWriter


class ScenarioEvaluatorOrchestrator:
    """
    Orchestrates the evaluation process for a single scenario.
    Calls the ScenarioLoader, passes data to the AgentInterface,
    and feeds results into the ResultComparator and EfficiencyEvaluator.
    Aggregates scores for the single scenario.
    """

    def __init__(
        self,
        scenario_loader: ScenarioLoader,
        agent_interface: AgentInterface,
        result_comparator: ResultComparator,
        efficiency_evaluator: EfficiencyEvaluator,
        evaluation_writer: ScenarioEvaluationWriter,
    ):
        """
        Initializes the ScenarioEvaluatorOrchestrator with instances of other components.

        Args:
            scenario_loader (ScenarioLoader): Instance of the ScenarioLoader.
            agent_interface (AgentInterface): Instance of the AgentInterface.
            result_comparator (ResultComparator): Instance of the ResultComparator.
            efficiency_evaluator (EfficiencyEvaluator): Instance of the EfficiencyEvaluator.
            evaluation_writer (ScenarioEvaluationWriter): Instance of the EvaluationWriter.
        """
        self.scenario_loader = scenario_loader
        self.agent_interface = agent_interface
        self.result_comparator = result_comparator
        self.efficiency_evaluator = efficiency_evaluator
        self.evaluation_writer = evaluation_writer

    def evaluate_scenario(self, scenario_id: str) -> dict:
        """
        Runs the evaluation process for a single scenario.

        Args:
            scenario_id (str): The identifier of the scenario to evaluate.

        Returns:
            dict: A dictionary containing all the evaluation results.
        """
        print(f"Orchestrator: Starting evaluation for scenario: {scenario_id}")
        scenario_results = {"scenario_id": scenario_id}

        try:
            # 1. Load Scenario Data
            print("Orchestrator: Loading scenario data...")
            scenario_data = self.scenario_loader.load_scenario(scenario_id)
            scenario_results["loaded_data_summary"] = {
                "description_loaded": "description" in scenario_data,
                "state_loaded": "state" in scenario_data,
                "ground_truth_loaded": "ground_truth" in scenario_data,
            }
            scenario_results["loaded_data"] = scenario_data

            # 2. Setup Scenario Directory and Interact with Agent
            print("Orchestrator: Setting up scenario directory...")
            self.evaluation_writer.setup_scenario_dir(scenario_id)

            print("Orchestrator: Interacting with agent...")
            self.efficiency_evaluator.start_timer()  # Start timer before agent interaction
            agent_output = self.agent_interface.interact_with_agent(scenario_data)
            # Stop timer and get score immediately after agent interaction
            efficiency_score = self.efficiency_evaluator.stop_timer_and_evaluate()
            scenario_results["agent_output"] = agent_output

            # Write agent output (considered ground truth for this run)
            print("Orchestrator: Writing agent output...")
            try:
                agent_output_content = json.dumps(agent_output, indent=2)
                self.evaluation_writer.write_ground_truth(
                    scenario_id, "agent_output.json", agent_output_content
                )
            except TypeError as e:
                print(
                    f"Orchestrator Warning: Could not serialize agent output to JSON: {e}"
                )
                # Fallback: Write as string representation
                self.evaluation_writer.write_ground_truth(
                    scenario_id, "agent_output.txt", str(agent_output)
                )

            # 3. Compare Results
            print("Orchestrator: Comparing agent output with ground truth...")
            if "ground_truth" in scenario_data:
                comparison_scores = self.result_comparator.compare(
                    agent_output=agent_output,
                    ground_truth=scenario_data["ground_truth"],
                )
                scenario_results["comparison_scores"] = comparison_scores
            else:
                print("Orchestrator: Ground truth not available, skipping comparison.")
                scenario_results["comparison_scores"] = {
                    "error": "Ground truth not available"
                }

            # 4. Evaluate Efficiency
            print("Orchestrator: Evaluating efficiency...")
            # Efficiency score was obtained when timer was stopped (line 71)
            scenario_results["efficiency_score"] = efficiency_score

        except FileNotFoundError as e:
            print(f"Orchestrator Error: {e}")
            scenario_results["error"] = str(e)
        except Exception as e:
            print(f"Orchestrator Error: An unexpected error occurred: {e}")
            scenario_results["error"] = str(e)

        print(f"Orchestrator: Finished evaluation for scenario: {scenario_id}")

        # 5. Write Final Results
        print("Orchestrator: Writing final results...")
        self.evaluation_writer.write_results(scenario_id, scenario_results)

        return scenario_results


# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Instantiate skeleton components
    # Note: In a real application, these would be properly configured

    # Dummy configurations
    dummy_storage_config = {"base_path": "src/scenarios"}  # Relative to workspace root
    dummy_agent_config = {"model_name": "dummy"}

    # Instantiate components
    loader = ScenarioLoader(storage_config=dummy_storage_config)
    agent_adapter = LLMAgentAdapter(agent_config=dummy_agent_config)
    comparator = ResultComparator()
    evaluator = EfficiencyEvaluator()
    writer = ScenarioEvaluationWriter(base_dir="bench_runs")  # Instantiate writer

    # Instantiate orchestrator
    orchestrator = ScenarioEvaluatorOrchestrator(
        scenario_loader=loader,
        agent_interface=agent_adapter,
        result_comparator=comparator,
        efficiency_evaluator=evaluator,
        evaluation_writer=writer,  # Pass writer
    )

    # Run evaluation for a dummy scenario ID
    # Use scenario_cpu_limit_002 as it exists in the provided file list
    scenario_id_to_evaluate = "scenario_cpu_limit_002"
    evaluation_results = orchestrator.evaluate_scenario(scenario_id_to_evaluate)

    print("\nSingle Scenario Evaluation Results:")
    import json  # Keep import here for standalone execution

    print(json.dumps(evaluation_results, indent=2))
