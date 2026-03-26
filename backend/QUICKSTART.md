# Quick Start Guide

## Backend Setup (Flask)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```
Edit `.env` with your secret keys (for development, defaults are fine)

### Step 3: Initialize Database
```bash
python init_db.py
```
This creates the database with sample data:
- User: `demo` / Password: `demo123`
- 4 default permissions (3 enabled, 1 disabled)
- 3 connected services (CRM, Email, Billing)
- Default trust scores

### Step 4: Run the Backend Server
```bash
python app.py
```
The API will be available at `http://localhost:5000`

## Frontend Setup

The frontend files are in the parent directory:
- `index.html` - Main HTML file
- `style.css` - Styling
- `script.js` - Interactive features

Simply open `index.html` in a browser to view the dashboard.

## API Integration Example

To connect the frontend to the backend, you can add this to `script.js`:

```javascript
// Example: Get dashboard data from backend
const getBackendRequest = document.getElementById('getBackendRequest');

getBackendRequest?.addEventListener('click', async function() {
    try {
        const response = await fetch('http://localhost:5000/api/health');
        const data = await response.json();
        console.log('Backend Status:', data);
    } catch (error) {
        console.error('Error connecting to backend:', error);
    }
});
```

## Testing the API

Use curl or Postman to test endpoints:

```bash
# Check API health
curl http://localhost:5000/api/health

# Register new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

## Project Structure

```
project/
├── frontend files:
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── backend/
    ├── app.py              # Flask app
    ├── config.py           # Config
    ├── models.py           # Database models
    ├── routes.py           # API endpoints
    ├── utils.py            # Utilities
    ├── init_db.py          # DB initialization
    ├── requirements.txt    # Dependencies
    ├── .env.example        # Environment template
    └── README.md           # Full documentation
```

## Troubleshooting

**Port 5000 already in use:**
```bash
# Use different port
python app.py # then edit app.py port parameter
```

**Database errors:**
```bash
# Reset database
python init_db.py
```

**CORS errors when connecting frontend:**
- Make sure Flask is running on `http://localhost:5000`
- CORS is enabled for all origins in development

## Next Steps

1. Connect the frontend dashboard to backend API
2. Add form validation and error handling
3. Implement real-time updates with WebSockets
4. Deploy to production with proper security
5. Add more test cases and documentation
