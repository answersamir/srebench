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
                displayScenarioData(data, scenarioId);
            } catch (error) {
                console.error(`Error parsing JSON for ${scenarioId}:`, error);
                appendResults(`<div class="scenario-details error-message"><h3>${scenarioId}</h3><p>Error parsing results.json: ${error.message}</p></div>`);
            }
        };

        reader.onerror = function(e) {
            console.error(`Error reading file for ${scenarioId}:`, e);
            appendResults(`<div class="scenario-details error-message"><h3>${scenarioId}</h3><p>Error reading results.json.</p></div>`);
        };

        reader.readAsText(file);
    }

    function displayScenarioData(data, scenarioIdFromFile) {
        const scenarioDiv = document.createElement('div');
        scenarioDiv.classList.add('scenario-details');

        // Use scenario_id from JSON if available, otherwise fallback to directory name
        const scenarioId = data.scenario_id || scenarioIdFromFile;
        scenarioDiv.innerHTML = `<h3>Scenario: ${scenarioId}</h3>`;

        // Root Cause Section
        const rootCauseSection = document.createElement('div');
        rootCauseSection.classList.add('root-cause-section');
        rootCauseSection.innerHTML = '<h3>Root Cause</h3>';
        if (data.agent_output && data.agent_output.root_cause) {
            const rc = data.agent_output.root_cause;
            rootCauseSection.innerHTML += `
                <div class="component-info">
                    <span><strong>Type:</strong> ${rc.type || 'N/A'}</span>
                    ${rc.component ? `
                        <span><strong>Component Kind:</strong> ${rc.component.kind || 'N/A'}</span>
                        <span><strong>Component Name:</strong> ${rc.component.name || 'N/A'}</span>
                        <span><strong>Component Namespace:</strong> ${rc.component.namespace || 'N/A'}</span>
                    ` : '<span><strong>Component:</strong> N/A</span>'}
                </div>
                <div class="details-text">${rc.details || 'N/A'}</div>
            `;
        } else {
            rootCauseSection.innerHTML += '<p>Not found</p>';
        }
        scenarioDiv.appendChild(rootCauseSection);

        // Resolution Section
        const resolutionSection = document.createElement('div');
        resolutionSection.classList.add('resolution-section');
        resolutionSection.innerHTML = '<h3>Resolution</h3>';
        if (data.agent_output && data.agent_output.resolution) {
            const res = data.agent_output.resolution;
             resolutionSection.innerHTML += `
                <div class="component-info">
                    <span><strong>Action:</strong> ${res.action_type || 'N/A'}</span>
                    ${res.target_component ? `
                        <span><strong>Target Kind:</strong> ${res.target_component.kind || 'N/A'}</span>
                        <span><strong>Target Name:</strong> ${res.target_component.name || 'N/A'}</span>
                        <span><strong>Target Namespace:</strong> ${res.target_component.namespace || 'N/A'}</span>
                    ` : '<span><strong>Target:</strong> N/A</span>'}
                 </div>
                <div class="details-text">${res.details || 'N/A'}</div>
            `;
        } else {
            resolutionSection.innerHTML += '<p>Not found</p>';
        }
        scenarioDiv.appendChild(resolutionSection);

        // Comparison Scores
        const comparisonScoresSection = document.createElement('div');
        comparisonScoresSection.classList.add('comparison-scores-section');
        comparisonScoresSection.innerHTML = '<h3>Comparison Scores</h3>';

        if (data.comparison_scores && Object.keys(data.comparison_scores).length > 0) {
            const scoresList = document.createElement('ul');
            scoresList.classList.add('scores-list'); // Add class to ul if needed
            for (const key in data.comparison_scores) {
                const listItem = document.createElement('li');
                listItem.classList.add('score-item');
                // Sanitize key to create a valid class name if needed, or just use spans
                // const keyClass = key.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
                listItem.innerHTML = `<span class="score-label">${key}:</span> <span class="score-value">${formatScore(data.comparison_scores[key])}</span>`;
                scoresList.appendChild(listItem);
            }
            comparisonScoresSection.appendChild(scoresList);
        } else {
             comparisonScoresSection.innerHTML += '<p>Not found</p>';
        }
        scenarioDiv.appendChild(comparisonScoresSection);

        // Efficiency Score Section
        const efficiencyScoreSection = document.createElement('div');
        efficiencyScoreSection.classList.add('efficiency-score-section');
        efficiencyScoreSection.innerHTML = '<h3>Efficiency Score</h3>';
        if (data.efficiency_score !== undefined && data.efficiency_score !== null) {
            efficiencyScoreSection.innerHTML += `<p class="score-value">${formatScore(data.efficiency_score)}</p>`;
        } else {
            efficiencyScoreSection.innerHTML += '<p>Not found</p>';
        }
        scenarioDiv.appendChild(efficiencyScoreSection);

        // Causal Graph Section
        const causalGraphSection = document.createElement('div');
        causalGraphSection.classList.add('causal-graph-section');
        causalGraphSection.innerHTML = '<h3>Causal Graph</h3>';
        if (data.agent_output && data.agent_output.causal_graph) {
            const graph = data.agent_output.causal_graph;
            const graphContainerId = `graph-${scenarioId.replace(/[^a-zA-Z0-9]/g, '-')}`;
            // Create the container div first
            const graphContainerDiv = document.createElement('div');
            graphContainerDiv.id = graphContainerId;
            graphContainerDiv.classList.add('graph-container');
            causalGraphSection.appendChild(graphContainerDiv); // Add container to section

            // Append the section *before* trying to initialize Vis.js
            scenarioDiv.appendChild(causalGraphSection);

            // Optional: Render graph with Vis.js
            if (typeof vis !== 'undefined') {
                // Now find the container within the appended section
                const container = causalGraphSection.querySelector(`#${graphContainerId}`);
                if (container) {
                    try {
                        const nodes = new vis.DataSet(graph.nodes);
                        const mappedEdges = graph.edges.map(edge => ({
                            from: edge.source,
                            to: edge.target,
                            label: edge.relation,
                            arrows: 'to'
                        }));
                        const edges = new vis.DataSet(mappedEdges);
                        const graphData = { nodes: nodes, edges: edges };
                        const options = {
                            layout: {
                                hierarchical: {
                                    enabled: true,
                                    direction: 'UD',
                                    sortMethod: 'directed',
                                    levelSeparation: 200,
                                    nodeSpacing: 150,
                                    treeSpacing: 250,
                                    blockShifting: true,
                                    edgeMinimization: true
                                }
                            },
                            edges: {
                                font: { align: 'middle', size: 12 },
                                arrows: 'to'
                            },
                            nodes: {
                                shape: 'box',
                                widthConstraint: { maximum: 150 },
                                font: { multi: true }
                            },
                            interaction: {
                                dragNodes: false,
                                dragView: false,
                                zoomView: false,
                                selectable: false,
                                tooltipDelay: 300,
                                navigationButtons: false,
                                keyboard: false
                            }
                        };
                        new vis.Network(container, graphData, options);
                    } catch (visError) {
                         console.error(`Error rendering Vis.js graph for ${scenarioId}:`, visError);
                         container.innerHTML = `<p class="error-message">Error rendering graph: ${visError.message}</p>`;
                    }
                } else {
                     console.error(`Graph container #${graphContainerId} not found after appending for ${scenarioId}.`);
                     causalGraphSection.innerHTML += `<p class="error-message">Could not find graph container.</p>`; // Add error inside section
                }
            } else {
                 // Handle case where Vis.js is not loaded but graph data exists
                 graphContainerDiv.innerHTML = `<p>(Vis.js library not loaded - graph display unavailable)</p>`; // Add message to container
            }
        } else {
            causalGraphSection.innerHTML += '<p>Not found</p>';
            // Append the section even if not found, to maintain structure
            scenarioDiv.appendChild(causalGraphSection);
        }

        // Ensure the main scenarioDiv is appended at the end, containing all sections
        appendResults(scenarioDiv);
    }

    function formatScore(score) {
        if (typeof score === 'number') {
            return score.toFixed(3); // Format to 3 decimal places
        }
        return score; // Return as is if not a number
    }

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

     function appendResults(elementOrHtml) {
        if (typeof elementOrHtml === 'string') {
            resultsDisplayDiv.innerHTML += elementOrHtml;
        } else {
            resultsDisplayDiv.appendChild(elementOrHtml);
        }
    }
});