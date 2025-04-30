"""
Module for comparing agent output with ground truth data for accuracy.
"""

# Import necessary modules for text similarity calculations.
# Import necessary modules for text similarity calculations.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ResultComparator:
    """
    A class to compare agent output with ground truth data for accuracy.

    This class provides methods to calculate semantic similarity, keyword overlap,
    and causal chain similarity scores.
    """

    """
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

        def calculate_semantic_similarity(text1: str, text2: str) -> float:
            """
            Calculate semantic similarity between two texts.

            Args:
                text1 (str): First text input.
                text2 (str): Second text input.

            Returns:
                float: Semantic similarity score between 0.0 and 1.0.
            """
            vectorizer = TfidfVectorizer().fit_transform([text1, text2])
            vectors = vectorizer.toarray()
            return cosine_similarity(vectors)[0, 1]

        def calculate_keyword_overlap(text1: str, text2: str) -> float:
            """
            Calculate keyword overlap between two texts.

            Args:
                text1 (str): First text input.
                text2 (str): Second text input.

            Returns:
                float: Keyword overlap score between 0.0 and 1.0.
            """
            set1 = set(text1.lower().split())
            set2 = set(text2.lower().split())
            return len(set1 & set2) / len(set1 | set2)

        def calculate_causal_chain_score(chain1: list, chain2: list) -> float:
            """
            Calculate causal chain similarity score.

            Args:
                chain1 (list): First causal chain.
                chain2 (list): Second causal chain.

            Returns:
                float: Causal chain similarity score between 0.0 and 1.0.
            """
            set1 = set(chain1)
            set2 = set(chain2)
            return len(set1 & set2) / len(set1 | set2)

        root_cause_similarity = calculate_semantic_similarity(
            agent_output.get("root_cause", ""), ground_truth.get("root_cause", "")
        )
        resolution_keyword_overlap = calculate_keyword_overlap(
            agent_output.get("resolution", ""), ground_truth.get("resolution", "")
        )
        causal_chain_score = calculate_causal_chain_score(
            agent_output.get("causal_chain", []), ground_truth.get("causal_graph", [])
        )

        return {
            "rca_root_cause_score": root_cause_similarity,
            "rca_causal_chain_score": causal_chain_score,
            "resolution_correctness_score": resolution_keyword_overlap,
        }


# Example usage (for testing purposes).
if __name__ == "__main__":
    # Example agent output and ground truth structures (simplified)
    example_agent_output = {
        "root_cause": "The database connection pool was exhausted.",
        "causal_chain": ["app_requests_increase", "db_connections_exhausted"],
        "resolution": "Increase the database connection pool size.",
    }

    example_ground_truth = {
        "root_cause": "Database connection pool exhaustion.",
        "causal_graph": ["app_requests", "db_connections"],
        "resolution": "Adjust database connection limit.",
    }

    # Instantiate and use the comparator
    comparator = ResultComparator()
    scores = comparator.compare(example_agent_output, example_ground_truth)

    print("\nComparison Scores:")
    print(scores)
