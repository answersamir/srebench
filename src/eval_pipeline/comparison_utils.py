"""
Utility functions for comparing evaluation results.

This module contains helper functions used by ResultComparator to calculate
similarity scores between agent outputs and ground truth data.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import fuzz


def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity between two texts using TF-IDF and cosine similarity.

    Args:
        text1 (str): First text input.
        text2 (str): Second text input.

    Returns:
        float: Semantic similarity score between 0.0 and 1.0.
               Returns 0.0 if either text is empty or only whitespace.
    """
    if not text1 or not text1.strip() or not text2 or not text2.strip():
        return 0.0  # Avoid division by zero or meaningless comparison

    try:
        vectorizer = TfidfVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        # Handle potential zero vectors if texts are identical stop words etc.
        if vectors.shape[0] < 2:
            return (
                1.0 if text1 == text2 else 0.0
            )  # Should ideally not happen with check above
        similarity = cosine_similarity(vectors)
        # Ensure the result is within bounds, cosine_similarity can sometimes be slightly off due to precision
        return max(0.0, min(1.0, similarity[0, 1]))
    except ValueError:
        # Can happen if vocabulary is empty (e.g., only stop words)
        return 1.0 if text1 == text2 else 0.0


def calculate_causal_graph_score(graph1: dict | None, graph2: dict | None) -> float:
    """
    Calculate causal graph similarity score based on fuzzy matching of node labels.

    Compares the sets of node labels between two graphs using fuzzy matching
    (token set ratio) to account for minor variations in phrasing.

    Args:
        graph1 (dict | None): First causal graph structure (expected keys: 'nodes').
        graph2 (dict | None): Second causal graph structure (expected keys: 'nodes').

    Returns:
        float: Causal graph similarity score between 0.0 and 1.0.
               Returns 0.0 if inputs are invalid or cannot be compared meaningfully.
               Returns 1.0 if both graphs are effectively empty (None or no valid nodes/labels).
    """

    # Helper to safely extract non-empty string labels from a graph's nodes list
    def _extract_labels(graph: dict | None) -> list[str]:
        """Extracts valid node labels from a graph dictionary."""
        if not isinstance(graph, dict):
            return []
        nodes = graph.get("nodes")
        if not isinstance(nodes, list):
            return []

        # Extract labels using list comprehension with checks
        return [
            node.get("label")
            for node in nodes
            if isinstance(node, dict)
            and isinstance(node.get("label"), str)
            and node.get("label").strip()  # Ensure label is not just whitespace
        ]

    agent_labels = _extract_labels(graph1)
    gt_labels = _extract_labels(graph2)

    # Handle cases where one or both graphs are empty/invalid
    if not agent_labels and not gt_labels:
        return 1.0  # Both empty, perfect match
    if not agent_labels or not gt_labels:
        return 0.0  # One empty, no match

    similarity_threshold = 80  # Threshold for fuzzy match (e.g., 80%)
    match_count = 0
    # Create a copy to modify while iterating
    remaining_gt_labels = list(gt_labels)

    for agent_label in agent_labels:
        best_match_score = -1
        best_match_index = -1

        # Find the best match for the current agent_label in remaining gt_labels
        for i, gt_label in enumerate(remaining_gt_labels):
            # Use token_set_ratio for better handling of word order and subsets
            score = fuzz.token_set_ratio(agent_label, gt_label)
            if score > best_match_score:
                best_match_score = score
                best_match_index = i

        # If a good enough match is found, count it and remove from future consideration
        if best_match_score >= similarity_threshold:
            match_count += 1
            # Remove the matched GT label by index to prevent reuse
            del remaining_gt_labels[best_match_index]

    # Calculate score based on matches (Dice coefficient style: 2 * |Intersection| / (|A| + |B|))
    denominator = len(agent_labels) + len(gt_labels)
    # Denominator should not be zero here due to checks above, but added for safety
    score = (2 * match_count) / denominator if denominator > 0 else 1.0
    return score


def compare_component(comp1: dict | None, comp2: dict | None) -> float:
    """
    Compare two component dictionaries for exact match on kind, name, and namespace.

    Checks if 'kind' and 'name' match exactly. If 'namespace' is present in
    either component, it must also match.

    Args:
        comp1 (dict | None): First component dictionary.
        comp2 (dict | None): Second component dictionary.

    Returns:
        float: 1.0 if components match based on the criteria, 0.0 otherwise.
               Returns 0.0 if either input is not a valid dictionary.
    """
    if not isinstance(comp1, dict) or not isinstance(comp2, dict):
        return 0.0  # One or both components missing/invalid

    # Check for exact match on mandatory keys
    if comp1.get("kind") != comp2.get("kind") or comp1.get("name") != comp2.get("name"):
        return 0.0

    # Check namespace only if present in either component
    comp1_ns = comp1.get("namespace")
    comp2_ns = comp2.get("namespace")
    if comp1_ns is not None or comp2_ns is not None:
        if comp1_ns != comp2_ns:
            return 0.0  # Namespace mismatch

    return 1.0  # All relevant keys match
