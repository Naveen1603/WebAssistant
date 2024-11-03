from flask import Flask
from flask_cors import CORS

from app.controllor.health_controllor import health_blueprint
from app.controllor.interaction_controllor import interaction_blueprint

app = Flask(__name__)
CORS(app)


app.register_blueprint(interaction_blueprint, url_prefix="/api")
app.register_blueprint(health_blueprint, url_prefix='/api')

# app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
