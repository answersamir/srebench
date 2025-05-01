"""
EfficiencyEvaluator Class
"""

import time


class EfficiencyEvaluator:
    """
    Calculates a score representing the agent's efficiency or simulated MTTR.
    """

    def __init__(self):
        """
        Initializes the EfficiencyEvaluator.
        """
        self._start_time = None

    def start_timer(self):
        """Starts the timer for efficiency calculation."""
        self._start_time = time.time()
        print("EfficiencyEvaluator: Timer started.")

    def stop_timer_and_evaluate(self, agent_execution_data: dict = None) -> float:
        """
        Stops the timer and calculates the efficiency score (simulated MTTR).

        Args:
            agent_execution_data (dict, optional): Data related to agent execution
            (e.g., number of steps). Not used in this basic skeleton.

        Returns:
            float: An efficiency score or simulated MTTR value for the scenario (in seconds).
                   Returns -1.0 if the timer was not started.
        """
        if self._start_time is None:
            print("EfficiencyEvaluator: Timer was not started.")
            return -1.0

        end_time = time.time()
        duration = end_time - self._start_time
        self._start_time = None  # Reset timer

        print(f"EfficiencyEvaluator: Timer stopped. Duration: {duration:.2f} seconds.")

        # Placeholder for actual efficiency calculation logic
        # For POC, duration itself can be the "score" (lower is better)
        # Or you could invert it, cap it, etc.
        efficiency_score = duration

        return efficiency_score


# Example Usage (for testing purposes)
if __name__ == "__main__":
    evaluator = EfficiencyEvaluator()

    print("Simulating agent work...")
    evaluator.start_timer()
    time.sleep(2.5)  # Simulate some work
    simulated_agent_data = {"steps_taken": 5}  # Example data

    mttr = evaluator.stop_timer_and_evaluate(simulated_agent_data)

    print(f"\nSimulated MTTR: {mttr:.2f} seconds")

    # Example without starting timer
    print("\nSimulating evaluation without starting timer...")
    mttr_no_start = evaluator.stop_timer_and_evaluate()
    print(f"Simulated MTTR: {mttr_no_start}")
