from werkzeug.security import generate_password_hash, check_password_hash
from models import db, TrustScore, Permission, ConnectedService, AuditLog
from datetime import datetime
from flask import request

def hash_password(password):
    """Hash a password using werkzeug"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password_hash, password):
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)

def calculate_trust_score(user_id):
    """
    Calculate the trust score for a user based on:
    - Permissions enabled
    - Service status
    - Data security
    """
    trust_score = TrustScore.query.filter_by(user_id=user_id).first()
    
    if not trust_score:
        return None
    
    # Get permissions
    permissions = Permission.query.filter_by(user_id=user_id).all()
    enabled_permissions = [p for p in permissions if p.enabled]
    permissions_score = int((len(enabled_permissions) / len(permissions)) * 100) if permissions else 0
    
    # Get services
    services = ConnectedService.query.filter_by(user_id=user_id).all()
    active_services = [s for s in services if s.status == 'active']
    service_status_score = int((len(active_services) / len(services)) * 100) if services else 0
    
    # Data security score (simulated - always high)
    data_security_score = 88
    
    # Calculate overall score
    overall_score = int((permissions_score + service_status_score + data_security_score) / 3)
    
    # Update trust score
    trust_score.permissions_score = permissions_score
    trust_score.service_status_score = service_status_score
    trust_score.data_security_score = data_security_score
    trust_score.overall_score = overall_score
    trust_score.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return trust_score

def log_audit(user_id, action, resource_type=None, resource_id=None, req=None, status='success'):
    """
    Log an audit event
    """
    ip_address = None
    user_agent = None
    
    if req:
        ip_address = req.remote_addr or req.headers.get('X-Forwarded-For', 'unknown')
        user_agent = req.headers.get('User-Agent', 'unknown')
    
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata={}
    )
    
    db.session.add(log)
    db.session.commit()
    
    return log

def get_user_stats(user_id):
    """
    Get statistics for a user
    """
    permissions = Permission.query.filter_by(user_id=user_id).all()
    services = ConnectedService.query.filter_by(user_id=user_id).all()
    audit_logs = AuditLog.query.filter_by(user_id=user_id).all()
    trust_score = TrustScore.query.filter_by(user_id=user_id).first()
    
    return {
        'total_permissions': len(permissions),
        'enabled_permissions': len([p for p in permissions if p.enabled]),
        'total_services': len(services),
        'active_services': len([s for s in services if s.status == 'active']),
        'total_audit_logs': len(audit_logs),
        'trust_score': trust_score.overall_score if trust_score else 0,
        'safety_score': trust_score.safety_score if trust_score else 0,
        'auditability_score': trust_score.auditability_score if trust_score else 0
    }
