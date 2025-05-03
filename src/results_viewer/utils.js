/**
 * Shared utility functions for the results viewer.
 */

/**
 * Formats a score to a fixed number of decimal places.
 * @param {number|string} score - The score to format.
 * @returns {string} The formatted score or the original value if not a number.
 */
function formatScore(score) {
    if (typeof score === 'number') {
        return score.toFixed(3); // Format to 3 decimal places
    }
    return score; // Return as is if not a number
}

/**
 * Appends an HTML element or string to a target div.
 * Handles potential errors if the target div is not found.
 * @param {HTMLElement|string} elementOrHtml - The element or HTML string to append.
 * @param {HTMLElement} targetDiv - The container element to append to.
 */
function appendResults(elementOrHtml, targetDiv) {
    if (!targetDiv) {
        console.error("Target div for appendResults is null or undefined.");
        // Optionally create a fallback or display an error message globally
        const errorMsg = document.createElement('p');
        errorMsg.className = 'error-message';
        errorMsg.textContent = 'Error: Could not append results, target display area not found.';
        document.body.appendChild(errorMsg); // Append to body as a last resort
        return;
    }
    if (typeof elementOrHtml === 'string') {
        targetDiv.insertAdjacentHTML('beforeend', elementOrHtml); // Safer than innerHTML +=
    } else if (elementOrHtml instanceof Node) {
        targetDiv.appendChild(elementOrHtml);
    } else {
        console.error("Invalid content type passed to appendResults:", elementOrHtml);
    }
}


/**
 * Displays the structured scenario evaluation data in a target div.
 * @param {object} data - The scenario result data object.
 * @param {string} scenarioIdFromFile - The ID derived from the filename or context.
 * @param {HTMLElement} targetDiv - The container element to display results in.
 * @param {object} [options={}] - Optional display options.
 * @param {string} [options.mainTitle] - Optional main title for the result block.
 * @param {string} [options.titleTag='h3'] - HTML tag for section titles (e.g., 'h3', 'h4').
 */
function displayScenarioData(data, scenarioIdFromFile, targetDiv, options = {}) {
    if (!targetDiv) {
        console.error("Target div for displayScenarioData is null or undefined.");
        targetDiv = document.createElement('div'); // Fallback
        targetDiv.innerHTML = '<p class="error-message">Error: Results display area not found.</p>';
        document.body.appendChild(targetDiv); // Append somewhere to show the error
        return; // Stop further processing
    }

    const scenarioDiv = document.createElement('div');
    scenarioDiv.classList.add('scenario-details');

    // Use scenario_id from JSON if available, otherwise fallback
    const displayId = data.scenario_id || scenarioIdFromFile;
    const titleTag = options.titleTag || 'h3'; // Default to h3

    // Clear previous results *within the targetDiv* if needed (caller might handle this)
    // Example: while (targetDiv.firstChild) { targetDiv.removeChild(targetDiv.firstChild); }

    // Add optional main title for the whole scenario block
    if (options.mainTitle) {
         const mainTitleElement = document.createElement(titleTag === 'h4' ? 'h2' : 'h3'); // Adjust main title level based on section level
         mainTitleElement.textContent = `${options.mainTitle}: ${displayId}`;
         scenarioDiv.appendChild(mainTitleElement);
    } else {
         // Default behavior from script.js
         scenarioDiv.innerHTML = `<${titleTag}>Scenario: ${displayId}</${titleTag}>`;
    }


    // --- Render Sections (Common Logic) ---

    // Root Cause Section
    const rootCauseSection = document.createElement('div');
    rootCauseSection.classList.add('result-section', 'root-cause-section');
    rootCauseSection.innerHTML = `<${titleTag}>Root Cause</${titleTag}>`;
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
    resolutionSection.classList.add('result-section', 'resolution-section');
    resolutionSection.innerHTML = `<${titleTag}>Resolution</${titleTag}>`;
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
    comparisonScoresSection.classList.add('result-section', 'comparison-scores-section');
    comparisonScoresSection.innerHTML = `<${titleTag}>Comparison Scores</${titleTag}>`;

    if (data.comparison_scores && Object.keys(data.comparison_scores).length > 0) {
        const scoresList = document.createElement('ul');
        scoresList.classList.add('scores-list');
        for (const key in data.comparison_scores) {
            const listItem = document.createElement('li');
            listItem.classList.add('score-item');
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
    efficiencyScoreSection.classList.add('result-section', 'efficiency-score-section');
    efficiencyScoreSection.innerHTML = `<${titleTag}>Efficiency Score</${titleTag}>`;
    if (data.efficiency_score !== undefined && data.efficiency_score !== null) {
        efficiencyScoreSection.innerHTML += `<p class="score-value">${formatScore(data.efficiency_score)}</p>`;
    } else {
        efficiencyScoreSection.innerHTML += '<p>Not found</p>';
    }
    scenarioDiv.appendChild(efficiencyScoreSection);

    // Causal Graph Section
    const causalGraphSection = document.createElement('div');
    causalGraphSection.classList.add('result-section', 'causal-graph-section');
    causalGraphSection.innerHTML = `<${titleTag}>Causal Graph</${titleTag}>`;
    let graphContainerId = null;
    let graphDataForVis = null;

    if (data.agent_output && data.agent_output.causal_graph && data.agent_output.causal_graph.nodes && data.agent_output.causal_graph.edges) {
        graphDataForVis = data.agent_output.causal_graph; // Store for later
        graphContainerId = `graph-${displayId.replace(/[^a-zA-Z0-9]/g, '-')}`;
        const graphContainerDiv = document.createElement('div');
        graphContainerDiv.id = graphContainerId;
        graphContainerDiv.classList.add('graph-container');
        causalGraphSection.appendChild(graphContainerDiv);
    } else {
        causalGraphSection.innerHTML += '<p>Not found or invalid graph data</p>';
    }
    scenarioDiv.appendChild(causalGraphSection); // Append section regardless

    // Append the completed scenarioDiv to the main target area
    appendResults(scenarioDiv, targetDiv);

    // Initialize Vis.js *after* the scenarioDiv is appended to the DOM
    if (graphContainerId && graphDataForVis && typeof vis !== 'undefined') {
        // Find the container *within the targetDiv* where it was just appended
        const containerElement = targetDiv.querySelector(`#${graphContainerId}`);
        if (containerElement) {
             initializeVisGraph(containerElement, graphDataForVis, displayId);
        } else {
             console.error(`Graph container #${graphContainerId} not found within targetDiv after appending.`);
             // Attempt to add error message directly to the graph section
             const graphSectionInDom = targetDiv.querySelector('.causal-graph-section:last-child'); // Find the last added graph section
             if(graphSectionInDom && !graphSectionInDom.querySelector('.error-message')) {
                 appendResults(`<p class="error-message">Could not find graph container element (#${graphContainerId}).</p>`, graphSectionInDom);
             }
        }
    } else if (graphContainerId && graphDataForVis) {
         // Vis.js not loaded, add message to the container if it exists
         const containerElement = targetDiv.querySelector(`#${graphContainerId}`);
         if (containerElement) {
             containerElement.innerHTML = `<p>(Vis.js library not loaded - graph display unavailable)</p>`;
         }
    }
}


/**
 * Initializes a Vis.js network graph in the specified container.
 * @param {HTMLElement} container - The DOM element to render the graph in.
 * @param {object} graphData - The graph data ({ nodes: [], edges: [] }).
 * @param {string} scenarioId - Identifier for logging purposes.
 */
function initializeVisGraph(container, graphData, scenarioId) {
     if (!container) {
         console.error(`Cannot initialize Vis graph: container element is null for ${scenarioId}.`);
         return;
     }
     try {
         // Ensure nodes and edges are arrays
         const nodesArray = Array.isArray(graphData.nodes) ? graphData.nodes : [];
         const edgesArray = Array.isArray(graphData.edges) ? graphData.edges : [];

         if (nodesArray.length === 0 && edgesArray.length === 0) {
             container.innerHTML = '<p>Graph data is empty.</p>';
             return;
         }

         const nodes = new vis.DataSet(nodesArray.map(node => ({
             id: node.id, // Ensure ID is present
             label: node.label || node.id, // Use label or fallback to ID
             // Include other node properties if needed
             shape: 'box',
             margin: 10,
             widthConstraint: { maximum: 140 },
             font: { multi: 'html', size: 12 }
         })));

         const mappedEdges = edgesArray.map(edge => ({
             from: edge.source,
             to: edge.target,
             label: edge.relation,
             arrows: 'to', // Ensure arrows are shown
             font: { align: 'middle', size: 11 }
         }));
         const edges = new vis.DataSet(mappedEdges);

         const visData = { nodes: nodes, edges: edges };
         const options = {
             layout: {
                 hierarchical: {
                     enabled: true,
                     direction: 'UD', // Up-Down layout
                     sortMethod: 'directed', // Sort based on edge direction
                     levelSeparation: 180,
                     nodeSpacing: 180,
                     treeSpacing: 200,
                     blockShifting: true,
                     edgeMinimization: true,
                     parentCentralization: true
                 }
             },
             edges: {
                 smooth: {
                    enabled: true,
                    type: "cubicBezier",
                    forceDirection: "vertical",
                    roundness: 0.4
                 },
                 arrows: { to: { enabled: true, scaleFactor: 0.7 } } // Ensure arrows are enabled
             },
             physics: {
                 enabled: false // Disable physics for hierarchical layout
             },
             interaction: {
                 dragNodes: false, // Disable node dragging
                 dragView: false, // Disable panning
                 zoomView: false, // Disable zooming
                 selectable: false, // Also disable selection as interaction is off
                 hover: true,
                 tooltipDelay: 200
             }
         };
         new vis.Network(container, visData, options);
     } catch (visError) {
          console.error(`Error rendering Vis.js graph for ${scenarioId}:`, visError);
          container.innerHTML = `<p class="error-message">Error rendering graph: ${visError.message}</p>`;
     }
}