document.addEventListener('DOMContentLoaded', () => {
    // --- Get all necessary DOM elements ---
    const sendButton = document.getElementById('send-button');
    const promptInput = document.getElementById('prompt-input');
    const resultsContainer = document.getElementById('results-container');
    const llmResponseEl = document.getElementById('llm-response');
    const piiListEl = document.getElementById('pii-detected-list');
    const promptDisplayEl = document.getElementById('prompt-display');
    const piiCountEl = document.getElementById('pii-count');

    // --- Set an initial example prompt ---
    const examplePrompt = "Paraphrase this: John Doe lives in Dublin, CA and works for Acme Corp.";
    promptInput.value = examplePrompt;

    // --- Main event listener for the send button ---
    sendButton.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        if (!prompt) {
            alert('Please enter a prompt.');
            return;
        }

        // --- 1. Set UI to a loading state ---
        sendButton.disabled = true;
        sendButton.textContent = 'Processing...';
        resultsContainer.classList.remove('active'); // Hide previous results
        llmResponseEl.textContent = 'Thinking...';
        piiListEl.innerHTML = '';
        promptDisplayEl.innerHTML = 'Analyzing...';
        piiCountEl.textContent = '... items';

        try {
            // --- 2. Call the FastAPI backend ---
            const response = await fetch('http://127.0.0.1:8000/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: "Unknown server error" }));
                throw new Error(`Server error: ${response.status} - ${errorData.detail || 'No details'}`);
            }

            const data = await response.json();

            // --- 3. Update the UI with the results ---
            // Display LLM's response
            llmResponseEl.textContent = data.llm_response;

            // Display detected PII count
            piiCountEl.textContent = `${data.named_entities.length} items`;
            
            // Highlight the original prompt and list the entities
            if (data.named_entities.length > 0) {
                let highlightedPrompt = prompt;
                
                // Sort entities by length descending to avoid replacement issues (e.g., "Dublin, CA" before "Dublin")
                const sortedEntities = data.named_entities.sort((a, b) => b.text.length - a.text.length);

                sortedEntities.forEach(entity => {
                    // Use a regex for global replacement to handle multiple occurrences
                    const regex = new RegExp(escapeRegExp(entity.text), 'g');
                    const highlightClass = `highlight highlight-${entity.label.toLowerCase()}`;
                    const highlightSpan = `<span class="${highlightClass}">${entity.text}</span>`;
                    highlightedPrompt = highlightedPrompt.replace(regex, highlightSpan);

                    // Add to the detected list
                    const piiItem = document.createElement('div');
                    piiItem.className = 'detected-item';
                    piiItem.innerHTML = `<span><strong>${entity.label}:</strong> ${entity.text}</span>`;
                    piiListEl.appendChild(piiItem);
                });
                promptDisplayEl.innerHTML = highlightedPrompt;
            } else {
                promptDisplayEl.textContent = prompt; // No highlighting needed
                piiListEl.innerHTML = '<span>No PII detected.</span>';
            }

            // --- 4. Show the results container ---
            resultsContainer.classList.add('active');

        } catch (error) {
            console.error('Error processing prompt:', error);
            llmResponseEl.textContent = `An error occurred: ${error.message}`;
            promptDisplayEl.textContent = 'Failed to process.';
             resultsContainer.classList.add('active'); // Show container even on error
        } finally {
            // --- 5. Reset the button state ---
            sendButton.disabled = false;
            sendButton.textContent = 'Process and Paraphrase';
        }
    });

    // Helper function to escape special characters for regex
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
});