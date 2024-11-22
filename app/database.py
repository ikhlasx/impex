from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def init_db(app):
    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        from app.models import Shop
        if not Shop.query.filter_by(shop_name='admin').first():
            admin = Shop(
                shop_name='admin',
                password=generate_password_hash('admin123')  # Change this password
            )
            db.session.add(admin)
            db.session.commit()
