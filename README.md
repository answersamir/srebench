# Design Document: SREBench - An AIOps Benchmark for AI SRE Agent Resolution Capabilities

## 1. Introduction

This document outlines the design for **SREBench**, a proposed benchmark specifically tailored for evaluating the incident resolution capabilities of AI Site Reliability Engineering (SRE) agents within Kubernetes (k8s) environments. Drawing inspiration from the data generation methodology of the Multistep Soft Reasoning (MuSR) dataset, SREBench aims to provide a collection of complex, realistic incident scenarios in simulated k8s clusters. Each scenario will include a defined cluster state (logs, metrics, events, topology), a known root cause, and a validated resolution path. The goal is to leverage Large Language Models (LLMs), potentially combined with symbolic methods, to synthetically generate these intricate scenarios, overcoming the challenges associated with obtaining diverse, labelled real-world incident data for benchmarking AIOps solutions.

## 2. Goals

*   To create a **standardized benchmark dataset** for evaluating the Root Cause Analysis (RCA) and resolution capabilities of AI SRE agents operating in k8s environments.
*   To enable **consistent and reproducible testing** of different AI SRE agent approaches and algorithms.
*   To provide **diverse and challenging incident scenarios** that reflect the complexity of real-world distributed systems, going beyond simple, rule-based failure injection.
*   To **accelerate research and development** in AI-driven incident management and automated remediation by providing a readily available, high-quality evaluation resource.
*   To **quantify the effectiveness** of AI SRE agents in reducing Mean Time to Resolution (MTTR) and improving operational efficiency.

## 3. Motivation

Modern large-scale distributed systems, such as those running on Kubernetes, generate vast amounts of operational data (logs, metrics, traces, events). Manually sifting through this data to detect, diagnose, and resolve incidents is increasingly challenging and time-consuming, leading to high MTTR. AIOps leverages AI and Machine Learning (ML) to automate these tasks, promising significant improvements in reliability and efficiency.

A core function of AIOps is incident management, which involves detection, diagnosis (RCA), and automated action/mitigation. While incident detection and correlation are areas with some existing benchmarks, evaluating the *resolution* phase, particularly the accuracy of RCA and the correctness of suggested or executed remediation, is significantly harder. This is partly due to the difficulty in obtaining large, diverse datasets of real-world incidents with verified root causes and effective resolution steps. Real-world data is often proprietary, messy, and lacks clear ground truth.

The MuSR dataset addresses a similar problem in evaluating LLM reasoning by synthetically generating complex reasoning scenarios (e.g., murder mysteries) with known solutions, embedded within natural language narratives. This synthetic generation process allows for scaling complexity and ensuring a ground truth. By adapting this approach, we can generate synthetic k8s incident scenarios where the underlying cause-and-effect chain (the "reasoning tree") and the correct resolution are known *a priori*. This synthetic approach provides a scalable way to create a challenging benchmark dataset that is currently lacking.

## 4. Background

*   **AIOps:** The application of big data and machine learning to enhance, strengthen, and automate IT operations. Key capabilities include incident management and resource management. AIOps platforms collect and analyse diverse data sources to provide visibility, control, and actionable insights.
*   **Incident Management in AIOps:** A systematic approach encompassing detection, diagnosis (RCA), and resolution of incidents. The objective is to automate as many tasks as possible to reduce time metrics like TTD, TTA, and TTR (Time to Repair/Mitigate).
*   **Root Cause Analysis (RCA):** The process of identifying the underlying reasons for an incident. In large, complex systems, manual RCA is difficult, and AI-based RCA holds significant potential. AI models can process high volumes of data and learn from past incidents to identify root causes. Challenges include a lack of benchmarks and difficulty integrating domain knowledge effectively. Knowledge mining from logs and incident reports can contribute to RCA.
*   **Automated Actions/Remediation:** Taking actions to resolve or mitigate an issue. This can include short-term remediation (e.g., server reboot, scaling) or longer-term resolutions (e.g., bug fixing guidance). ML-based auto-remediation is particularly useful in large systems where manual workflows are impractical.
*   **MuSR Dataset:** A benchmark for evaluating LLMs on multistep soft reasoning based on natural language narratives. It uses a neurosymbolic synthetic-to-natural generation algorithm with three stages: Tree Template Construction, Reasoning Tree Completion, and Story Generation. This process creates complex scenarios with a known logical structure, challenging LLMs beyond simple tasks.

## 5. Proposed Solution: SREBench Architecture

SREBench will be a curated collection of k8s incident scenarios designed for benchmarking AI SRE agents. Each entry in SREBench will represent a single incident and will consist of:

1.  **Scenario Description:** A natural language summary of the symptoms observed.
2.  **Simulated Cluster State:** A collection of synthetic operational data (logs, metrics, events, topology, etc.) captured during the incident, representing the state of a k8s cluster. This data must be consistent with the scenario description and the underlying root cause and causal chain.
3.  **Ground Truth:** Detailed information about the incident, including:
    *   The specific root cause.
    *   The causal chain/reasoning steps linking the root cause to the observed symptoms.
    *   The correct resolution steps or an executable remediation playbook.
    *   Relevant findings or anomalies in the simulated state data that point to the root cause.

The core innovation of SREBench is the **synthetic generation pipeline** for creating the Simulated Cluster State and Ground Truth, adapting the MuSR methodology.

## 6. Technical Design: Scenario Generation Pipeline

The SREBench generation pipeline adapts the three-stage process from MuSR:

### 6.1. Stage 1: Incident Template Construction (Analogue of MuSR's Tree Template Construction)

*   Define a set of **incident templates** representing common types of failures in k8s distributed systems (e.g., resource saturation, network connectivity issues, application errors, misconfigurations, data store problems).
*   Each template defines a **general fault propagation pattern** or a class of causal graphs associated with that incident type. For instance, a "Resource Saturation" template might have patterns for CPU limits being hit leading to latency spikes, or memory leaks leading to OOMKills and pod restarts.
*   These templates provide the high-level structure for the scenarios.

### 6.2. Stage 2: Specific Incident Scenario Completion (Analogue of MuSR's Reasoning Tree Completion)

*   Using an LLM, potentially augmented with symbolic reasoning or domain-specific k8s knowledge, generate a **specific instance** of an incident based on a chosen template.
*   This involves filling in details: specific affected k8s resources (deployment names, namespaces, pod names), threshold values for metrics, specific error messages in logs, timeline of the event.
*   Crucially, the LLM/system generates a **detailed causal chain** or "reasoning tree" linking the specific root cause to the specific observable symptoms across different layers (application, platform, infrastructure). This chain represents the logical steps an SRE or an AI agent would follow during RCA. For example, "high traffic (cause) -> increased CPU usage on `paymentservice` pod (intermediate) -> `paymentservice` pod hits CPU limit (intermediate) -> `paymentservice` pod throttled (intermediate) -> increased latency for API calls to `paymentservice` (symptom) -> `cartservice` experiences 5xx errors calling `paymentservice` (symptom)."
*   This stage produces the **Ground Truth**: the specific root cause, the complete causal graph/chain, and the expected resolution steps (e.g., increase CPU limit for `paymentservice` deployment). This is similar to how MuSR generates the "gold reasoning trees" and "gold fact set".

### 6.3. Stage 3: Simulated State Data Generation (Analogue of MuSR's Story Generation)

*   This is the key adaptation of MuSR's "Story Generation," where the structured causal chain is translated into realistic, temporal operational data streams.
*   Using the specific incident scenario and causal chain from Stage 2:
    *   **Log Generation:** Generate synthetic log entries for relevant pods/services. LLMs can be used to create natural language-like log messages, including error messages, warnings, and informational messages, consistent with the incident type and timeline. This might involve templates for common log structures augmented by LLM-generated content.
    *   **Metric Generation:** Generate time-series data for key k8s and application metrics (CPU, memory, network I/O, request latency, error rates). This data should show anomalies and trends that reflect the progression of the incident as defined by the causal chain. This could involve baseline generation plus injecting anomalies and correlating them across different metrics based on the causal graph.
    *   **Event Generation:** Generate k8s events (e.g., `Warning: Evicted`, `Warning: Restarting`, `FailedScheduling`) that would occur during the incident, linked to the specific resources and timeline.
    *   **Topology/Configuration:** Define or simulate the relevant parts of the k8s cluster topology (e.g., service dependencies, pod assignments to nodes) and potentially specific configurations that might be the root cause or contribute to the incident.
*   The generated data streams must be **temporally consistent** and accurately reflect the cause-and-effect relationships defined in Stage 2.
*   This stage requires mapping the abstract causal model to concrete, quantifiable, and observable data points in a k8s environment. This is where domain knowledge about k8s behaviour and monitoring is critical.

## 7. SREBench Dataset Structure

Each entry in the SREBench dataset would be a self-contained representation of an incident:

```
srebench/
├── scenario_<id>/
│   ├── description.md          # Natural language summary of symptoms
│   ├── state/
│   │   ├── logs.jsonl          # Simulated log entries
│   │   ├── metrics.json        # Simulated time-series metrics
│   │   ├── events.jsonl        # Simulated k8s events
│   │   ├── topology.json       # Relevant cluster topology snapshot
│   │   └── configuration.yaml  # Relevant configuration files (if applicable to cause)
│   ├── ground_truth/
│   │   ├── root_cause.md       # Description of the root cause
│   │   ├── causal_graph.json   # Structured representation of the cause-effect chain
│   │   ├── resolution.md       # Description of the correct resolution steps
│   │   └── playbook.yaml       # (Optional) Machine-readable resolution playbook
│   └── metadata.json           # Incident template used, complexity level, etc.
```

## 8. Evaluation Framework

AI SRE agents would be evaluated by presenting them with the `scenario_<id>/description.md` and the `scenario_<id>/state/` data. The agent's task is to perform RCA and propose/execute a resolution.

Evaluation metrics would compare the agent's output against the `ground_truth`:

*   **RCA Accuracy:** How accurately does the agent identify the root cause and the causal chain compared to `ground_truth/root_cause.md` and `ground_truth/causal_graph.json`?
*   **Resolution Correctness:** How correct and effective are the agent's proposed or executed resolution steps compared to `ground_truth/resolution.md` or `ground_truth/playbook.yaml`?
*   **Efficiency:** Simulate MTTR based on the time taken by the agent to diagnose and propose/execute the resolution, potentially compared to a human baseline or optimal path defined by the ground truth. AIOps aims for significant MTTR reduction.
*   **False Positive/Negative Rate:** How often does the agent misdiagnose or fail to diagnose the incident? How often does it suggest incorrect or harmful remediation?

Similar to MuSR's human evaluation, human SRE experts could potentially be involved in validating the generated scenarios and ground truth to ensure realism and solvability.

## 9. Challenges

*   **Realism and Complexity of Data Generation:** Generating synthetic logs, metrics, and events that accurately mimic the patterns and correlations in real, complex k8s environments is challenging. Ensuring temporal consistency across different data sources and reflecting nuanced system behaviour is difficult.
*   **LLM Hallucinations:** LLMs can "hallucinate" facts or logical connections. This risk exists in both generating the causal chain (Stage 2) and translating it into realistic data (Stage 3). Ensuring the generated ground truth is logically sound and the simulated data accurately reflects it is critical.
*   **Domain Knowledge Integration:** Effectively injecting deep k8s and distributed systems domain knowledge into the LLM-based generation process is necessary for creating realistic and technically accurate scenarios. This relates to the challenge of combining causal discovery and domain knowledge in RCA.
*   **Scalability of Generation:** While LLMs offer scalability in generating content, generating high-fidelity, multi-modal operational data for hundreds or thousands of complex scenarios might be computationally expensive or require sophisticated data synthesis techniques beyond simple LLM text generation.
*   **Defining Ground Truth:** While the synthetic nature allows for *a* defined ground truth, ensuring that the defined root cause and resolution are the *most plausible* or *most effective* in a given simulated state requires careful design and potential human validation.

## 10. Future Work

*   Develop sophisticated data synthesis modules (e.g., incorporating time-series data generators, log simulators, network simulators) guided by the LLM-generated causal graphs to enhance the realism of the Simulated Cluster State.
*   Explore using Graph Neural Networks (GNNs) or other graph-based AI techniques, similar to those used in RCA or Graph RAG, within the generation pipeline to better represent and translate k8s topology and causal dependencies into simulated data.
*   Incorporate a human-in-the-loop feedback mechanism into the generation pipeline to allow SRE experts to review and refine generated scenarios, improving the quality and realism of the benchmark.
*   Expand the types of incidents and the scale of the simulated k8s clusters to cover a wider range of real-world complexity.
*   Integrate the SREBench dataset with existing AIOps platforms or testing frameworks to facilitate adoption.

## 11. Conclusion

SREBench, leveraging the synthetic data generation principles of the MuSR dataset, offers a promising approach to create a much-needed benchmark for evaluating AI SRE agent capabilities in k8s incident resolution. By generating diverse, complex scenarios with known root causes and resolutions, SREBench can provide a standardized platform to drive progress in AI-driven RCA and automated remediation, ultimately contributing to the vision of more resilient and efficient distributed systems management.
