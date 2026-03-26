from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('Permission', backref='user', lazy=True, cascade='all, delete-orphan')
    services = db.relationship('ConnectedService', backref='user', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Permission(db.Model):
    """Permission model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ConnectedService(db.Model):
    """Connected Service model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    icon = db.Column(db.String(10))
    status = db.Column(db.String(20), default='pending')  # active, pending, inactive
    permissions_granted = db.Column(db.Integer, default=0)
    last_sync = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'status': self.status,
            'permissions_granted': self.permissions_granted,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class TrustScore(db.Model):
    """Trust Score model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    overall_score = db.Column(db.Integer, default=50)
    permissions_score = db.Column(db.Integer, default=50)
    service_status_score = db.Column(db.Integer, default=50)
    data_security_score = db.Column(db.Integer, default=50)
    safety_score = db.Column(db.Integer, default=85)
    auditability_score = db.Column(db.Integer, default=80)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'overall_score': self.overall_score,
            'permissions_score': self.permissions_score,
            'service_status_score': self.service_status_score,
            'data_security_score': self.data_security_score,
            'safety_score': self.safety_score,
            'auditability_score': self.auditability_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AuditLog(db.Model):
    """Audit Log model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(80))
    resource_id = db.Column(db.Integer)
    status = db.Column(db.String(20), default='success')  # success, failed
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    log_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'status': self.status,
            'ip_address': self.ip_address,
            'metadata': self.log_metadata,
            'created_at': self.created_at.isoformat()
        }

class Notification(db.Model):
    """Notification model for personalized user notifications"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # permission_granted, permission_revoked, trust_score_changed, service_status_changed, alert
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(50), default='ℹ️')  # emoji or icon identifier
    category = db.Column(db.String(50), default='info')  # info, warning, success, error
    read = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(255))  # URL to take action or view more details
    notification_metadata = db.Column(db.JSON)  # Additional context data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'icon': self.icon,
            'category': self.category,
            'read': self.read,
            'action_url': self.action_url,
            'metadata': self.notification_metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
