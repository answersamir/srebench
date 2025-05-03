import unittest
import os
import json
import yaml
import tempfile
import shutil

# Assuming the ScenarioLoader class is in eval_pipeline/scenario_loader.py
# Add the parent directory to the path to import the module
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from eval_pipeline.scenario_loader import ScenarioLoader


class TestScenarioLoader(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.scenarios_base_path = os.path.join(self.test_dir, "scenarios")
        os.makedirs(self.scenarios_base_path)

        self.scenario_id_full = "scenario_full"
        self.scenario_full_path = os.path.join(
            self.scenarios_base_path, self.scenario_id_full
        )
        self._create_full_scenario(self.scenario_full_path)

        self.scenario_id_partial = "scenario_partial"
        self.scenario_partial_path = os.path.join(
            self.scenarios_base_path, self.scenario_id_partial
        )
        self._create_partial_scenario(self.scenario_partial_path)

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def _create_full_scenario(self, scenario_path):
        """Helper to create a dummy scenario with all files."""
        os.makedirs(os.path.join(scenario_path, "state"))
        os.makedirs(os.path.join(scenario_path, "ground_truth"))

        with open(os.path.join(scenario_path, "description.md"), "w") as f:
            f.write("Full scenario description.")
        with open(os.path.join(scenario_path, "state", "logs.jsonl"), "w") as f:
            f.write('{"timestamp": "t1", "message": "log1"}\n')
            f.write('{"timestamp": "t2", "message": "log2"}\n')
        with open(os.path.join(scenario_path, "state", "metrics.json"), "w") as f:
            json.dump({"cpu": [10, 20], "mem": [30, 40]}, f)
        with open(os.path.join(scenario_path, "state", "events.jsonl"), "w") as f:
            f.write('{"time": "e1", "type": "alert"}\n')
        with open(os.path.join(scenario_path, "state", "topology.json"), "w") as f:
            json.dump({"nodes": ["app", "db"]}, f)
        with open(os.path.join(scenario_path, "state", "configuration.yaml"), "w") as f:
            yaml.dump({"limit": 100, "timeout": 5}, f)
        with open(
            os.path.join(scenario_path, "ground_truth", "root_cause.md"), "w"
        ) as f:
            f.write("The root cause.")
        with open(
            os.path.join(scenario_path, "ground_truth", "causal_graph.json"), "w"
        ) as f:
            json.dump({"cause": "effect"}, f)
        with open(
            os.path.join(scenario_path, "ground_truth", "resolution.md"), "w"
        ) as f:
            f.write("The resolution steps.")
        with open(
            os.path.join(scenario_path, "ground_truth", "metadata.json"), "w"
        ) as f:
            json.dump({"difficulty": "easy"}, f)

    def _create_partial_scenario(self, scenario_path):
        """Helper to create a dummy scenario with missing files."""
        os.makedirs(os.path.join(scenario_path, "state"))
        os.makedirs(os.path.join(scenario_path, "ground_truth"))
        # Only create description and one state/ground_truth file each
        with open(os.path.join(scenario_path, "description.md"), "w") as f:
            f.write("Partial scenario description.")
        with open(os.path.join(scenario_path, "state", "logs.jsonl"), "w") as f:
            f.write('{"message": "only logs"}\n')
        with open(
            os.path.join(scenario_path, "ground_truth", "root_cause.md"), "w"
        ) as f:
            f.write("Only root cause.")

    def _assert_full_scenario_data(self, scenario_data):
        """Helper to assert the content of a full scenario."""
        self.assertIn("description", scenario_data)
        self.assertEqual(scenario_data["description"], "Full scenario description.")

        self.assertIn("state", scenario_data)
        self.assertIn("logs", scenario_data["state"])
        self.assertEqual(
            scenario_data["state"]["logs"],
            [
                {"timestamp": "t1", "message": "log1"},
                {"timestamp": "t2", "message": "log2"},
            ],
        )
        self.assertIn("metrics", scenario_data["state"])
        self.assertEqual(
            scenario_data["state"]["metrics"], {"cpu": [10, 20], "mem": [30, 40]}
        )
        self.assertIn("events", scenario_data["state"])
        self.assertEqual(
            scenario_data["state"]["events"], [{"time": "e1", "type": "alert"}]
        )
        self.assertIn("topology", scenario_data["state"])
        self.assertEqual(scenario_data["state"]["topology"], {"nodes": ["app", "db"]})
        self.assertIn("configuration", scenario_data["state"])
        self.assertEqual(
            scenario_data["state"]["configuration"], {"limit": 100, "timeout": 5}
        )

        self.assertIn("ground_truth", scenario_data)
        self.assertIn("root_cause", scenario_data["ground_truth"])
        self.assertEqual(scenario_data["ground_truth"]["root_cause"], "The root cause.")
        self.assertIn("causal_graph", scenario_data["ground_truth"])
        self.assertEqual(
            scenario_data["ground_truth"]["causal_graph"], {"cause": "effect"}
        )
        self.assertIn("resolution", scenario_data["ground_truth"])
        self.assertEqual(
            scenario_data["ground_truth"]["resolution"], "The resolution steps."
        )
        self.assertIn("metadata", scenario_data["ground_truth"])
        self.assertEqual(
            scenario_data["ground_truth"]["metadata"], {"difficulty": "easy"}
        )

    def _assert_partial_scenario_data(self, scenario_data):
        """Helper to assert the content of a partial scenario."""
        self.assertIn("description", scenario_data)
        self.assertEqual(scenario_data["description"], "Partial scenario description.")

        self.assertIn("state", scenario_data)
        self.assertIn("logs", scenario_data["state"])
        self.assertEqual(scenario_data["state"]["logs"], [{"message": "only logs"}])
        # Check that missing state files are not present or are empty dicts/lists
        self.assertNotIn("metrics", scenario_data["state"])
        self.assertNotIn("events", scenario_data["state"])
        self.assertNotIn("topology", scenario_data["state"])
        self.assertNotIn("configuration", scenario_data["state"])

        self.assertIn("ground_truth", scenario_data)
        self.assertIn("root_cause", scenario_data["ground_truth"])
        self.assertEqual(
            scenario_data["ground_truth"]["root_cause"], "Only root cause."
        )
        # Check that missing ground truth files are not present or are empty dicts/lists
        self.assertNotIn("causal_graph", scenario_data["ground_truth"])
        self.assertNotIn("resolution", scenario_data["ground_truth"])
        self.assertNotIn("metadata", scenario_data["ground_truth"])

    def test_load_scenario_full(self):
        """Test loading a scenario with all expected files."""
        loader = ScenarioLoader(storage_config={"base_path": self.scenarios_base_path})
        scenario_data = loader.load_scenario(self.scenario_id_full)
        self._assert_full_scenario_data(scenario_data)

    def test_load_scenario_partial(self):
        """Test loading a scenario with some missing optional files."""
        loader = ScenarioLoader(storage_config={"base_path": self.scenarios_base_path})
        scenario_data = loader.load_scenario(self.scenario_id_partial)
        self._assert_partial_scenario_data(scenario_data)

    def test_load_nonexistent_scenario(self):
        """Test loading a scenario ID that does not exist."""
        loader = ScenarioLoader(storage_config={"base_path": self.scenarios_base_path})
        nonexistent_id = "scenario_nonexistent"

        with self.assertRaises(FileNotFoundError) as cm:
            loader.load_scenario(nonexistent_id)

        self.assertIn(f"Scenario {nonexistent_id} not found", str(cm.exception))

    def test_load_jsonl_empty(self):
        """Test loading an empty JSONL file."""
        empty_jsonl_path = os.path.join(self.test_dir, "empty.jsonl")
        with open(empty_jsonl_path, "w"):
            pass  # Create an empty file

        loader = ScenarioLoader(storage_config={"base_path": self.scenarios_base_path})
        # Use the private method directly for isolated testing
        loaded_data = loader._load_jsonl(empty_jsonl_path)
        self.assertEqual(loaded_data, [])

    def test_load_json_empty(self):
        """Test loading an empty JSON file (should ideally be {} or [])."""
        # Note: An empty file is not valid JSON, but an empty object/array is.
        # The current _load_json returns {} for non-existent or empty files.
        # Let's test with an empty JSON object.
        empty_json_path = os.path.join(self.test_dir, "empty.json")
        with open(empty_json_path, "w") as f:
            json.dump({}, f)

        loader = ScenarioLoader(storage_config={"base_path": self.scenarios_base_path})
        loaded_data = loader._load_json(empty_json_path)
        self.assertEqual(loaded_data, {})

    def test_load_yaml_empty(self):
        """Test loading an empty YAML file."""
        empty_yaml_path = os.path.join(self.test_dir, "empty.yaml")
        with open(empty_yaml_path, "w"):
            pass  # Create an empty file

        loader = ScenarioLoader(storage_config={"base_path": self.scenarios_base_path})
        loaded_data = loader._load_yaml(empty_yaml_path)
        # PyYAML loads empty files as None
        self.assertIsNone(loaded_data)


if __name__ == "__main__":
    unittest.main()
