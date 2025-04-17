from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from database import db, migrate
from auth import auth_bp
from routes import routes_bp
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
jwt = JWTManager(app)
CORS(app)  # Allows frontend requests

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(routes_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
