from flask import Flask
from dotenv import load_dotenv
import os
from .extensions import db, migrate
from .routes.auth import auth_bp
from flask_jwt_extended import JWTManager
from .routes.category import category_bp
from .routes.product import product_bp
from .routes.inventory import inventory_bp
from datetime import timedelta
from app.routes.dashboard import dashboard_bp
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
    jwt = JWTManager(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/"
        f"{os.getenv('DB_NAME')}"
    )

    db.init_app(app)
    migrate.init_app(app, db)
    from .models import Category,Product,User,InventoryTransaction


    @app.route("/home")
    def home():
        return "It is a home page"
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(dashboard_bp)
    return app