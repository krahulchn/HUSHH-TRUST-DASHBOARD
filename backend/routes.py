from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Permission, ConnectedService, TrustScore, AuditLog, Notification
from utils import calculate_trust_score, hash_password, verify_password, log_audit
from datetime import datetime
import json

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
permissions_bp = Blueprint('permissions', __name__, url_prefix='/api/permissions')
services_bp = Blueprint('services', __name__, url_prefix='/api/services')
trust_bp = Blueprint('trust', __name__, url_prefix='/api/trust')
audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

# =====================
# Auth Routes
# =====================

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Initialize default permissions
    default_permissions = [
        {'name': 'Profile Data', 'description': 'Access to personal profile information'},
        {'name': 'Analytics', 'description': 'Access to usage analytics and behavioral data'},
        {'name': 'Location', 'description': 'Access to geographic location information'},
        {'name': 'Notifications', 'description': 'Permission to send notifications'}
    ]
    
    for perm in default_permissions:
        permission = Permission(
            user_id=user.id,
            name=perm['name'],
            description=perm['description'],
            enabled=False
        )
        db.session.add(permission)
    
    # Initialize trust score
    trust_score = TrustScore(user_id=user.id)
    db.session.add(trust_score)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    from flask_jwt_extended import create_access_token
    
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not verify_password(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

# =====================
# Dashboard Routes
# =====================

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """Get complete dashboard overview"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get trust score
    trust_score = TrustScore.query.filter_by(user_id=user_id).first()
    
    # Get permissions
    permissions = Permission.query.filter_by(user_id=user_id).all()
    
    # Get connected services
    services = ConnectedService.query.filter_by(user_id=user_id).all()
    
    # Get recent audit logs
    audit_logs = AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.created_at.desc()).limit(10).all()
    
    return jsonify({
        'user': user.to_dict(),
        'trust_score': trust_score.to_dict() if trust_score else None,
        'permissions': [p.to_dict() for p in permissions],
        'services': [s.to_dict() for s in services],
        'audit_logs': [a.to_dict() for a in audit_logs]
    }), 200

# =====================
# Permissions Routes
# =====================

@permissions_bp.route('/', methods=['GET'])
@jwt_required()
def get_permissions():
    """Get all permissions for current user"""
    user_id = get_jwt_identity()
    permissions = Permission.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'permissions': [p.to_dict() for p in permissions]
    }), 200

@permissions_bp.route('/<int:permission_id>', methods=['PUT'])
@jwt_required()
def update_permission(permission_id):
    """Update a permission"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    permission = Permission.query.filter_by(id=permission_id, user_id=user_id).first()
    
    if not permission:
        return jsonify({'error': 'Permission not found'}), 404
    
    permission.enabled = data.get('enabled', permission.enabled)
    permission.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log the action
    log_audit(user_id, f'Updated permission: {permission.name}', 'permission', permission_id, request)
    
    # Recalculate trust score
    calculate_trust_score(user_id)
    
    return jsonify({
        'message': 'Permission updated successfully',
        'permission': permission.to_dict()
    }), 200

# =====================
# Services Routes
# =====================

@services_bp.route('/', methods=['GET'])
@jwt_required()
def get_services():
    """Get all connected services"""
    user_id = get_jwt_identity()
    services = ConnectedService.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'services': [s.to_dict() for s in services]
    }), 200

@services_bp.route('/', methods=['POST'])
@jwt_required()
def add_service():
    """Add a new connected service"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Service name is required'}), 400
    
    service = ConnectedService(
        user_id=user_id,
        name=data['name'],
        icon=data.get('icon', '📱'),
        status=data.get('status', 'pending')
    )
    
    db.session.add(service)
    db.session.commit()
    
    log_audit(user_id, f'Added service: {service.name}', 'service', service.id, request)
    
    return jsonify({
        'message': 'Service added successfully',
        'service': service.to_dict()
    }), 201

@services_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    """Update a connected service"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    service = ConnectedService.query.filter_by(id=service_id, user_id=user_id).first()
    
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    service.status = data.get('status', service.status)
    service.permissions_granted = data.get('permissions_granted', service.permissions_granted)
    service.last_sync = datetime.utcnow()
    service.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_audit(user_id, f'Updated service: {service.name}', 'service', service_id, request)
    
    return jsonify({
        'message': 'Service updated successfully',
        'service': service.to_dict()
    }), 200

@services_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    """Delete a connected service"""
    user_id = get_jwt_identity()
    
    service = ConnectedService.query.filter_by(id=service_id, user_id=user_id).first()
    
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    db.session.delete(service)
    db.session.commit()
    
    log_audit(user_id, f'Deleted service: {service.name}', 'service', service_id, request)
    
    return jsonify({
        'message': 'Service deleted successfully'
    }), 200

# =====================
# Trust Score Routes
# =====================

@trust_bp.route('/', methods=['GET'])
@jwt_required()
def get_trust_score():
    """Get trust score for current user"""
    user_id = get_jwt_identity()
    trust_score = TrustScore.query.filter_by(user_id=user_id).first()
    
    if not trust_score:
        return jsonify({'error': 'Trust score not found'}), 404
    
    return jsonify(trust_score.to_dict()), 200

@trust_bp.route('/recalculate', methods=['POST'])
@jwt_required()
def recalculate_trust():
    """Recalculate trust score"""
    user_id = get_jwt_identity()
    calculate_trust_score(user_id)
    
    trust_score = TrustScore.query.filter_by(user_id=user_id).first()
    
    return jsonify({
        'message': 'Trust score recalculated',
        'trust_score': trust_score.to_dict()
    }), 200

# =====================
# Audit Logs Routes
# =====================

@audit_bp.route('/', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Get audit logs for current user"""
    user_id = get_jwt_identity()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    logs = AuditLog.query.filter_by(user_id=user_id).order_by(
        AuditLog.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    }), 200

@audit_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_audit_log(log_id):
    """Get specific audit log"""
    user_id = get_jwt_identity()
    log = AuditLog.query.filter_by(id=log_id, user_id=user_id).first()
    
    if not log:
        return jsonify({'error': 'Audit log not found'}), 404
    
    return jsonify(log.to_dict()), 200

# =====================
# Notification Routes
# =====================

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get all notifications for current user"""
    user_id = get_jwt_identity()
    
    # Get query parameters
    unread_only = request.args.get('unread_only', False, type=lambda x: x.lower() == 'true')
    category = request.args.get('category', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Notification.query.filter_by(user_id=user_id)
    
    if unread_only:
        query = query.filter_by(read=False)
    
    if category:
        query = query.filter_by(category=category)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications.items],
        'unread_count': Notification.query.filter_by(user_id=user_id, read=False).count(),
        'total': notifications.total,
        'pages': notifications.pages,
        'current_page': page
    }), 200

@notifications_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    """Get specific notification"""
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    return jsonify(notification.to_dict()), 200

@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark notification as read"""
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.read = True
    notification.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_audit(user_id, f'Marked notification as read: {notification.title}', 'notification', notification_id, request)
    
    return jsonify({
        'message': 'Notification marked as read',
        'notification': notification.to_dict()
    }), 200

@notifications_bp.route('/mark-all-as-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read"""
    user_id = get_jwt_identity()
    
    unread_notifications = Notification.query.filter_by(user_id=user_id, read=False).all()
    
    for notification in unread_notifications:
        notification.read = True
        notification.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_audit(user_id, f'Marked all notifications as read', 'notification', None, request)
    
    return jsonify({
        'message': f'Marked {len(unread_notifications)} notifications as read',
        'count': len(unread_notifications)
    }), 200

@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification"""
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    db.session.delete(notification)
    db.session.commit()
    
    log_audit(user_id, f'Deleted notification: {notification.title}', 'notification', notification_id, request)
    
    return jsonify({
        'message': 'Notification deleted successfully'
    }), 200

@notifications_bp.route('/clear-all', methods=['DELETE'])
@jwt_required()
def clear_all_notifications():
    """Delete all notifications for user"""
    user_id = get_jwt_identity()
    
    notifications = Notification.query.filter_by(user_id=user_id).all()
    count = len(notifications)
    
    for notification in notifications:
        db.session.delete(notification)
    
    db.session.commit()
    
    log_audit(user_id, f'Cleared all notifications ({count} total)', 'notification', None, request)
    
    return jsonify({
        'message': f'Cleared {count} notifications',
        'count': count
    }), 200

@notifications_bp.route('/', methods=['POST'])
@jwt_required()
def create_notification():
    """Create a new notification (admin/internal use)"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('message'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    notification = Notification(
        user_id=user_id,
        type=data.get('type', 'info'),
        title=data['title'],
        message=data['message'],
        icon=data.get('icon', 'ℹ️'),
        category=data.get('category', 'info'),
        action_url=data.get('action_url'),
        notification_metadata=data.get('metadata')
    )
    
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'message': 'Notification created successfully',
        'notification': notification.to_dict()
    }), 201