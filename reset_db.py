from app import create_app, db
from app.models import Shop, ButtonPress


def reset_database():
    app = create_app()

    with app.app_context():
        # Drop all existing tables
        db.drop_all()

        # Create all tables
        db.create_all()

        # Create admin user
        admin = Shop(shop_name='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)

        # Create test shop
        test_shop = Shop(shop_name='test_shop', is_admin=False)
        test_shop.set_password('test123')
        db.session.add(test_shop)

        try:
            db.session.commit()
            print("Database initialized successfully!")
            print("\nDefault credentials:")
            print("Admin - username: admin, password: admin123")
            print("Test Shop - username: test_shop, password: test123")
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()


if __name__ == "__main__":
    reset_database()