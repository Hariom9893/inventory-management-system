from flask import Flask
from dotenv import load_dotenv
import os
from .extensions import db
from .routes.auth import auth_bp
from flask_jwt_extended import JWTManager
from .routes.category import category_bp
from .routes.product import product_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    jwt = JWTManager(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/"
        f"{os.getenv('DB_NAME')}"
    )

    db.init_app(app)

    from .models import Category,Product,User,InventoryTransaction

    with app.app_context():
        db.create_all()

    @app.route("/home")
    def home():
        return "It is a home page"
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    return app