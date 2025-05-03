"""
This module serves the web UI for the SREBench results viewer, handling requests
for custom scenarios and serving static files.
"""

import json
import yaml
import io
from typing import Dict, Any, List, Optional

# Removed duplicate import: from typing import Dict, Any, List
import logging  # Added for logging

import os
from flask import Flask, request, jsonify, send_from_directory

# Import the refactored initialization function
from .main import initialize_evaluation_components

# No longer need the standalone import alias

app = Flask(__name__)

# --- Global Orchestrator Instance ---
# Initialize components once when the app starts.
# This avoids re-initializing the LLM and other components on every request.
# Note: In a production scenario with multiple workers, consider if shared state
# needs more sophisticated handling (e.g., lazy initialization per worker).
try:
    orchestrator = initialize_evaluation_components()
except Exception as e:
    # Log the error and potentially prevent the app from starting
    # or set orchestrator to None and handle it in the request.
    logging.critical(f"Failed to initialize evaluation components on startup: {e}")
    orchestrator = None  # Indicate initialization failure


def parse_jsonl(jsonl_content: str) -> List[Dict[str, Any]]:
    """Parses a string containing JSONL content."""
    lines = []
    for line in io.StringIO(jsonl_content):
        if line.strip():
            try:
                lines.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in JSONL line: {line.strip()}") from e
    return lines


# --- Static File Serving ---

# Define the path to the results_viewer directory relative to this script's location
# Assuming web_ui.py is in src/ and results_viewer is also in src/
RESULTS_VIEWER_DIR = os.path.join(os.path.dirname(__file__), "results_viewer")
logging.info(f"RESULTS_VIEWER_DIR is set to: {RESULTS_VIEWER_DIR}")


@app.route("/custom")
def serve_custom_scenario():
    """Serves the main custom_scenario.html file."""
    logging.debug(f"Attempting to serve custom_scenario.html from {RESULTS_VIEWER_DIR}")
    return send_from_directory(RESULTS_VIEWER_DIR, "custom_scenario.html")


@app.route("/custom/<path:filename>")
def serve_custom_static(filename):
    """Serves static files (JS, CSS) requested by custom_scenario.html."""
    logging.debug(
        f"Attempting to serve static file {filename} from {RESULTS_VIEWER_DIR}"
    )
    # logging.debug(f"Serving static file: {filename} from directory: {RESULTS_VIEWER_DIR}") # Redundant log
    return send_from_directory(RESULTS_VIEWER_DIR, filename)


# Define the base directory for scenarios relative to this script
SCENARIOS_BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "scenarios")
)
logging.info(f"Scenarios base directory: {SCENARIOS_BASE_DIR}")

# --- Helper Function for Reading Scenario Files ---


def _read_scenario_file(file_path: str) -> Optional[str]:
    """Safely reads the content of a scenario file.

    Args:
        file_path: The absolute path to the file.

    Returns:
        The file content as a string, or None if the file
        doesn't exist or cannot be read.
    """
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            logging.warning(f"Scenario file not found or is not a file: {file_path}")
            return None
    except IOError as e:
        logging.error(f"Error reading scenario file {file_path}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error reading file {file_path}: {e}")
        return None


# --- API Endpoints ---


@app.route("/api/scenarios", methods=["GET"])
def list_scenarios():
    """Lists available scenario IDs based on subdirectories."""
    logging.info(f"Request received for /api/scenarios. Scanning {SCENARIOS_BASE_DIR}")
    if not os.path.exists(SCENARIOS_BASE_DIR) or not os.path.isdir(SCENARIOS_BASE_DIR):
        logging.error(f"Scenarios directory not found: {SCENARIOS_BASE_DIR}")
        return jsonify({"error": "Scenarios directory not found on server."}), 500

    try:
        scenario_ids = [
            d
            for d in os.listdir(SCENARIOS_BASE_DIR)
            if os.path.isdir(os.path.join(SCENARIOS_BASE_DIR, d))
        ]
        logging.info(f"Found scenarios: {scenario_ids}")
        return jsonify(scenario_ids)
    except OSError as e:
        logging.error(f"Error reading scenarios directory {SCENARIOS_BASE_DIR}: {e}")
        return jsonify({"error": "Could not read scenarios directory."}), 500
    except Exception as e:
        logging.error(f"Unexpected error listing scenarios: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route("/api/scenarios/<scenario_id>", methods=["GET"])
def get_scenario_data(scenario_id: str):
    """Retrieves the content of all files for a given scenario."""
    logging.info(f"Request received for /api/scenarios/{scenario_id}")

    # Basic input validation for scenario_id to prevent path traversal
    if (
        not scenario_id
        or ".." in scenario_id
        or "/" in scenario_id
        or "\\" in scenario_id
    ):
        logging.warning(f"Invalid scenario_id requested: {scenario_id}")
        return jsonify({"error": "Invalid scenario ID format."}), 400

    scenario_path = os.path.join(SCENARIOS_BASE_DIR, scenario_id)
    logging.info(f"Constructed scenario path: {scenario_path}")

    if not os.path.exists(scenario_path) or not os.path.isdir(scenario_path):
        logging.warning(f"Scenario directory not found: {scenario_path}")
        return jsonify({"error": f"Scenario '{scenario_id}' not found."}), 404

    # Define the files and their corresponding keys in the response JSON
    files_to_read = {
        "description": "description.md",
        "metadata": "metadata.json",
        "logs": os.path.join("state", "logs.jsonl"),
        "metrics": os.path.join("state", "metrics.json"),
        "topology": os.path.join("state", "topology.json"),
        "configuration": os.path.join("state", "configuration.yaml"),
        "causal_graph": os.path.join("ground_truth", "causal_graph.json"),
        "resolution": os.path.join("ground_truth", "resolution.json"),
        "root_cause": os.path.join("ground_truth", "root_cause.json"),
    }

    scenario_content: Dict[str, Optional[str]] = {}

    logging.info(f"Reading files for scenario: {scenario_id}")
    for key, relative_path in files_to_read.items():
        full_file_path = os.path.join(scenario_path, relative_path)
        content = _read_scenario_file(full_file_path)
        scenario_content[key] = content  # Store content or None if read failed

    # Check if at least one file was successfully read (optional, depends on requirements)
    if all(value is None for value in scenario_content.values()):
        # This might happen if the directory exists but is empty or contains none of the expected files
        logging.warning(
            f"No relevant files found or readable in scenario directory: {scenario_path}"
        )
        # Decide whether to return 404 or an empty object based on desired behavior
        # Returning 404 might be clearer if the expectation is that these files *should* exist
        return (
            jsonify(
                {"error": f"No relevant data files found for scenario '{scenario_id}'."}
            ),
            404,
        )

    logging.info(f"Successfully retrieved data for scenario: {scenario_id}")
    return jsonify(scenario_content)


# --- API Endpoints ---


@app.route("/evaluate", methods=["POST"])
def evaluate_scenario():
    """
    Endpoint to evaluate a custom scenario provided in the request body.
    Expects a JSON payload with scenario details.
    """
    logging.info("Received request to evaluate custom scenario.")
    if orchestrator is None:
        logging.error("Orchestrator not initialized. Cannot evaluate scenario.")
        return (
            jsonify(
                {
                    "error": "Evaluation service is not available due to initialization failure."
                }
            ),
            503,
        )  # Service Unavailable

    if not request.is_json:
        logging.warning("Received non-JSON request for /evaluate endpoint.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    logging.debug(
        "Received scenario data payload."
    )  # Use debug for potentially large data

    # --- Input Validation ---
    required_fields = ["description", "metadata", "state_files", "ground_truth_files"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

    required_state_files = [
        "configuration.yaml",
        "logs.jsonl",
        "metrics.json",
        "topology.json",
    ]
    if not isinstance(data["state_files"], dict) or not all(
        f in data["state_files"] for f in required_state_files
    ):
        return (
            jsonify(
                {
                    "error": f"state_files must be a dict containing keys: {required_state_files}"
                }
            ),
            400,
        )

    required_gt_files = ["causal_graph.json", "resolution.json", "root_cause.json"]
    if not isinstance(data["ground_truth_files"], dict) or not all(
        f in data["ground_truth_files"] for f in required_gt_files
    ):
        return (
            jsonify(
                {
                    "error": f"ground_truth_files must be a dict containing keys: {required_gt_files}"
                }
            ),
            400,
        )

    # --- Parsing ---
    try:
        description = data["description"]
        metadata = data["metadata"]
        state_files_content = data["state_files"]
        ground_truth_files_content = data["ground_truth_files"]

        # Parse state files
        configuration = yaml.safe_load(state_files_content["configuration.yaml"])
        logs = parse_jsonl(state_files_content["logs.jsonl"])
        metrics = state_files_content["metrics.json"]
        topology = state_files_content["topology.json"]

        # Parse ground truth files
        causal_graph = ground_truth_files_content["causal_graph.json"]
        resolution = ground_truth_files_content["resolution.json"]
        root_cause = ground_truth_files_content["root_cause.json"]

    except (json.JSONDecodeError, yaml.YAMLError, ValueError, KeyError) as e:
        logging.error(f"Error parsing input data: {e}", exc_info=True)
        return jsonify({"error": f"Error parsing input data: {e}"}), 400
    except Exception as e:  # Catch unexpected errors during parsing
        logging.error(
            f"An unexpected error occurred during parsing: {e}", exc_info=True
        )
        return (
            jsonify({"error": f"An unexpected error occurred during parsing: {e}"}),
            500,
        )

    # --- Construct scenario_data ---
    scenario_data = {
        "description": description,
        "metadata": metadata,
        "state": {
            "configuration": configuration,
            "logs": logs,
            "metrics": metrics,
            "topology": topology,
        },
        "ground_truth": {
            "causal_graph": causal_graph,
            "resolution": resolution,
            "root_cause": root_cause,
        },
    }

    # --- Evaluation Logic ---
    try:
        # Generate a unique name for this run if desired, or use a default
        custom_run_name = f"custom_run_{request.headers.get('X-Request-ID', 'default')}"

        logging.info(
            f"Calling orchestrator.evaluate_custom_scenario for '{custom_run_name}'"
        )
        # Call the method directly on the orchestrator instance
        evaluation_results = orchestrator.evaluate_custom_scenario(
            scenario_data=scenario_data,  # Consider logging parts of this if needed for debug, but be wary of size
            custom_scenario_name=custom_run_name,
        )
        logging.info(f"Orchestrator evaluation finished for '{custom_run_name}'.")

        # Check if the evaluation itself resulted in an error
        if "error" in evaluation_results:
            logging.error(
                f"Evaluation for '{custom_run_name}' resulted in an error: {evaluation_results['error']}"
            )
            # Return 500 for internal evaluation errors
            return (
                jsonify({"error": f"Evaluation failed: {evaluation_results['error']}"}),
                500,
            )

        logging.info(
            f"Successfully evaluated custom scenario '{custom_run_name}'. Returning results."
        )
        return jsonify(evaluation_results)

    except Exception as e:
        # Catch unexpected errors during the evaluation call within the endpoint
        logging.exception(
            f"Unexpected error during orchestrator call for custom scenario: {e}"
        )  # Use logging.exception to include traceback
        return (
            jsonify({"error": f"An unexpected error occurred during evaluation: {e}"}),
            500,
        )


if __name__ == "__main__":
    # Note: For development only. Use a proper WSGI server for production.
    # Run only if orchestrator initialized successfully
    if orchestrator:
        # Configure basic logging for development server
        logging.basicConfig(level=logging.DEBUG)
        app.run(debug=True, port=5001)
    else:
        logging.critical(
            "Cannot start Flask server: Evaluation components failed to initialize."
        )
