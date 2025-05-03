document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scenario-form');
    const submitButton = document.getElementById('submit-button');
    const statusMessage = document.getElementById('status-message');
    // const resultOutput = document.getElementById('result-output').querySelector('code'); // Old output
    const resultsDisplayDiv = document.getElementById('results-display'); // New output container

// --- Textarea Auto-Resizing Logic ---
    function autoResizeTextarea(textarea) {
        // Temporarily shrink height to get accurate scrollHeight
        textarea.style.height = 'auto';
        // Set height to scrollHeight to fit content, adding a small buffer if needed (e.g., 2px)
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }

    // Apply resizing to all textareas within the form
    const textareas = form.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        // Initial resize on load
        autoResizeTextarea(textarea);
        // Resize on input
        textarea.addEventListener('input', () => autoResizeTextarea(textarea));
    });
    // --- End Textarea Auto-Resizing Logic ---
    // Input fields
    const descriptionInput = document.getElementById('description');
    const metadataInput = document.getElementById('metadata');
    const logsInput = document.getElementById('logs');
    const metricsInput = document.getElementById('metrics');
    const topologyInput = document.getElementById('topology');
    const configurationInput = document.getElementById('configuration');
    const causalGraphInput = document.getElementById('causal_graph');
    const resolutionInput = document.getElementById('resolution');
    const rootCauseInput = document.getElementById('root_cause');
    const scenarioSelect = document.getElementById('scenario-select'); // Added

    // --- Autofill Logic ---

    /**
     * Fetches the list of available scenario IDs and populates the dropdown.
     */
    async function populateScenarioDropdown() {
        try {
            const response = await fetch('/api/scenarios');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const scenarioIds = await response.json();

            if (Array.isArray(scenarioIds)) {
                scenarioIds.forEach(id => {
                    const option = document.createElement('option');
                    option.value = id;
                    option.textContent = id;
                    scenarioSelect.appendChild(option);
                });
            } else {
                console.error('Expected an array of scenario IDs, but received:', scenarioIds);
                statusMessage.textContent = 'Error: Could not load scenario list (invalid format).';
                statusMessage.style.color = 'red';
            }
        } catch (error) {
            console.error('Error fetching scenario list:', error);
            statusMessage.textContent = `Error loading scenarios: ${error.message}`;
            statusMessage.style.color = 'red';
        }
    }

/**
     * Fills the form fields based on the provided scenario data object.
     * @param {object} data - The scenario data object (flat structure from backend).
     */
    function fillForm(data) {
        descriptionInput.value = data.description || '';
        metadataInput.value = data.metadata || '{}'; // Default to empty JSON object

        // State Files (directly available in the flat structure)
        logsInput.value = data.logs || '';
        metricsInput.value = data.metrics || '{}';
        topologyInput.value = data.topology || '{}';
        configurationInput.value = data.configuration || '';

        // Ground Truth Files (directly available in the flat structure)
        causalGraphInput.value = data.causal_graph || '{}';
        resolutionInput.value = data.resolution || '{}';
        rootCauseInput.value = data.root_cause || '{}';

        // Trigger resize for all textareas after filling
        const allTextareas = form.querySelectorAll('textarea');
        allTextareas.forEach(textarea => autoResizeTextarea(textarea));
    }

    /**
     * Fetches data for the selected scenario and fills the form.
     * @param {string} scenarioId - The ID of the scenario to fetch.
     */
    async function fetchAndFillScenarioData(scenarioId) {
        if (!scenarioId) {
            // Optionally clear the form if "-- Select --" is chosen
            // fillForm({}); // Uncomment to clear form
            return;
        }

        statusMessage.textContent = `Loading scenario ${scenarioId}...`;
        statusMessage.style.color = 'orange';

        try {
            const response = await fetch(`/api/scenarios/${scenarioId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const scenarioData = await response.json();

            console.log(`Fetched data for ${scenarioId}:`, scenarioData); // Added log

            // The backend returns a flat object directly
            if (scenarioData) { // Check if data is not null/undefined
                fillForm(scenarioData); // Pass the flat data directly
                statusMessage.textContent = `Scenario ${scenarioId} loaded.`;
                statusMessage.style.color = 'green';
            } else {
                throw new Error('Scenario data is empty or invalid.');
            }

        } catch (error) {
            console.error(`Error fetching data for scenario ${scenarioId}:`, error);
            statusMessage.textContent = `Error loading scenario ${scenarioId}: ${error.message}`;
            statusMessage.style.color = 'red';
            // Optionally clear form on error
            // fillForm({});
        }
    }
    // Event listener for the scenario dropdown
    scenarioSelect.addEventListener('change', (event) => {
        const selectedScenarioId = event.target.value;
        fetchAndFillScenarioData(selectedScenarioId);
    });

    // Initial population of the dropdown
    populateScenarioDropdown();

    // --- End Autofill Logic ---

    // --- Helper function for JSON validation ---
    function isValidJson(str, fieldName) {
        if (!str.trim()) return true; // Allow empty strings
        try {
            JSON.parse(str);
            return true;
        } catch (e) {
            statusMessage.textContent = `Error: Invalid JSON in '${fieldName}'. Please correct it.`;
            statusMessage.style.color = 'red';
            console.error(`Invalid JSON in ${fieldName}:`, e);
            return false;
        }
    }

    form.addEventListener('submit', async (event) => {
        console.log('Form submit event triggered.');
        event.preventDefault(); // Prevent default form submission

        console.log('Default form submission prevented.');
        statusMessage.textContent = 'Validating input...';
        statusMessage.style.color = 'orange';
        submitButton.disabled = true;
        resultsDisplayDiv.innerHTML = ''; // Clear previous results/errors

        // --- Input Validation ---
        const inputsToValidate = {
            'Metadata': metadataInput,
            'Metrics': metricsInput,
            'Topology': topologyInput,
            'Causal Graph': causalGraphInput,
            'Resolution': resolutionInput,
            'Root Cause': rootCauseInput
        };

        let isValid = true;
        for (const [name, inputElement] of Object.entries(inputsToValidate)) {
            if (!isValidJson(inputElement.value, name)) {
                isValid = false;
                inputElement.focus(); // Focus the first invalid field
                break; // Stop validation on first error
            }
        }

        if (!isValid) {
            submitButton.disabled = false; // Re-enable button if validation fails
            return; // Stop submission
        }
        // --- End Validation ---

        statusMessage.textContent = 'Submitting...'; // Update status after validation

        // Construct payload *after* validation
        const payload = {
            description: descriptionInput.value,
            // Parse validated JSON strings before sending
            metadata: metadataInput.value.trim() ? JSON.parse(metadataInput.value) : {},
            state_files: {
                "logs.jsonl": logsInput.value, // Assuming logs are line-delimited, not single JSON
                "metrics.json": metricsInput.value.trim() ? JSON.parse(metricsInput.value) : {},
                "topology.json": topologyInput.value.trim() ? JSON.parse(topologyInput.value) : {},
                "configuration.yaml": configurationInput.value // YAML is not JSON, no parse needed
            },
            ground_truth_files: {
                "causal_graph.json": causalGraphInput.value.trim() ? JSON.parse(causalGraphInput.value) : {},
                "resolution.json": resolutionInput.value.trim() ? JSON.parse(resolutionInput.value) : {},
                "root_cause.json": rootCauseInput.value.trim() ? JSON.parse(rootCauseInput.value) : {}
            }
        };


        try {
            const response = await fetch('/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (!response.ok || result.error) {
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }

            // Clear previous results before displaying new ones
            while (resultsDisplayDiv.firstChild) {
                resultsDisplayDiv.removeChild(resultsDisplayDiv.firstChild);
            }
            // Use the shared display function with options for custom page
            displayScenarioData(result, 'custom-scenario-result', resultsDisplayDiv, {
                mainTitle: 'Evaluation Result', // Set a main title
                titleTag: 'h4' // Use H4 for section titles as before
            });
            statusMessage.textContent = 'Complete';
            statusMessage.style.color = 'green';

        } catch (error) {
            console.error('Submission error:', error);
            statusMessage.textContent = `Error: ${error.message}`;
            statusMessage.style.color = 'red';
            // Display error in the results area if possible
            resultsDisplayDiv.innerHTML = `<p class="error-message">Evaluation failed: ${error.message}. Check console for details.</p>`;
        } finally {
            submitButton.disabled = false;
        }
    });

    // Rendering functions are now in utils.js
});