// Utility function to generate a random UUID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Buffer to hold current interaction data
let interactionBuffer = {};

// Helper function to create a readable description for the interaction
function createDescription(eventType, element) {
    const elementId = element.id ? `with ID: ${element.id}` : '';
    const elementClass = element.className ? ` and class: ${element.className}` : '';
    const elementTag = ` (${element.tagName})`;

    let description = `User performed a ${eventType}`;
    if (eventType === "input") {
        description += ` by entering the value "${element.value}"`;
    } else if (eventType === "click") {
        description += ` on the element${elementId}${elementClass}${elementTag}`;
    } else if (eventType === "scroll") {
        description += ` by scrolling to position ${window.scrollY}`;
    }

    return description;
}

// Helper function to capture XPath of an element
function getXPath(element) {
    let path = '';
    while (element) {
        let name = element.localName;
        if (!element.id) {
            let siblings = Array.from(element.parentNode.children);
            let index = siblings.indexOf(element) + 1;
            path = `${name}[${index}]` + (path ? '/' + path : '');
        } else {
            path = `${name}[@id='${element.id}']` + (path ? '/' + path : '');
            break;
        }
        element = element.parentNode;
    }
    return path;
}

// Helper function to send or update an interaction in the buffer
function aggregateInteraction(eventType, element, extraData = {}) {
    const interactionId = generateUUID();
    const interactionKey = `${eventType}_${element.id || element.className || element.tagName}`;
    const currentTime = Date.now();

    // Create a new interaction record in the buffer
    interactionBuffer[interactionKey] = {
        interactionId,
        eventType,
        elementId: element.id,
        elementClass: element.className,
        selector: `${element.tagName}${element.id ? `#${element.id}` : ''}${element.className ? `.${element.className}` : ''}`,
        xpath: getXPath(element),
        pageURL: window.location.href,
        scrollPosition: window.scrollY,
        data: eventType === "input" ? extraData.value : '', // Store latest value only
        timestamp: currentTime,
        description: createDescription(eventType, element) // Custom description for the interaction
    };
}

// Function to send the final aggregated data for all interactions
function sendAggregatedInteractions() {
    for (let key in interactionBuffer) {
        const interaction = interactionBuffer[key];

        // Send the final interaction data to the background script
        chrome.runtime.sendMessage({
            action: 'capture_interaction',
            data: {
                interactionId: interaction.interactionId, // Unique interaction ID
                eventType: interaction.eventType,
                elementId: interaction.elementId,
                elementClass: interaction.elementClass,
                selector: interaction.selector,
                xpath: interaction.xpath,
                pageURL: interaction.pageURL,
                scrollPosition: interaction.scrollPosition,
                data: interaction.data, // Only the latest value
                timestamp: interaction.timestamp,
                description: interaction.description // Custom description for LLM
            }
        });
    }
    // Clear the buffer after sending
    interactionBuffer = {};
}

// Event listeners

// Capture input events, aggregating values in the buffer
document.addEventListener("input", (event) => {
    if (event.target.tagName === "INPUT" || event.target.tagName === "TEXTAREA") {
        aggregateInteraction("input", event.target, { value: event.target.value });
    }
});

// Finalize input data on change events
document.addEventListener("change", (event) => {
    if (event.target.tagName === "INPUT" || event.target.tagName === "TEXTAREA") {
        aggregateInteraction("input", event.target, { value: event.target.value });
        sendAggregatedInteractions(); // Send data when input changes are finalized
    }
});

// Capture clicks and aggregate them in the buffer
document.addEventListener("click", (event) => {
    aggregateInteraction("click", event.target);
    sendAggregatedInteractions(); // Send data on each click
});

// Capture scroll events with a threshold
let lastScrollY = 0;
window.addEventListener("scroll", () => {
    const currentScrollY = window.scrollY;
    if (Math.abs(currentScrollY - lastScrollY) > 100) { // Only send if significant scroll change
        lastScrollY = currentScrollY;
        aggregateInteraction("scroll", document.body, { scrollPosition: currentScrollY });
    }
});

// Capture page load and unload events
window.addEventListener("load", () => {
    aggregateInteraction("load", document.body);
    sendAggregatedInteractions(); // Send data on page load
});

window.addEventListener("beforeunload", () => {
    aggregateInteraction("unload", document.body);
    sendAggregatedInteractions(); // Send data on page unload
});
