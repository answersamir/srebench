document.addEventListener('DOMContentLoaded', () => {
    const runInput = document.getElementById('run-input');
    const runSummaryDiv = document.getElementById('run-summary');
    const resultsDisplayDiv = document.getElementById('results-display');

    runInput.addEventListener('change', handleDirectorySelect);

    function handleDirectorySelect(event) {
        const files = event.target.files;
        clearPreviousResults();

        if (!files || files.length === 0) {
            updateSummary('No directory selected.');
            updateResultsDisplay('<p>Please select a benchmark run directory.</p>');
            return;
        }

        // Extract the base directory name (e.g., "20250502_232815")
        const firstFilePathParts = files[0].webkitRelativePath.split('/');
        const runDirectoryName = firstFilePathParts.length > 1 ? firstFilePathParts[0] : 'Selected Run';
        updateSummary(`Selected Run: <strong>${runDirectoryName}</strong>`);

        const scenarioFiles = groupFilesByScenario(files);
        const scenariosFound = Object.keys(scenarioFiles).length > 0;

        if (!scenariosFound) {
            updateResultsDisplay('<p class="error-message">No scenario folders (e.g., scenario_XXX) containing results.json found in the selected directory.</p>');
            return;
        }

        updateResultsDisplay(''); // Clear the initial message

        let resultsDisplayedCount = 0;
        for (const scenarioDir in scenarioFiles) {
            const resultsFile = scenarioFiles[scenarioDir].find(f => f.name === 'results.json');
            if (resultsFile) {
                readAndDisplayResults(resultsFile, scenarioDir);
                resultsDisplayedCount++;
            } else {
                 console.warn(`results.json not found in ${scenarioDir}`);
                 appendResults(`<div class="scenario-details error-message"><h3>${scenarioDir}</h3><p>Error: results.json not found.</p></div>`);
            }
        }

         if (resultsDisplayedCount === 0) {
             updateResultsDisplay('<p class="error-message">Found scenario folders, but none contained a readable results.json file.</p>');
         }
    }

    function groupFilesByScenario(files) {
        const scenarios = {};
        const scenarioPattern = /^[^/]+\/(scenario_\d+)\//; // Matches "run_dir/scenario_XXX/"

        for (const file of files) {
            const match = file.webkitRelativePath.match(scenarioPattern);
            if (match) {
                const scenarioDir = match[1]; // e.g., "scenario_001"
                if (!scenarios[scenarioDir]) {
                    scenarios[scenarioDir] = [];
                }
                // Store the file object itself for later reading
                 // We only really need results.json, but store all for potential future use
                if (file.webkitRelativePath.endsWith('results.json')) {
                     scenarios[scenarioDir].push(file);
                }
            }
        }
        return scenarios;
    }

    function readAndDisplayResults(file, scenarioId) {
        const reader = new FileReader();

        reader.onload = function(e) {
            try {
                const content = e.target.result;
                const data = JSON.parse(content);
                // Use shared function, passing the target div
                displayScenarioData(data, scenarioId, resultsDisplayDiv);
            } catch (error) {
                console.error(`Error parsing JSON for ${scenarioId}:`, error);
                // Use shared appendResults
                appendResults(`<div class="scenario-details error-message"><h3>${scenarioId}</h3><p>Error parsing results.json: ${error.message}</p></div>`, resultsDisplayDiv);
            }
        };

        reader.onerror = function(e) {
            console.error(`Error reading file for ${scenarioId}:`, e);
            // Use shared appendResults
            appendResults(`<div class="scenario-details error-message"><h3>${scenarioId}</h3><p>Error reading results.json.</p></div>`, resultsDisplayDiv);
        };

        reader.readAsText(file);
    }

    // Removed displayScenarioData - now in utils.js
    // Removed formatScore - now in utils.js

    function clearPreviousResults() {
        updateSummary('No run selected.');
        updateResultsDisplay('<p>Select a run directory to view results.</p>');
    }

    function updateSummary(htmlContent) {
        // Ensure the title remains
        runSummaryDiv.innerHTML = `<h2>Run Summary</h2>${htmlContent}`;
    }

    function updateResultsDisplay(htmlContent) {
         // Ensure the title remains
        resultsDisplayDiv.innerHTML = `<h2>Scenario Details</h2>${htmlContent}`;
    }

    // Removed appendResults - now in utils.js
    // Removed initializeVisGraph - now in utils.js
});