from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///video_player.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Create folders if they don't exist
    os.makedirs(os.path.join(app.root_path, 'static', 'videos'), exist_ok=True)

    with app.app_context():
        # Import models after creating app context
        from app.models import Shop, ButtonPress

        # Create database tables
        db.create_all()

        # Create admin user if not exists
        if not Shop.query.filter_by(shop_name='admin').first():
            admin = Shop(
                shop_name='admin',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    # Register blueprints
    from app.routes import auth, main, admin
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin)

    return app