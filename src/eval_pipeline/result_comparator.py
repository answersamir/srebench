"""
Module for comparing agent output with ground truth data for accuracy.
"""

from .comparison_utils import (
    calculate_semantic_similarity,
    calculate_causal_graph_score,
    compare_component,
)


class ResultComparator:
    """
    A class to compare agent output with ground truth data for accuracy.

    This class provides methods to calculate semantic similarity, keyword overlap,
    and causal chain similarity scores.

    Compares the structured output from the AgentInterface against the
    structured ground_truth/ data from the ScenarioLoader for accuracy.
    """

    def __init__(self):
        """
        Initializes the ResultComparator.
        """
        # Initialization logic is not required.

    def compare(self, agent_output: dict, ground_truth: dict) -> dict:
        """
        Compares agent output with ground truth data and calculates scores.

        Args:
            agent_output (dict): Standardized agent output.
            ground_truth (dict): Structured ground truth data.

        Returns:
            dict: A dictionary of comparison scores for the scenario.
                  Expected keys: 'rca_root_cause_score', 'rca_causal_chain_score',
                  'resolution_correctness_score'. Scores typically range from 0.0 to 1.0.
        """

        agent_rc = agent_output.get("root_cause", {})
        gt_rc = ground_truth.get("root_cause", {})
        agent_res = agent_output.get("resolution", {})
        gt_res = ground_truth.get("resolution", {})
        agent_cg = agent_output.get("causal_graph", {})
        gt_cg = ground_truth.get("causal_graph", {})

        rca_root_cause_score = self._compare_root_cause(agent_rc, gt_rc)
        resolution_correctness_score = self._compare_resolution(agent_res, gt_res)
        rca_causal_graph_score = self._compare_causal_graph(agent_cg, gt_cg)

        return {
            "rca_root_cause_score": rca_root_cause_score,
            "rca_causal_graph_score": rca_causal_graph_score,
            "resolution_correctness_score": resolution_correctness_score,
        }

    def _compare_root_cause(self, agent_rc: dict, gt_rc: dict) -> float:
        """
        Compares the root cause section of agent output and ground truth.

        Args:
            agent_rc (dict): Agent's identified root cause.
            gt_rc (dict): Ground truth root cause.

        Returns:
            float: The comparison score for the root cause (0.0 to 1.0).
        """
        rca_weights = {
            "type": 0.2,
            "resource_type": 0.2,
            "component": 0.3,
            "details": 0.3,
        }

        # Compare type
        type_score = (
            1.0
            if agent_rc.get("type") == gt_rc.get("type")
            and agent_rc.get("type") is not None
            else 0.0
        )

        # Compare resource_type
        resource_type_score = (
            1.0
            if agent_rc.get("resource_type") == gt_rc.get("resource_type")
            and agent_rc.get("resource_type") is not None
            else 0.0
        )

        # Compare component
        component_score = compare_component(
            agent_rc.get("component"), gt_rc.get("component")
        )

        # Compare details
        agent_rc_details = agent_rc.get("details", "")
        gt_rc_details = gt_rc.get("details", "")
        details_score_rc = calculate_semantic_similarity(
            agent_rc_details, gt_rc_details
        )

        # Calculate weighted root cause score
        rca_root_cause_score = (
            rca_weights["type"] * type_score
            + rca_weights["resource_type"] * resource_type_score
            + rca_weights["component"] * component_score
            + rca_weights["details"] * details_score_rc
        )
        return rca_root_cause_score

    def _compare_resolution(self, agent_res: dict, gt_res: dict) -> float:
        """
        Compares the resolution section of agent output and ground truth.

        Args:
            agent_res (dict): Agent's proposed resolution.
            gt_res (dict): Ground truth resolution.

        Returns:
            float: The comparison score for the resolution (0.0 to 1.0).
        """
        res_weights = {
            "action_type": 0.3,
            "target_component": 0.4,
            "details": 0.3,
        }

        # Compare action_type
        action_type_score = (
            1.0
            if agent_res.get("action_type") == gt_res.get("action_type")
            and agent_res.get("action_type") is not None
            else 0.0
        )

        # Compare target_component
        target_component_score = compare_component(
            agent_res.get("target_component"), gt_res.get("target_component")
        )

        # Compare details
        agent_res_details = agent_res.get("details", "")
        gt_res_details = gt_res.get("details", "")
        details_score_res = calculate_semantic_similarity(
            agent_res_details, gt_res_details
        )

        # Calculate weighted resolution score
        resolution_correctness_score = (
            res_weights["action_type"] * action_type_score
            + res_weights["target_component"] * target_component_score
            + res_weights["details"] * details_score_res
        )
        return resolution_correctness_score

    def _compare_causal_graph(self, agent_cg: dict, gt_cg: dict) -> float:
        """
        Compares the causal graph section of agent output and ground truth.

        Args:
            agent_cg (dict): Agent's identified causal graph.
            gt_cg (dict): Ground truth causal graph.

        Returns:
            float: The comparison score for the causal graph (0.0 to 1.0).
        """
        return calculate_causal_graph_score(agent_cg, gt_cg)


# Example usage (for testing purposes).
if __name__ == "__main__":
    # Example agent output and ground truth structures (Updated Format)
    example_agent_output = {
        "root_cause": {
            "type": "Resource Exhaustion",
            "resource_type": "Connection Pool",
            "component": {
                "kind": "Database",
                "name": "auth-db",
                "namespace": "prod",
            },  # Added namespace
            "details": "The connection pool for the authentication database was exhausted due to high login rates.",
        },
        "causal_graph": {
            "nodes": [
                {"id": "n1", "label": "High Login Rate", "type": "External Factor"},
                {"id": "n2", "label": "Auth Service High CPU", "type": "Symptom"},
                {
                    "id": "n3",
                    "label": "Auth DB Connection Exhaustion",
                    "type": "Root Cause",
                },
            ],
            "edges": [
                {"source": "n1", "target": "n2", "relation": "CAUSES"},
                {"source": "n2", "target": "n3", "relation": "CAUSES"},
            ],
        },
        "resolution": {
            "action_type": "Configuration Change",
            "target_component": {
                "kind": "Database",
                "name": "auth-db",
                "namespace": "prod",
            },  # Added namespace
            "details": "Increase the maximum connection limit for the 'auth-db' connection pool.",
        },
    }

    example_ground_truth = {
        "root_cause": {
            "type": "Resource Exhaustion",
            "resource_type": "Database Connections",  # Different resource_type
            "component": {
                "kind": "Database",
                "name": "auth-db",
                "namespace": "prod",
            },  # Matching component
            "details": "Exhaustion of available connections in the authentication database pool.",  # Different details
        },
        "causal_graph": {
            "nodes": [
                {
                    "id": "gt_n1",
                    "label": "Increased User Logins",
                    "type": "Load Increase",
                },
                {
                    "id": "gt_n2",
                    "label": "Auth DB Connection Exhaustion",
                    "type": "Resource Bottleneck",
                },
                {
                    "id": "gt_n3",
                    "label": "Login Latency High",
                    "type": "Performance Impact",
                },
            ],
            "edges": [
                {"source": "gt_n1", "target": "gt_n2", "relation": "LEADS_TO"},
                {"source": "gt_n2", "target": "gt_n3", "relation": "RESULTS_IN"},
            ],
        },
        "resolution": {
            "action_type": "Scale Resource",  # Different action_type
            "target_component": {
                "kind": "Database",
                "name": "auth-db",
                "namespace": "prod",
            },  # Matching component
            "details": "Adjust the max_connections parameter for the 'auth-db' pool.",  # Different details
        },
    }

    # Example with missing parts
    example_agent_output_missing = {
        "root_cause": {
            "type": "Resource Exhaustion",
            # Missing resource_type
            "component": {"kind": "Database", "name": "auth-db"},  # Missing namespace
            "details": "The connection pool for the authentication database was exhausted.",
        },
        "causal_graph": {},  # Empty graph
        "resolution": {
            # Missing action_type
            "target_component": {"kind": "Database", "name": "auth-db"},
            "details": "Increase the maximum connection limit.",
        },
    }
    example_ground_truth_missing = {
        "root_cause": {
            "type": "Resource Exhaustion",
            "resource_type": "Database Connections",
            "component": {"kind": "Database", "name": "auth-db", "namespace": "prod"},
            "details": "Exhaustion of available connections.",
        },
        "causal_graph": {"nodes": [], "edges": []},  # Empty graph
        "resolution": {
            "action_type": "Scale Resource",
            # Missing target_component
            "details": "Adjust the max_connections parameter.",
        },
    }

    # Instantiate and use the comparator
    comparator = ResultComparator()
    print("\n--- Standard Comparison ---")
    scores = comparator.compare(example_agent_output, example_ground_truth)
    print("Comparison Scores:")
    print(scores)

    print("\n--- Comparison with Missing Parts ---")
    scores_missing = comparator.compare(
        example_agent_output_missing, example_ground_truth_missing
    )
    print("Comparison Scores (Missing Parts):")
    print(scores_missing)
