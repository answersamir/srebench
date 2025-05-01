"""
Scenario Loader Module
"""

import os
import json
import yaml


class ScenarioLoader:
    """
    Responsible for locating and reading all the raw data files for a single scenario.
    Parses different file formats into structured data representations.
    """

    def __init__(self, storage_config):
        """
        Initializes the ScenarioLoader with storage configuration.

        Args:
            storage_config (dict): Configuration for the scenario data storage location.
        """
        self.storage_config = storage_config
        # Placeholder for storage path, should be derived from storage_config
        self.base_path = storage_config.get("base_path", "./scenarios")

    def load_scenario(self, scenario_id: str) -> dict:
        """
        Loads and parses data for a given scenario ID.

        Args:
            scenario_id (str): The identifier of the scenario to load.

        Returns:
            dict: A structured object containing parsed scenario data.
        """
        scenario_path = os.path.join(self.base_path, scenario_id)
        if not os.path.exists(scenario_path):
            raise FileNotFoundError(
                f"Scenario {scenario_id} not found at {scenario_path}"
            )

        parsed_data = {}

        # Load description.md
        description_path = os.path.join(scenario_path, "description.md")
        if os.path.exists(description_path):
            with open(description_path, "r", encoding="utf-8") as f:
                parsed_data["description"] = f.read()

        # Load state files
        state_path = os.path.join(scenario_path, "state")
        if os.path.exists(state_path):
            parsed_data["state"] = {}
            # Example: Load logs.jsonl
            logs_path = os.path.join(state_path, "logs.jsonl")
            if os.path.exists(logs_path):
                parsed_data["state"]["logs"] = self._load_jsonl(logs_path)
            # Example: Load metrics.json
            metrics_path = os.path.join(state_path, "metrics.json")
            if os.path.exists(metrics_path):
                parsed_data["state"]["metrics"] = self._load_json(metrics_path)
            # Example: Load events.jsonl
            events_path = os.path.join(state_path, "events.jsonl")
            if os.path.exists(events_path):
                parsed_data["state"]["events"] = self._load_jsonl(events_path)
            # Example: Load topology.json
            topology_path = os.path.join(state_path, "topology.json")
            if os.path.exists(topology_path):
                parsed_data["state"]["topology"] = self._load_json(topology_path)
            # Example: Load configuration.yaml
            config_path = os.path.join(state_path, "configuration.yaml")
            if os.path.exists(config_path):
                parsed_data["state"]["configuration"] = self._load_yaml(config_path)

        # Load ground_truth files
        ground_truth_path = os.path.join(scenario_path, "ground_truth")
        if os.path.exists(ground_truth_path):
            parsed_data["ground_truth"] = {}
            # Example: Load root_cause.md
            root_cause_path = os.path.join(ground_truth_path, "root_cause.md")
            if os.path.exists(root_cause_path):
                with open(root_cause_path, "r", encoding="utf-8") as f:
                    parsed_data["ground_truth"]["root_cause"] = f.read()
            # Example: Load causal_graph.json
            causal_graph_path = os.path.join(ground_truth_path, "causal_graph.json")
            if os.path.exists(causal_graph_path):
                parsed_data["ground_truth"]["causal_graph"] = self._load_json(
                    causal_graph_path
                )
            # Example: Load resolution.md
            resolution_path = os.path.join(ground_truth_path, "resolution.md")
            if os.path.exists(resolution_path):
                with open(resolution_path, "r", encoding="utf-8") as f:
                    parsed_data["ground_truth"]["resolution"] = f.read()
            # Example: Load metadata.json
            metadata_path = os.path.join(ground_truth_path, "metadata.json")
            if os.path.exists(metadata_path):
                parsed_data["ground_truth"]["metadata"] = self._load_json(metadata_path)

        return parsed_data

    def _load_jsonl(self, file_path: str) -> list:
        """Loads a JSONL file."""

        data = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    data.append(json.loads(line))
        return data

    def _load_json(self, file_path: str) -> dict:
        """Loads a JSON file."""

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_yaml(self, file_path: str) -> dict:
        """Loads a YAML file."""

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}


# Example Usage (for testing purposes)
if __name__ == "__main__":
    loader = ScenarioLoader(storage_config={"base_path": "../scenarios"})
    try:
        scenario_data = loader.load_scenario("scenario_cpu_limit_001")
        print("Successfully loaded scenario_cpu_limit_001")
        # print(scenario_data) # Uncomment to see loaded data
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
