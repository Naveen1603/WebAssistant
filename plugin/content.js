// Utility function to generate a random UUID
// Function to request interactionId from the background script
// Call the function at the start to initialize interactionId
let interactionId = null;

function requestInteractionId() {
    chrome.runtime.sendMessage({ action: "getInteractionId" }, function(response) {
        if (response && response.interactionId) {
            console.log("Retrieved interactionId:", response.interactionId);
            interactionId=response.interactionId;
        } else {
            console.error("Failed to retrieve interactionId");
        }
    });
}

// Call the function at the start to initialize interactionId
requestInteractionId();

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

function getNearestText(element) {
    const parentText = element.closest('*')?.textContent.trim();
    const siblingText = Array.from(element.parentElement?.children || [])
        .filter(sibling => sibling !== element)
        .map(sibling => sibling.textContent.trim())
        .filter(text => text.length)
        .join(' ');
    return (parentText || '') + ' ' + (siblingText || '').trim();
}

// Helper function to capture XPath of an element
function getXPath(element) {
    let xpath = '';
    while (element && element.nodeType === Node.ELEMENT_NODE) {
        let index = 1;
        let sibling = element.previousSibling;

        // Count previous siblings of the same tag name
        while (sibling) {
            if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName === element.nodeName) {
                index++;
            }
            sibling = sibling.previousSibling;
        }

        const tagName = element.nodeName.toLowerCase();
        xpath = `/${tagName}[${index}]` + xpath;
        element = element.parentNode;
    }
    return xpath;
}


// Helper function to send or update an interaction in the buffer
function aggregateInteraction(eventType, element, extraData = {}) {
    const interactionKey = `${eventType}_${element.id || element.className || element.tagName}`;
    const currentTime = Date.now();

    // Create a new interaction record in the buffer
    if (interactionBuffer[interactionKey]) {
        const interaction = interactionBuffer[interactionKey];

        // Update interaction with the latest data (e.g., append input value)
        if (eventType === "input") {
            interaction.data = extraData.value;
        }
        interaction.timestamp = currentTime;  // Update timestamp
    }else{
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
            nearestText: getNearestText(element),
            timestamp: currentTime,
            description: createDescription(eventType, element) // Custom description for the interaction
        };
    }
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
