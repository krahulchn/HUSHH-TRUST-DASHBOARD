"""
Database initialization script
Run this script to set up the database with sample data
"""

from app import create_app
from models import db, User, Permission, ConnectedService, TrustScore
from utils import hash_password
from datetime import datetime

def init_db():
    """Initialize database with sample data"""
    
    app = create_app()
    
    with app.app_context():
        # Drop existing tables
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create new tables
        print("Creating tables...")
        db.create_all()
        
        # Create sample user
        print("Creating sample user...")
        user = User(
            username='demo',
            email='demo@hushh.com',
            password_hash=hash_password('demo123')
        )
        db.session.add(user)
        db.session.commit()
        
        # Create default permissions
        print("Creating permissions...")
        permissions_data = [
            {
                'name': 'Profile Data',
                'description': 'Access to personal profile information',
                'enabled': True
            },
            {
                'name': 'Analytics',
                'description': 'Access to usage analytics and behavioral data',
                'enabled': True
            },
            {
                'name': 'Location',
                'description': 'Access to geographic location information',
                'enabled': False
            },
            {
                'name': 'Notifications',
                'description': 'Permission to send notifications',
                'enabled': True
            }
        ]
        
        for perm_data in permissions_data:
            permission = Permission(
                user_id=user.id,
                name=perm_data['name'],
                description=perm_data['description'],
                enabled=perm_data['enabled']
            )
            db.session.add(permission)
        
        db.session.commit()
        
        # Create connected services
        print("Creating connected services...")
        services_data = [
            {
                'name': 'CRM',
                'icon': '💼',
                'status': 'active',
                'permissions_granted': 3
            },
            {
                'name': 'Email',
                'icon': '✉️',
                'status': 'pending',
                'permissions_granted': 0
            },
            {
                'name': 'Billing',
                'icon': '💳',
                'status': 'active',
                'permissions_granted': 2
            }
        ]
        
        for service_data in services_data:
            service = ConnectedService(
                user_id=user.id,
                name=service_data['name'],
                icon=service_data['icon'],
                status=service_data['status'],
                permissions_granted=service_data['permissions_granted'],
                last_sync=datetime.utcnow()
            )
            db.session.add(service)
        
        db.session.commit()
        
        # Create trust score
        print("Creating trust score...")
        trust_score = TrustScore(
            user_id=user.id,
            overall_score=78,
            permissions_score=75,
            service_status_score=66,
            data_security_score=88,
            safety_score=92,
            auditability_score=85
        )
        db.session.add(trust_score)
        db.session.commit()
        
        print("\n✅ Database initialized successfully!")
        print("\nSample User Credentials:")
        print(f"  Username: demo")
        print(f"  Email: demo@hushh.com")
        print(f"  Password: demo123")
        print("\nDatabase location: trustdb.db")
        print("Ready to start the Flask server!")

if __name__ == '__main__':
    init_db()
