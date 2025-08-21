document.addEventListener('DOMContentLoaded', () => {
    const messagesDiv = document.getElementById('messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const casefileListDiv = document.getElementById('casefile-list');
    const newCasefileForm = document.getElementById('new-casefile-form');
    const newCasefileNameInput = document.getElementById('new-casefile-name');
    const newCasefileDescTextarea = document.getElementById('new-casefile-desc');

    const USER_ID = 'G'; // Placeholder for user ID
    let currentCasefileId = null;
    let chatHistory = [];

    // --- API Communication ---
    async function fetchCasefiles() {
        try {
            const response = await fetch('http://localhost:8000/api/v1/casefiles');
            if (!response.ok) throw new Error('Failed to fetch casefiles');
            const casefilesJson = await response.json();
            console.log('Fetched casefiles (JSON strings):', casefilesJson);
            return casefilesJson.map(jsonString => JSON.parse(jsonString));
        } catch (error) {
            console.error('Error fetching casefiles:', error);
            displayMessage(`Error: Could not load casefiles.`, 'agent');
            return [];
        }
    }

    async function createCasefile(name, description) {
        try {
            const response = await fetch('http://localhost:8000/api/v1/casefiles', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-User-ID': USER_ID },
                body: JSON.stringify({ name, description }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create casefile');
            }
            return await response.text();
        } catch (error) {
            console.error('Error creating casefile:', error);
            displayMessage(`Error: ${error.message}`, 'agent');
            return null;
        }
    }

    async function sendMessageToBackend(message) {
        if (!currentCasefileId) {
            displayMessage('Please select a casefile before starting a chat.', 'agent');
            return;
        }

        displayMessage(message, 'user');
        chatHistory.push({ role: 'user', parts: [{ text: message }] });

        try {
            const response = await fetch('http://localhost:8000/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': USER_ID
                },
                body: JSON.stringify({
                    user_input: message,
                    casefile_id: currentCasefileId,
                    history: chatHistory.slice(0, -1) // Send history excluding current message
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Something went wrong');
            }

            const data = await response.json();
            displayMessage(data.response, 'agent');
            chatHistory.push({ role: 'model', parts: [{ text: data.response }] });

        } catch (error) {
            console.error('Error sending message:', error);
            displayMessage(`Error: ${error.message}`, 'agent');
        }
    }


    // --- UI Rendering ---
    function displayMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.textContent = message;
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function renderCasefileList(casefiles) {
        console.log('Rendering casefiles:', casefiles);
        casefileListDiv.innerHTML = '';
        casefiles.forEach(casefile => {
            const casefileElement = document.createElement('div');
            casefileElement.classList.add('casefile-item');
            casefileElement.textContent = casefile.name;
            casefileElement.dataset.id = casefile.id;
            casefileElement.addEventListener('click', () => selectCasefile(casefile, casefileElement));
            casefileListDiv.appendChild(casefileElement);
        });
    }

    function selectCasefile(casefile, element) {
        currentCasefileId = casefile.id;
        chatHistory = []; // Reset history on new selection
        messagesDiv.innerHTML = ''; // Clear chat window
        displayMessage(`Selected casefile: "${casefile.name}". You can start chatting now.`, 'agent');

        // Update selection visuals
        document.querySelectorAll('.casefile-item').forEach(el => el.classList.remove('selected'));
        element.classList.add('selected');
    }


    // --- Event Handlers ---
    async function handleSendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        userInput.value = '';
        await sendMessageToBackend(message);
    }

    async function handleCreateCasefile(event) {
        event.preventDefault();
        const name = newCasefileNameInput.value.trim();
        const description = newCasefileDescTextarea.value.trim();
        if (name === '') return;

        newCasefileNameInput.value = '';
        newCasefileDescTextarea.value = '';

        const newCasefileId = await createCasefile(name, description);
        if (newCasefileId) {
            // Fetch the full casefile details using the ID
            const response = await fetch(`http://localhost:8000/api/v1/casefiles/${newCasefileId}`);
            const newCasefileJson = await response.text();
            console.log('Fetched new casefile (JSON string):', newCasefileJson);
            const newCasefile = JSON.parse(newCasefileJson);

            // Add the new casefile to the list without re-fetching
            const casefileElement = document.createElement('div');
            casefileElement.classList.add('casefile-item');
            casefileElement.textContent = newCasefile.name;
            casefileElement.dataset.id = newCasefile.id;
            casefileElement.addEventListener('click', () => selectCasefile(newCasefile, casefileElement));
            casefileListDiv.appendChild(casefileElement);

            // Automatically select the new casefile
            selectCasefile(newCasefile, casefileElement);
        }
    }

    // --- Initialization ---
    async function initialize() {
        sendButton.addEventListener('click', handleSendMessage);
        userInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') handleSendMessage();
        });
        newCasefileForm.addEventListener('submit', handleCreateCasefile);

        try {
            const casefiles = await fetchCasefiles();
            renderCasefileList(casefiles);
        } catch (error) {
            console.error('Error during initialization:', error);
            displayMessage('Error: Could not initialize the application.', 'agent');
        }

        displayMessage('Welcome! Please select a casefile from the left panel or create a new one to begin.', 'agent');
    }

    initialize();
});