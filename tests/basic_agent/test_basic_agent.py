import pytest
import os
from unittest.mock import patch, MagicMock
from langchain_community.llms.fake import FakeListLLM

# Add the parent directory to the path to import modules
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from basic_agent.basic_agent import BasicLLMAgent
from basic_agent.basic_agent_adapter import BasicLLMAgentAdapter
from eval_pipeline.agent_interface import AgentInterface


# Mock the environment variable for API key during testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy_key"}):
        yield


# Test cases for BasicLLMAgent
class TestBasicLLMAgent:

    def test_initialization(self):
        """Test BasicLLMAgent initialization."""
        agent = BasicLLMAgent(model_name="test-model")
        assert agent.model is not None
        assert agent.prompt is not None
        assert agent.chain is not None

    def test_process_scenario_state_success(self):
        """Test processing scenario state with a successful LLM response."""
        # Configure the mock LLM to return a specific response
        llm = FakeListLLM(
            responses=[
                '{"root_cause": "Test Root Cause", "causal_chain": ["step1", "step2"], "resolution": "Test Resolution"}'
            ]
        )

        agent = BasicLLMAgent(llm=llm)
        scenario_state = {"logs": [], "metrics": {}}
        results = agent.process_scenario_state(scenario_state)

        assert isinstance(results, dict)
        assert results.get("root_cause") == "Test Root Cause"
        assert results.get("causal_chain") == ["step1", "step2"]
        assert results.get("resolution") == "Test Resolution"

    def test_process_scenario_state_invalid_json(self):
        """Test processing scenario state with an invalid JSON response from LLM."""
        llm = FakeListLLM(responses=["invalid json response"])

        agent = BasicLLMAgent(llm=llm)
        scenario_state = {"logs": [], "metrics": {}}
        results = agent.process_scenario_state(scenario_state)

        assert isinstance(results, dict)
        assert results.get("root_cause") == "Parsing failed."
        assert results.get("causal_chain") == []
        assert results.get("resolution") == "Parsing failed."


# Test cases for BasicLLMAgentAdapter
class TestBasicLLMAgentAdapter:

    @patch("basic_agent.basic_agent_adapter.BasicLLMAgent")
    def test_initialization(self, MockBasicLLMAgent):
        """Test BasicLLMAgentAdapter initialization."""
        agent_config = {"model_name": "adapter-test-model"}
        adapter = BasicLLMAgentAdapter(agent_config=agent_config)
        MockBasicLLMAgent.assert_called_once_with(model_name="adapter-test-model")
        assert isinstance(adapter, AgentInterface)
        assert adapter.basic_agent is not None

    @patch("basic_agent.basic_agent_adapter.BasicLLMAgent")
    def test_interact_with_agent(self, MockBasicLLMAgent):
        """Test interact_with_agent method of the adapter."""
        mock_basic_agent_instance = MagicMock()
        mock_basic_agent_instance.process_scenario_state.return_value = {
            "root_cause": "Adapter Test Root Cause",
            "causal_chain": ["adapter_step1"],
            "resolution": "Adapter Test Resolution",
        }
        MockBasicLLMAgent.return_value = mock_basic_agent_instance

        agent_config = {"model_name": "adapter-test-model"}
        adapter = BasicLLMAgentAdapter(agent_config=agent_config)

        scenario_data = {
            "description": "Adapter test scenario.",
            "state": {"logs": [{"msg": "adapter log"}]},
        }

        results = adapter.interact_with_agent(scenario_data)

        assert isinstance(results, dict)
        assert results.get("root_cause") == "Adapter Test Root Cause"
        assert results.get("causal_chain") == ["adapter_step1"]
        assert results.get("resolution") == "Adapter Test Resolution"

        # Verify that the underlying BasicLLMAgent's method was called with the correct state
        mock_basic_agent_instance.process_scenario_state.assert_called_once_with(
            scenario_data.get("state")
        )
