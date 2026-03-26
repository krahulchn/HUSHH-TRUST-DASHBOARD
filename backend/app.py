import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db
from routes import auth_bp, dashboard_bp, permissions_bp, services_bp, trust_bp, audit_bp, notifications_bp

def create_app(config_name=None):
    """Application factory"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(permissions_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(trust_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(notifications_bp)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'message': 'Trust Dashboard Backend is running'}), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'name': 'Hushh Trust Dashboard API',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login'
                },
                'dashboard': {
                    'overview': 'GET /api/dashboard/overview'
                },
                'permissions': {
                    'get_all': 'GET /api/permissions/',
                    'update': 'PUT /api/permissions/<id>'
                },
                'services': {
                    'get_all': 'GET /api/services/',
                    'add': 'POST /api/services/',
                    'update': 'PUT /api/services/<id>',
                    'delete': 'DELETE /api/services/<id>'
                },
                'trust': {
                    'get_score': 'GET /api/trust/',
                    'recalculate': 'POST /api/trust/recalculate'
                },
                'audit': {
                    'get_logs': 'GET /api/audit/',
                    'get_log': 'GET /api/audit/<id>'
                }
            }
        }), 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
