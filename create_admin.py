from app import app, db
from models import User

def create_admin():
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@psra.com').first()
        if admin:
            print("Admin user already exists!")
            return

        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@psra.com',
            batch_number=1,
            phone_number='+1234567890',
            whatsapp_number='+1234567890',
            is_admin=True
        )
        admin.set_password('admin123')

        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("Email: admin@psra.com")
        print("Password: admin123")

if __name__ == '__main__':
    create_admin()
