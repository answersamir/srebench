/**
 * Script for the SREBench results browsing page (browse_results.html).
 * Handles fetching the list of available runs and displaying results for a selected run.
 */

document.addEventListener('DOMContentLoaded', () => {
    const runSelect = document.getElementById('run-select');
    const loadingStatus = document.getElementById('loading-status');
    const summaryContent = document.getElementById('summary-content');
    const resultsDisplay = document.getElementById('scenarios-content'); // Target for detailed results

    /**
     * Fetches the list of available benchmark runs from the backend.
     */
    async function fetchRunList() {
        setLoadingStatus('Loading available runs...');
        try {
            console.log('Fetching run list from /api/list_runs');
            const response = await fetch('/api/list_runs');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const runIds = await response.json(); // Expecting a JSON array of strings

            populateRunSelect(runIds); // Pass the fetched run IDs
            setLoadingStatus('Please select a run.');

        } catch (error) {
            console.error('Error fetching run list:', error);
            setLoadingStatus(`Error loading runs: ${error.message}. Please try refreshing.`);
            runSelect.disabled = true;
        }
    }

    /**
     * Populates the run selection dropdown.
     * @param {string[]} runIds - An array of run identifiers.
     */
    function populateRunSelect(runIds) {
        runSelect.innerHTML = '<option value="">-- Select a previous run --</option>'; // Clear existing options except placeholder
        if (runIds && runIds.length > 0) {
            runIds.forEach(runId => {
                const option = document.createElement('option');
                option.value = runId;
                option.textContent = runId;
                runSelect.appendChild(option);
            });
            runSelect.disabled = false;
        } else {
            runSelect.innerHTML = '<option value="">-- No runs found --</option>';
            runSelect.disabled = true;
        }
    }

    /**
     * Fetches the detailed results for a specific run ID.
     * @param {string} runId - The identifier of the run to fetch.
     */
    async function fetchRunDetails(runId) {
        if (!runId) {
            clearResultsDisplay();
            setLoadingStatus('Please select a run.');
            return;
        }

        setLoadingStatus(`Loading results for ${runId}...`);
        clearResultsDisplay(); // Clear previous results

        try {
            console.log(`Fetching results for run ${runId} from /api/get_run_results?run_id=${runId}`);
            const response = await fetch(`/api/get_run_results?run_id=${encodeURIComponent(runId)}`);
            if (!response.ok) {
                // Attempt to read error message from response body if available
                let errorBody = '';
                try {
                    errorBody = await response.text();
                } catch (e) {
                    // Ignore if reading body fails
                }
                throw new Error(`HTTP error! status: ${response.status}${errorBody ? ` - ${errorBody}` : ''}`);
            }
            const resultsData = await response.json(); // Assign fetched data

            // Check if the expected data structure is present
            if (
                !resultsData ||
                typeof resultsData !== 'object' ||
                !resultsData.summary ||
                typeof resultsData.summary !== 'object' ||
                !Array.isArray(resultsData.scenarios) ||
                resultsData.scenarios.length === 0
            ) {
                console.warn('Received data does not match expected structure:', resultsData);
                throw new Error('Received data structure is invalid.');
                 // Decide how to handle unexpected structure: throw error or display partial data?
                 // For now, let's proceed but log a warning. The display function might handle missing parts.
                 // Alternatively, throw new Error('Received data structure is invalid.');
            }

            displayRunResults(resultsData); // Display the fetched results
            setLoadingStatus(`Displaying results for ${runId}.`);

        } catch (error) {
            console.error(`Error fetching details for run ${runId}:`, error);
            setLoadingStatus(`Error loading results for ${runId}: ${error.message}`);
            clearResultsDisplay(true); // Clear and show error message
        }
    }

    /**
     * Displays the fetched run results (summary and details).
     * @param {object} resultsData - The complete results object for the run.
     */
    function displayRunResults(resultsData) {
        // 1. Display Summary
        if (resultsData.summary) {
            const meta = resultsData.summary;
            // {'run_id': '20250502_232815', 'scenario_count': 1, 'average_efficiency_score': 7.430467128753662}
            summaryContent.innerHTML = `
                <p><strong>Run ID:</strong> ${meta.run_id || 'N/A'}</p>
                <p><strong>Agent:</strong> ${meta.agent_name || 'N/A'}</p>
                <p><strong>Overall Score:</strong> ${formatScore(meta.average_efficiency_score)}</p> <!-- Updated to use average_efficiency_score -->
                <p><strong>Scenarios Evaluated:</strong> ${meta.scenario_count || 'N/A'}</p> <!-- Updated to use scenario_count -->
            `;
        } else {
            summaryContent.innerHTML = '<p>Run summary data not available.</p>';
        }

        // 2. Display Detailed Scenario Results
        resultsDisplay.innerHTML = ''; // Clear previous detailed results
        if (resultsData.scenarios && Object.keys(resultsData.scenarios).length > 0) {
            for (const scenarioId in resultsData.scenarios) {
                const scenarioData = resultsData.scenarios[scenarioId];
                // Use the utility function to display each scenario
                // Pass the target div and potentially options like title tag
                displayScenarioData(scenarioData, scenarioId, resultsDisplay, { titleTag: 'h4' });
            }
        } else {
            resultsDisplay.innerHTML = '<p>No detailed scenario results available for this run. Please ensure the scenarios data is correctly populated in the backend response.</p>';
        }
    }

    /**
     * Updates the loading status message.
     * @param {string} message - The message to display.
     */
    function setLoadingStatus(message) {
        if (loadingStatus) {
            loadingStatus.textContent = message;
        }
    }

    /**
     * Clears the results display areas.
     * @param {boolean} showError - If true, display an error message instead of default text.
     */
    function clearResultsDisplay(showError = false) {
        if (summaryContent) {
            summaryContent.innerHTML = showError ? '<p class="error-message">Could not load run summary.</p>' : '<p>Select a run to view its summary.</p>';
        }
        if (resultsDisplay) {
            resultsDisplay.innerHTML = showError ? '<p class="error-message">Could not load detailed results.</p>' : '<p>Select a run to view detailed results.</p>';
        }
    }

    // --- Event Listeners ---
    runSelect.addEventListener('change', (event) => {
        const selectedRunId = event.target.value;
        fetchRunDetails(selectedRunId);
    });

    // --- Initial Load ---
    fetchRunList();
    clearResultsDisplay(); // Set initial state

});