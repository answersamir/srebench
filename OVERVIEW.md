### **High-Level Architecture Document for SREBench**

#### **1. Introduction**

SREBench is a benchmark designed to evaluate the incident resolution capabilities of AI Site Reliability Engineering (SRE) agents in Kubernetes (k8s) environments. It provides a synthetic dataset of complex incident scenarios, enabling consistent and reproducible testing of AI-driven Root Cause Analysis (RCA) and resolution strategies. The benchmark aims to accelerate research in AIOps by offering a standardized evaluation framework.

---

#### **2. Codebase Structure**

The codebase is organized into the following directories:

- **`src/`**: Contains the main source code for SREBench, including core components and utilities.
  - **`basic_agent/`**: Implements the AI agent's logic and interaction with scenarios.
  - **`eval_pipeline/`**: Manages the evaluation process, including scenario loading, comparison, and efficiency evaluation.
  - **`prompts/`**: Stores prompt templates for AI agents, categorized by versions.
  - **`results_viewer/`**: Provides a web-based interface for visualizing evaluation results.
  - **`scenarios/`**: Contains predefined incident scenarios, including their state, ground truth, and metadata.
  - **`tests/`**: Includes unit tests for validating the functionality of core components.

---

#### **3. Core Components**

The main components and their interactions are as follows:

- **`basic_agent`**:
  - Implements the AI agent's behavior and adapts it to the benchmark scenarios.
  - Key files: `basic_agent.py`, `basic_agent_adapter.py`.

- **`eval_pipeline`**:
  - Orchestrates the evaluation process, including scenario loading, RCA comparison, and efficiency scoring.
  - Key files: `scenario_loader.py`, `result_comparator.py`, `efficiency_evaluator.py`.

- **`prompts`**:
  - Provides prompt templates for guiding the AI agent's reasoning and actions.
  - Key files: `basic_agent_prompts.py`, `v0.md`, `v1.md`, `v2.md`.

- **`results_viewer`**:
  - Offers a web-based interface for browsing and analyzing benchmark results.
  - Key files: `browse_results.html`, `script.js`, `style.css`.

- **`scenarios`**:
  - Stores incident scenarios with their state, ground truth, and metadata.
  - Example: `scenario_001` includes logs, metrics, topology, and resolution steps.

---

#### **4. Testing Strategy**

The testing strategy focuses on validating the functionality of core components:

- **Coverage**:
  - Unit tests are implemented for `basic_agent` and `eval_pipeline`.
  - Example test files: `test_basic_agent.py`, `test_result_comparator.py`, `test_scenario_loader.py`.

- **Identified Gaps**:
  - Limited test coverage for the `results_viewer` and `prompts` components.
  - Potential need for integration tests to validate end-to-end functionality.

---

#### **5. Key Design Patterns**

The codebase employs the following design patterns and architectural decisions:

- **Modularity**:
  - Each component is encapsulated in its own directory, promoting separation of concerns.

- **Template-Based Design**:
  - Prompts and scenarios are defined using templates, enabling easy customization and scalability.

- **Web-Based Visualization**:
  - The `results_viewer` leverages a web interface for user-friendly result analysis.

- **Synthetic Data Generation**:
  - Scenarios are generated using a pipeline inspired by the MuSR dataset methodology, ensuring consistency and scalability.

---

This document provides a high-level overview of the SREBench architecture. Let me know if further refinements are needed or if you'd like this written to a markdown file.
