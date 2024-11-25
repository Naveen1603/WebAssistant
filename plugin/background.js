console.log("Background script loaded");

chrome.runtime.onInstalled.addListener(() => {
    console.log("Extension installed");
});

const API_URL = "http://127.0.0.1:5000/api/track-interaction";
const BATCH_INTERVAL_MS = 10000; // Send data every 10 seconds
const MAX_BATCH_SIZE = 20;        // Maximum number of events to batch

let interactionBuffer = [];        // Buffer to hold interactions
let timer;                         // Timer to send data periodically
const interactionId = crypto.randomUUID();

// Function to add interaction data to the buffer
function addInteractionToBuffer(data) {
    interactionBuffer.push(data);

    // Send the batch if the buffer reaches the maximum size
    if (interactionBuffer.length >= MAX_BATCH_SIZE) {
        sendInteractions();
    }
}

// Function to send interactions to the backend
function sendInteractions() {
    if (interactionBuffer.length === 0) return; // Nothing to send

    // Send data to backend API
    fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ interactions: interactionBuffer })
    })
    .then(response => response.json())
    .then(data => console.log("Interactions sent successfully:", data))
    .catch(error => console.error("Error sending interactions:", error));

    // Clear the buffer after sending
    interactionBuffer = [];
}

// Listener for interactions from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'capture_interaction') {
        const interactionData = {
            interactionId: message.data.interactionId || null,  // Unique ID for the interaction
            eventType: message.data.eventType,
            elementText: message.data.elementText || null,
            pageURL: sender.tab.url || null,
            data: message.data.data || null,
            scrollPosition: message.data.scrollPosition || null,
            timestamp: new Date().toISOString(),
            selector: message.data.selector || null,  // CSS selector
            xpath: message.data.xpath || null,        // XPath
            description: message.data.description || null, // Custom description,
            nearestText: message.data.nearestText || null
        };

        addInteractionToBuffer(interactionData);
        sendResponse({ status: "received" });
    }else if (message.action === "getInteractionId") {
        // Retrieve or generate a new interactionId
        sendResponse({ interactionId: interactionId });

        // Required to indicate async response
        return true;
    }
});

// Start the periodic sending of interactions
timer = setInterval(sendInteractions, BATCH_INTERVAL_MS);

// Clean up timer when the extension is disabled
chrome.runtime.onSuspend.addListener(() => {
    clearInterval(timer);
    sendInteractions(); // Send any remaining interactions
});
