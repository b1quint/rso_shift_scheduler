# Architecture Overview

## System Design

### Backend (Django)

The backend follows Django's MVT (Model-View-Template) pattern, adapted for API development:

- **Models**: Define data structure (Staff, Shift, Schedule, etc.)
- **Views**: API endpoints using Django REST Framework
- **Serializers**: Convert between Python objects and JSON

#### App Structure

1. **users**: Authentication and user management
2. **staff**: Staff profiles, roles, and availability
3. **shifts**: Individual shift definitions
4. **observatory**: Observatory-specific data (telescopes, instruments)

### Frontend (React)

Feature-based architecture for better organization:

- **features/**: Each major feature in its own folder
- **components/**: Shared/reusable components
- **services/**: API communication layer
- **hooks/**: Custom React hooks for shared logic

### Communication

- REST API between frontend and backend
- JWT tokens for authentication
- CORS configured for development

### Database Schema (Planned)

```
User
├── Staff (extends User)
│   ├── role
│   ├── availability
│   └── preferences
│
Shift
├── assigned_staff (FK to Staff)
├── start_time
├── end_time
├── shift_type
└── observatory_resource

Schedule
├── date_range
└── shifts (M2M)
```

## Development Workflow

1. Backend changes: Models → Migrations → Views → URLs
2. Frontend changes: Components → Services → Integration
3. Testing at each layer
