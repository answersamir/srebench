"""
This module serves the web UI for the SREBench results viewer, handling requests
for custom scenarios and serving static files.
"""

import json
import yaml
import io
from typing import Dict, Any, List, Optional
import logging  # Added for logging
import os
from flask import Flask, request, jsonify, send_from_directory
from orechestrator_builder import initialize_evaluation_components

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)

# Define the path to the results_viewer directory relative to this script's location
# Assuming web_ui.py is in src/ and results_viewer is also in src/
RESULTS_VIEWER_DIR = os.path.join(os.path.dirname(__file__), "results_viewer")
logger.info(f"RESULTS_VIEWER_DIR is set to: {RESULTS_VIEWER_DIR}")
# Define the base directory for scenarios relative to this script
SCENARIOS_BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "scenarios")
)
logger.info(f"Scenarios base directory: {SCENARIOS_BASE_DIR}")
# Define the path to the evaluation results directory
# Assumes web_ui.py is in src/ and eval_results/ is at the project root
EVAL_RESULTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "bench_runs")
)
logger.info(f"Evaluation results directory: {EVAL_RESULTS_DIR}")

# --- Global Orchestrator Instance ---
# Initialize components once when the app starts.
# This avoids re-initializing the LLM and other components on every request.
# Note: In a production scenario with multiple workers, consider if shared state
# needs more sophisticated handling (e.g., lazy initialization per worker).
try:
    orchestrator = initialize_evaluation_components(
        scenario_base_path=SCENARIOS_BASE_DIR
    )
except Exception as e:
    # Log the error and potentially prevent the app from starting
    # or set orchestrator to None and handle it in the request.
    logger.critical(f"Failed to initialize evaluation components on startup: {e}")
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


@app.route("/custom")
def serve_custom_scenario():
    """Serves the main custom_scenario.html file."""
    logger.debug(f"Attempting to serve custom_scenario.html from {RESULTS_VIEWER_DIR}")
    return send_from_directory(RESULTS_VIEWER_DIR, "custom_scenario.html")


@app.route("/custom/<path:filename>")
def serve_custom_static(filename):
    """Serves static files (JS, CSS) requested by custom_scenario.html."""
    logger.debug(
        f"Attempting to serve static file {filename} from {RESULTS_VIEWER_DIR}"
    )
    # logger.debug(f"Serving static file: {filename} from directory: {RESULTS_VIEWER_DIR}") # Redundant log
    return send_from_directory(RESULTS_VIEWER_DIR, filename)


# --- HTML Page Serving ---


@app.route("/run_benchmark")
def serve_run_benchmark():
    """Serves the run_bench.html page."""
    logger.debug(f"Attempting to serve run_bench.html from {RESULTS_VIEWER_DIR}")
    return send_from_directory(RESULTS_VIEWER_DIR, "run_bench.html")


@app.route("/browse_results")
def serve_browse_results():
    """Serves the browse_results.html page."""
    logger.debug(f"Attempting to serve browse_results.html from {RESULTS_VIEWER_DIR}")
    return send_from_directory(RESULTS_VIEWER_DIR, "browse_results.html")


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
            logger.warning(f"Scenario file not found or is not a file: {file_path}")
            return None
    except IOError as e:
        logger.error(f"Error reading scenario file {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading file {file_path}: {e}")
        return None


# --- API Endpoints ---


@app.route("/api/scenarios", methods=["GET"])
def list_scenarios():
    """Lists available scenario IDs based on subdirectories."""
    logger.info(f"Request received for /api/scenarios. Scanning {SCENARIOS_BASE_DIR}")
    if not os.path.exists(SCENARIOS_BASE_DIR) or not os.path.isdir(SCENARIOS_BASE_DIR):
        logger.error(f"Scenarios directory not found: {SCENARIOS_BASE_DIR}")
        return jsonify({"error": "Scenarios directory not found on server."}), 500

    try:
        scenario_ids = [
            d
            for d in os.listdir(SCENARIOS_BASE_DIR)
            if os.path.isdir(os.path.join(SCENARIOS_BASE_DIR, d))
        ]
        logger.info(f"Found scenarios: {scenario_ids}")
        return jsonify(scenario_ids)
    except OSError as e:
        logger.error(f"Error reading scenarios directory {SCENARIOS_BASE_DIR}: {e}")
        return jsonify({"error": "Could not read scenarios directory."}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing scenarios: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route("/api/scenarios/<scenario_id>", methods=["GET"])
def get_scenario_data(scenario_id: str):
    """Retrieves the content of all files for a given scenario."""
    logger.info(f"Request received for /api/scenarios/{scenario_id}")
    logger.debug(f"SCENARIOS_BASE_DIR: {SCENARIOS_BASE_DIR}")
    logger.debug(f"Validating scenario_id: {scenario_id}")

    # Basic input validation for scenario_id to prevent path traversal
    if (
        not scenario_id
        or ".." in scenario_id
        or "/" in scenario_id
        or "\\" in scenario_id
    ):
        logger.warning(f"Invalid scenario_id requested: {scenario_id}")
        return jsonify({"error": "Invalid scenario ID format."}), 400

    scenario_path = os.path.join(SCENARIOS_BASE_DIR, scenario_id)
    logger.info(f"Constructed scenario path: {scenario_path}")
    logger.debug(f"Checking if scenario path exists: {scenario_path}")
    if os.path.exists(scenario_path):
        logger.debug(f"Scenario path exists: {scenario_path}")
    else:
        logger.debug(f"Scenario path does not exist: {scenario_path}")
        logger.debug(
            f"Directory listing for SCENARIOS_BASE_DIR: {os.listdir(SCENARIOS_BASE_DIR) if os.path.exists(SCENARIOS_BASE_DIR) else 'SCENARIOS_BASE_DIR does not exist'}"
        )

    if not os.path.exists(scenario_path) or not os.path.isdir(scenario_path):
        logger.warning(f"Scenario directory not found: {scenario_path}")
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

    logger.info(f"Reading files for scenario: {scenario_id}")
    for key, relative_path in files_to_read.items():
        full_file_path = os.path.join(scenario_path, relative_path)
        content = _read_scenario_file(full_file_path)
        scenario_content[key] = content  # Store content or None if read failed

    # Check if at least one file was successfully read (optional, depends on requirements)
    if all(value is None for value in scenario_content.values()):
        # This might happen if the directory exists but is empty or contains none of the expected files
        logger.warning(
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

    logger.info(f"Successfully retrieved data for scenario: {scenario_id}")
    return jsonify(scenario_content)


@app.route("/api/list_runs", methods=["GET"])
def list_runs():
    """Lists available benchmark run IDs based on subdirectories in EVAL_RESULTS_DIR."""
    logger.info(f"Request received for /api/list_runs. Scanning {EVAL_RESULTS_DIR}")
    if not os.path.exists(EVAL_RESULTS_DIR) or not os.path.isdir(EVAL_RESULTS_DIR):
        logger.warning(f"Evaluation results directory not found: {EVAL_RESULTS_DIR}")
        # Return empty list if dir doesn't exist, as the frontend might expect an array
        return jsonify([])

    try:
        run_ids = [
            d
            for d in os.listdir(EVAL_RESULTS_DIR)
            if os.path.isdir(os.path.join(EVAL_RESULTS_DIR, d))
        ]
        # Sort runs for consistent ordering, perhaps reverse chronologically if names allow
        run_ids.sort(reverse=True)
        logger.info(f"Found runs: {run_ids}")
        return jsonify(run_ids)
    except OSError as e:
        logger.error(f"Error reading results directory {EVAL_RESULTS_DIR}: {e}")
        return jsonify({"error": "Could not read evaluation results directory."}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing runs: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route("/api/get_run_results", methods=["GET"])
def get_run_results():
    """
    Retrieves and aggregates results.json data from scenario subdirectories
    within a specific benchmark run.
    """
    run_id = request.args.get("run_id")
    logger.info(f"Request received for /api/get_run_results with run_id: {run_id}")
    logger.debug(f"Starting get_run_results for run_id: {run_id}")

    # --- Input Validation ---
    if not run_id:
        logger.warning("Missing 'run_id' query parameter.")
        return jsonify({"error": "Missing 'run_id' query parameter."}), 400

    # Basic security check to prevent path traversal
    if ".." in run_id or "/" in run_id or "\\" in run_id:
        logger.warning(f"Invalid characters detected in run_id: {run_id}")
        return jsonify({"error": "Invalid run_id format."}), 400

    # --- Path Construction and Directory Check ---
    run_dir_path = os.path.join(EVAL_RESULTS_DIR, run_id)
    logger.debug(f"Constructed run directory path: {run_dir_path}")

    run_dir_exists = os.path.exists(run_dir_path)
    run_dir_is_dir = os.path.isdir(run_dir_path)
    logger.debug(
        f"Check results for {run_dir_path}: exists={run_dir_exists}, isdir={run_dir_is_dir}"
    )

    if not run_dir_exists or not run_dir_is_dir:
        logger.warning(f"Run directory not found: {run_dir_path}")
        return jsonify({"error": f"Run '{run_id}' not found."}), 404

    # --- Aggregate Scenario Results ---
    all_scenario_data: List[Dict[str, Any]] = []
    try:
        logger.debug(f"Listing contents of run directory: {run_dir_path}")
        for item_name in os.listdir(run_dir_path):
            logger.debug(f"Found item in run directory: {item_name}")
            scenario_dir_path = os.path.join(run_dir_path, item_name)
            logger.debug(f"Constructed scenario directory path: {scenario_dir_path}")

            # Check if it's a directory (potential scenario directory)
            scenario_dir_is_dir = os.path.isdir(scenario_dir_path)
            logger.debug(
                f"Check results for {scenario_dir_path}: isdir={scenario_dir_is_dir}"
            )

            if scenario_dir_is_dir:
                results_file_path = os.path.join(scenario_dir_path, "results.json")
                logger.debug(f"Constructed results file path: {results_file_path}")

                results_file_exists = os.path.exists(results_file_path)
                results_file_is_file = os.path.isfile(results_file_path)
                logger.debug(
                    f"Check results for {results_file_path}: exists={results_file_exists}, isfile={results_file_is_file}"
                )

                if results_file_exists and results_file_is_file:
                    logger.debug(
                        f"Attempting to read results file: {results_file_path}"
                    )
                    try:
                        with open(results_file_path, "r", encoding="utf-8") as f:
                            scenario_result = json.load(f)
                            # Optionally add scenario name if needed later
                            # scenario_result['scenario_id'] = item_name
                            all_scenario_data.append(scenario_result)
                            logger.debug(
                                f"Successfully loaded results from {results_file_path}"
                            )
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"Failed to parse JSON in {results_file_path}: {e}. Skipping file."
                        )
                    except IOError as e:
                        logger.warning(
                            f"Failed to read file {results_file_path}: {e}. Skipping file."
                        )
                    except Exception as e:
                        logger.warning(
                            f"Unexpected error processing file {results_file_path}: {e}. Skipping file."
                        )
                else:
                    logger.debug(
                        f"Results file not found or is not a file: {results_file_path}"
                    )

    except OSError as e:
        logger.error(f"Error listing contents of run directory {run_dir_path}: {e}")
        return jsonify({"error": "Failed to read run directory contents."}), 500
    except Exception as e:
        logger.error(f"Unexpected error processing run '{run_id}': {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500

    # --- Check if any results were found ---
    if not all_scenario_data:
        logger.warning(
            f"No valid scenario results found in run '{run_id}'. Returning 404."
        )
        return jsonify({"error": f"No scenario results found for run '{run_id}'."}), 404

    # --- Construct Final Response ---
    logger.debug(
        f"Aggregating {len(all_scenario_data)} scenario results for run '{run_id}'."
    )

    # Create a top-level summary object
    summary = {
        "run_id": run_id,
        "scenario_count": len(all_scenario_data),
    }

    # Optionally, aggregate additional metrics from scenarios if needed
    # Example: Calculate average efficiency_score if present
    efficiency_scores = [
        scenario.get("efficiency_score")
        for scenario in all_scenario_data
        if "efficiency_score" in scenario
    ]
    if efficiency_scores:
        summary["average_efficiency_score"] = sum(efficiency_scores) / len(
            efficiency_scores
        )

    aggregated_results = {
        "summary": summary,
        "scenarios": all_scenario_data,
    }

    logger.info(
        f"Successfully aggregated results for run '{run_id}'. Returning aggregated data."
    )
    logger.info(f"Returning aggregated results: {aggregated_results}")
    return jsonify(aggregated_results)


@app.route("/api/run_benchmark", methods=["POST"])
def run_benchmark():
    """
    Endpoint to start a benchmark run.
    This endpoint is called by the frontend to initiate a benchmark process.
    """
    logger.info("Received request to start benchmark.")
    # Check if orchestrator is initialized
    if orchestrator is None:
        logger.error("Orchestrator not initialized. Cannot start benchmark.")
        return jsonify(
            {
                "error": "Benchmark service is not available due to initialization failure."
            }
        ), 503

    try:
        scenario_id_to_evaluate = "scenario_001"  # Placeholder for actual scenario ID
        logger.info(f"\nRunning evaluation for scenario: {scenario_id_to_evaluate}...")
        _ = orchestrator.evaluate_scenario(scenario_id_to_evaluate)
        logger.info("Evaluation completed.")
        logger.info("Benchmark started successfully")
        return jsonify({"message": "Benchmark started successfully."}), 200
    except Exception as e:
        logger.error(f"Error starting benchmark: {e}", exc_info=True)
        return jsonify(
            {"error": "An unexpected error occurred while starting the benchmark."}
        ), 500


# --- API Endpoints ---


@app.route("/evaluate", methods=["POST"])
def evaluate_scenario():
    """
    Endpoint to evaluate a custom scenario provided in the request body.
    Expects a JSON payload with scenario details.
    """
    logger.info("Received request to evaluate custom scenario.")
    if orchestrator is None:
        logger.error("Orchestrator not initialized. Cannot evaluate scenario.")
        return (
            jsonify(
                {
                    "error": "Evaluation service is not available due to initialization failure."
                }
            ),
            503,
        )  # Service Unavailable

    if not request.is_json:
        logger.warning("Received non-JSON request for /evaluate endpoint.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    logger.debug(
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
        logger.error(f"Error parsing input data: {e}", exc_info=True)
        return jsonify({"error": f"Error parsing input data: {e}"}), 400
    except Exception as e:  # Catch unexpected errors during parsing
        logger.error(f"An unexpected error occurred during parsing: {e}", exc_info=True)
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

        logger.info(
            f"Calling orchestrator.evaluate_custom_scenario for '{custom_run_name}'"
        )
        # Call the method directly on the orchestrator instance
        evaluation_results = orchestrator.evaluate_custom_scenario(
            scenario_data=scenario_data,  # Consider logging parts of this if needed for debug, but be wary of size
            custom_scenario_name=custom_run_name,
        )
        logger.info(f"Orchestrator evaluation finished for '{custom_run_name}'.")

        # Check if the evaluation itself resulted in an error
        if "error" in evaluation_results:
            logger.error(
                f"Evaluation orchestrator returned an error: {evaluation_results['error']}"
            )
            # Return the error from the orchestrator
            return jsonify(evaluation_results), 500
        else:
            logger.info(
                f"Evaluation successful for '{custom_run_name}'. Returning results."
            )
            return jsonify(evaluation_results), 200

    except Exception as e:
        logger.error(
            f"An unexpected error occurred during scenario evaluation: {e}",
            exc_info=True,
        )
        return (
            jsonify({"error": f"An unexpected error occurred during evaluation: {e}"}),
            500,
        )


if __name__ == "__main__":
    # In a production deployment, a production-ready WSGI server like Gunicorn
    # should be used instead of Flask's built-in server.
    # Example: gunicorn -w 4 'src.web_ui:app'
    logger.basicConfig(level=logger.DEBUG)  # Set logging level to DEBUG for development
    app.run(debug=True, port=5000)
