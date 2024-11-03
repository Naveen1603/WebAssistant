from flask import Blueprint, jsonify

health_blueprint = Blueprint('health', __name__)

@health_blueprint.get('/health')
def health():
    return jsonify({"status": "success", "message": "Application was UP!!"}), 200

