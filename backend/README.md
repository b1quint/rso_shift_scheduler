# Backend - Django REST API

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Database Setup

For development, SQLite is fine. For production, use PostgreSQL:

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## Project Structure

```
backend/
├── config/           # Django project settings
├── apps/
│   ├── users/       # User authentication & management
│   ├── shifts/      # Shift scheduling logic
│   ├── staff/       # Staff profiles & availability
│   └── observatory/ # Observatory-specific data
└── manage.py
```

## API Endpoints (To be implemented)

- `/api/auth/` - Authentication endpoints
- `/api/staff/` - Staff management
- `/api/shifts/` - Shift operations
- `/api/schedules/` - Schedule management
