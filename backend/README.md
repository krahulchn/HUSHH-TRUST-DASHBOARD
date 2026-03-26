# Trust Dashboard Backend

A Flask-based backend API for the Trust Dashboard application. This backend provides secure authentication, data management, and audit logging for a comprehensive data relationship management system.

## Features

- **User Authentication** - Register and login with JWT tokens
- **Permission Management** - Control data access permissions
- **Service Integration** - Connect and manage third-party services
- **Trust Score Calculation** - Automatic calculation of trust metrics
- **Audit Logging** - Complete audit trail of all actions
- **RESTful API** - Clean, well-documented API endpoints
- **CORS Support** - Easy frontend integration
- **Database** - SQLAlchemy ORM with SQLite support

## Project Structure

```
backend/
├── app.py              # Flask application factory
├── config.py           # Configuration settings
├── models.py           # Database models
├── routes.py           # API routes and endpoints
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create .env file:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your secret keys:
   ```
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```

## Running the Server

Start the Flask development server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication (`/api/auth`)

#### Register User
- **POST** `/api/auth/register`
- Body: `{ "username": "user", "email": "user@example.com", "password": "pass" }`
- Response: User details and message

#### Login
- **POST** `/api/auth/login`
- Body: `{ "username": "user", "password": "pass" }`
- Response: JWT access token and user details

### Dashboard (`/api/dashboard`)

#### Get Overview
- **GET** `/api/dashboard/overview`
- Headers: `Authorization: Bearer <token>`
- Response: Complete dashboard data including scores, permissions, services, and audit logs

### Permissions (`/api/permissions`)

#### Get All Permissions
- **GET** `/api/permissions/`
- Headers: `Authorization: Bearer <token>`
- Response: Array of permission objects

#### Update Permission
- **PUT** `/api/permissions/<id>`
- Headers: `Authorization: Bearer <token>`
- Body: `{ "enabled": true }`
- Response: Updated permission object

### Services (`/api/services`)

#### Get All Services
- **GET** `/api/services/`
- Headers: `Authorization: Bearer <token>`
- Response: Array of service objects

#### Add Service
- **POST** `/api/services/`
- Headers: `Authorization: Bearer <token>`
- Body: `{ "name": "Service Name", "icon": "💼", "status": "pending" }`
- Response: Created service object

#### Update Service
- **PUT** `/api/services/<id>`
- Headers: `Authorization: Bearer <token>`
- Body: `{ "status": "active", "permissions_granted": 3 }`
- Response: Updated service object

#### Delete Service
- **DELETE** `/api/services/<id>`
- Headers: `Authorization: Bearer <token>`
- Response: Success message

### Trust Score (`/api/trust`)

#### Get Trust Score
- **GET** `/api/trust/`
- Headers: `Authorization: Bearer <token>`
- Response: Trust score object with all metrics

#### Recalculate Trust Score
- **POST** `/api/trust/recalculate`
- Headers: `Authorization: Bearer <token>`
- Response: Recalculated trust score object

### Audit Logs (`/api/audit`)

#### Get Audit Logs
- **GET** `/api/audit/`
- Headers: `Authorization: Bearer <token>`
- Query Parameters: `page` (default: 1), `per_page` (default: 20)
- Response: Paginated audit log objects

#### Get Specific Audit Log
- **GET** `/api/audit/<id>`
- Headers: `Authorization: Bearer <token>`
- Response: Specific audit log object

## Database Models

### User
- id, username, email, password_hash
- created_at, updated_at
- Relationships: permissions, services, audit_logs

### Permission
- id, user_id, name, description, enabled
- created_at, updated_at

### ConnectedService
- id, user_id, name, icon, status
- permissions_granted, last_sync
- created_at, updated_at

### TrustScore
- id, user_id, overall_score
- permissions_score, service_status_score, data_security_score
- safety_score, auditability_score
- created_at, updated_at

### AuditLog
- id, user_id, action, resource_type, resource_id
- status, ip_address, user_agent, metadata
- created_at

## Development

### Running with Different Config

```bash
# Development (default)
flask run

# Production
FLASK_ENV=production python app.py

# Testing
FLASK_ENV=testing pytest
```

### Database Reset

To reset the database and start fresh:
```python
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
```

## Security Considerations

- Change `SECRET_KEY` and `JWT_SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting
- Add input validation and sanitization
- Use strong password hashing (already implemented with werkzeug)
- Regularly audit and rotate tokens

## Error Handling

The API returns standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error

## Testing

Example test requests using curl:

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123"}'

# Get Dashboard (replace TOKEN with actual JWT)
curl -X GET http://localhost:5000/api/dashboard/overview \
  -H "Authorization: Bearer TOKEN"
```

## Dependencies

- Flask: Web framework
- Flask-SQLAlchemy: ORM
- Flask-CORS: Cross-origin support
- Flask-JWT-Extended: JWT authentication
- python-dotenv: Environment variables
- Werkzeug: Utilities for WSGI

See `requirements.txt` for specific versions.

## License

Proprietary - Hushh Trust Dashboard
