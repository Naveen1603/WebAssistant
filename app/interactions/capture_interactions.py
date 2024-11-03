import json
from playwright.sync_api import sync_playwright
import uuid
import ollama

# Initialize interaction store
interaction_store = {}


def generate_interaction_id():
    return str(uuid.uuid4())


def capture_interaction(element, user_action):
    """
    Capture and store interaction data with element properties and action.

    Args:
        element (dict): Metadata of the UI element (tag name, id, text, classes, etc.)
        user_action (str): The action user performed on the element

    Returns:
        interaction_id (str): ID of the stored interaction
    """
    element_description = " ".join([f"{key}: {value}" for key, value in element.items()])

    # Generate embedding with Ollama
    embedding_response = ollama.embed(element_description)
    element_embedding = embedding_response.get("embedding")

    # Generate unique ID and store interaction
    interaction_id = generate_interaction_id()
    interaction_store[interaction_id] = {
        "element": element,
        "user_action": user_action,
        "embedding": element_embedding
    }
    print(f"Captured interaction: {interaction_id}")
    return interaction_id


def get_element_properties(element_handle):
    """
    Extract properties of a Playwright element handle.

    Args:
        element_handle (ElementHandle): Playwright element handle to extract properties from

    Returns:
        element_properties (dict): Properties of the element
    """
    element_properties = {
        "tag": element_handle.evaluate("el => el.tagName"),
        "id": element_handle.evaluate("el => el.id"),
        "text": element_handle.evaluate("el => el.innerText"),
        "class": element_handle.evaluate("el => el.className")
    }
    return element_properties

if __name__ == '__main__':
    # Start Playwright and capture interactions
    with sync_playwright() as p:
        # Launch Chrome browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to a page
        page.goto("https://amazon.com")  # Replace with target URL


        # Capture 'click' and 'type' events
        def on_click(event):
            element = get_element_properties(event.target)
            capture_interaction(element, "click")


        def on_type(event):
            element = get_element_properties(event.target)
            capture_interaction(element, "type text")


        # Attach listeners to events
        page.on("click", on_click)
        page.on("input", on_type)  # For typing events

        print("Tracking interactions...")

        # Keep the script running to capture interactions
        page.wait_for_timeout(30000)  # Adjust timeout as needed

        # Close browser after capture
        browser.close()

    # Save interactions to a file
    with open("captured_interactions.json", "w") as file:
        json.dump(interaction_store, file, indent=4)
