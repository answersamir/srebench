document.addEventListener('DOMContentLoaded', () => {
    const runButton = document.getElementById('run-benchmark-button');
    const statusMessageDiv = document.getElementById('status-message');

    if (!runButton || !statusMessageDiv) {
        console.error('Required elements (button or status div) not found.');
        if (statusMessageDiv) {
            statusMessageDiv.textContent = 'Error: Page elements missing. Cannot initialize.';
            statusMessageDiv.className = 'status-box error'; // Assuming 'error' class for styling
        }
        return;
    }

    runButton.addEventListener('click', () => {
        statusMessageDiv.textContent = 'Benchmark run initiated...';
        statusMessageDiv.className = 'status-box info'; // Assuming 'info' class

        // Placeholder for the actual API call
        fetch('/api/run_benchmark', {
            method: 'POST',
            // Headers might be needed depending on the backend API
            // headers: {
            //     'Content-Type': 'application/json',
            // },
            // Body might be needed if sending parameters
            // body: JSON.stringify({ /* parameters */ }),
        })
        .then(response => {
            if (response.ok) {
                // You might want to parse the response if the backend sends data
                // return response.json();
                return { success: true }; // Placeholder success object
            } else {
                // Throw an error to be caught by the .catch block
                throw new Error(`Server responded with status: ${response.status}`);
            }
        })
        .then(data => {
            // Handle successful API response
            statusMessageDiv.textContent = 'Benchmark started successfully.';
            statusMessageDiv.className = 'status-box success'; // Assuming 'success' class
            console.log('Benchmark start request successful:', data);
        })
        .catch(error => {
            // Handle errors during fetch or from the server response
            statusMessageDiv.textContent = `Error starting benchmark: ${error.message}`;
            statusMessageDiv.className = 'status-box error'; // Assuming 'error' class
            console.error('Error starting benchmark:', error);
        });
    });
});