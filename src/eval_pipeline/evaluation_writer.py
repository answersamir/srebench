"""
Handles writing evaluation results and ground truth for benchmark scenarios.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union


class ScenarioEvaluationWriter:
    """Handles writing evaluation results and ground truth for benchmark scenarios."""

    def __init__(self, base_dir: Union[str, Path] = "bench_runs"):
        """
        Initializes the writer and sets up the main run directory.

        Args:
            base_dir: The base directory to store benchmark runs. Defaults to 'bench_runs'.
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)  # Ensure base directory exists

    def _create_base_dir(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.base_dir / timestamp
        self.run_dir.mkdir()  # Create the timestamped run directory

    def _get_scenario_path(self, scenario_name: str) -> Path:
        """Gets the path for a specific scenario's results directory."""
        if not scenario_name:
            raise ValueError("Scenario name cannot be empty.")
        # Basic sanitization - replace potentially problematic characters
        safe_scenario_name = "".join(
            c if c.isalnum() or c in ("-", "_") else "_" for c in scenario_name
        )
        return self.run_dir / safe_scenario_name

    def _setup_scenario_dir(self, scenario_name: str) -> Path:
        """
        Creates a directory for a specific scenario within the current run.

        Args:
            scenario_name: The name of the scenario.

        Returns:
            The path to the created scenario directory.

        Raises:
            ValueError: If scenario_name is empty.
            OSError: If directory creation fails for reasons other than existence.
        """
        scenario_path = self._get_scenario_path(scenario_name)
        try:
            scenario_path.mkdir(parents=True, exist_ok=True)
            # print(f"Setup directory for scenario '{scenario_name}': {scenario_path}")
        except OSError as e:
            print(f"Error creating directory {scenario_path}: {e}")
            raise  # Re-raise the error after logging
        return scenario_path

    def write_results(self, scenario_name: str, score_data: Dict[str, Any]) -> None:
        """
        Writes evaluation results (scores) to a JSON file in the scenario's directory.

        Ensures the scenario directory exists before writing.

        Args:
            scenario_name: The name of the scenario.
            score_data: A dictionary containing the evaluation scores.

        Raises:
            ValueError: If scenario_name is empty.
            IOError: If writing the file fails.
            TypeError: If score_data is not JSON serializable.
            OSError: If directory creation fails.
        """
        self._create_base_dir()  # Ensure base directory is created
        scenario_path = self._setup_scenario_dir(scenario_name)  # Ensure dir exists
        results_path = scenario_path / "results.json"

        try:
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(score_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error writing results file {results_path}: {e}")
            raise  # Re-raise the error after logging
        except TypeError as e:
            print(f"Error serializing results data to JSON for {results_path}: {e}")
            raise  # Re-raise the error after logging
