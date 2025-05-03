"""
This module initializes the evaluation pipeline components for the scenario evaluator.
"""

from basic_agent.basic_agent_adapter import BasicLLMAgentAdapter
from eval_pipeline.efficiency_evaluator import EfficiencyEvaluator
from eval_pipeline.evaluation_writer import ScenarioEvaluationWriter
from eval_pipeline.result_comparator import ResultComparator
from eval_pipeline.scenario_evaluator_orchestrator import ScenarioEvaluatorOrchestrator
from eval_pipeline.scenario_loader import ScenarioLoader
import llm_provider


def initialize_evaluation_components(
    scenario_base_path: str,
) -> ScenarioEvaluatorOrchestrator:
    """
    Initializes and returns the core components for the evaluation pipeline.

    Returns:
        ScenarioEvaluatorOrchestrator: The configured orchestrator instance.

    Raises:
        Exception: If any component fails to initialize.
    """
    print("Initializing evaluation components...")
    # Ensure the base path is correct relative to the project root
    storage_config = {"base_path": scenario_base_path}
    # Placeholder agent config - replace with actual configuration if needed

    loader = ScenarioLoader(storage_config=storage_config)
    llm = llm_provider.setup_llm()
    # Replace LLMAgentAdapter if a different agent implementation is required
    agent_config = {"llm": llm}
    agent_adapter = BasicLLMAgentAdapter(agent_config=agent_config)
    comparator = ResultComparator()
    evaluator = EfficiencyEvaluator()
    evaluation_writer = ScenarioEvaluationWriter(base_dir="bench_runs")

    orchestrator = ScenarioEvaluatorOrchestrator(
        scenario_loader=loader,
        agent_interface=agent_adapter,
        result_comparator=comparator,
        efficiency_evaluator=evaluator,
        evaluation_writer=evaluation_writer,
    )
    print("Components initialized successfully.")
    return orchestrator
