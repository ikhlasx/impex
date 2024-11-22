from app import create_app, db
from app.models import Shop, ButtonPress


def init_database():
    app = create_app()
    with app.app_context():
        # Drop all existing tables
        db.drop_all()

        # Create all tables
        db.create_all()

        # Create admin user
        admin = Shop(
            shop_name='admin',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # Create a test shop
        test_shop = Shop(
            shop_name='test_shop',
            is_admin=False
        )
        test_shop.set_password('test123')
        db.session.add(test_shop)

        # Commit changes
        db.session.commit()

        print("Database initialized successfully!")
        print("Admin credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("\nTest shop credentials:")
        print("Username: test_shop")
        print("Password: test123")


if __name__ == '__main__':
    init_database()