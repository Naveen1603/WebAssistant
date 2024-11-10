from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime

from flask_cors import cross_origin

from app.InteractionService import InteractionService

# Define a Blueprint for the interaction routes
interaction_blueprint = Blueprint('interaction', __name__)
service = InteractionService()
# Path to store interactions data
DATA_FILE = 'interactions_log.json'

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)  # Initialize as an empty list


def save_interaction(data):
    """
    Save the interaction data to a JSON file.
    """
    # Load existing data
    with open(DATA_FILE, 'r') as f:
        interactions = json.load(f)

    # Append new interaction
    interactions.append(data)

    # Write updated data back to the file
    with open(DATA_FILE, 'w') as f:
        json.dump(interactions, f, indent=4)


@interaction_blueprint.route('/track-interaction', methods=['POST'])
# @cross_origin()
def track_interaction():
    """
    Endpoint to track user interactions from the Chrome extension.
    """
    try:
        interactions = request.json.get('interactions', [])
        response_status = service.store_interaction(interactions)
        # Get JSON data from request
        # interaction_data = request.get_json()
        #
        # if not interaction_data:
        #     return jsonify({"error": "No data provided"}), 400
        #
        # # Add server timestamp for reference
        # interaction_data['received_at'] = datetime.utcnow().isoformat()
        #
        # # Save interaction
        print("Received interaction:", interactions)
        # save_interaction(interaction_data)
        #
        return jsonify({"status": "success", "message": "Interaction recorded"}), 200
    except Exception as e:
        print("Exception occured while saving interaction", e)

    return jsonify({"status": "success", "message": "Interaction record failed"}), 400
