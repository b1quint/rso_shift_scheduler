# API Endpoints Documentation

## Base URL
`http://localhost:8000/api/`

## Available Endpoints

### 🧑‍💼 Staff Management

#### Staff Members
- **List all staff**: `GET /api/staff/members/`
- **Get one staff**: `GET /api/staff/members/{id}/`
- **Create staff**: `POST /api/staff/members/`
- **Update staff**: `PUT /api/staff/members/{id}/`
- **Partial update**: `PATCH /api/staff/members/{id}/`
- **Delete staff**: `DELETE /api/staff/members/{id}/`

**Filters**: `?role=astronomer`, `?status=active`, `?prefers_night_shifts=true`
**Search**: `?search=John`

#### Staff Availability
- **List availability**: `GET /api/staff/availability/`
- **Get one**: `GET /api/staff/availability/{id}/`
- **Create**: `POST /api/staff/availability/`
- **Update**: `PUT /api/staff/availability/{id}/`
- **Delete**: `DELETE /api/staff/availability/{id}/`

**Filters**: `?staff_member=1`, `?availability_type=unavailable`

---

### 🔭 Observatory

#### Telescopes
- **List all telescopes**: `GET /api/observatory/telescopes/`
- **Get one telescope**: `GET /api/observatory/telescopes/{id}/`
- **Create telescope**: `POST /api/observatory/telescopes/`
- **Update telescope**: `PUT /api/observatory/telescopes/{id}/`
- **Delete telescope**: `DELETE /api/observatory/telescopes/{id}/`

**Filters**: `?is_active=true`
**Search**: `?search=VLT`

#### Instruments
- **List all instruments**: `GET /api/observatory/instruments/`
- **Get one instrument**: `GET /api/observatory/instruments/{id}/`
- **Create instrument**: `POST /api/observatory/instruments/`
- **Update instrument**: `PUT /api/observatory/instruments/{id}/`
- **Delete instrument**: `DELETE /api/observatory/instruments/{id}/`

**Filters**: `?telescope=1`, `?is_active=true`

---

### 📅 Shifts & Schedules

#### Shifts
- **List all shifts**: `GET /api/shifts/`
- **Get one shift**: `GET /api/shifts/{id}/`
- **Create shift**: `POST /api/shifts/`
- **Update shift**: `PUT /api/shifts/{id}/`
- **Delete shift**: `DELETE /api/shifts/{id}/`

**Filters**: `?shift_type=night`, `?status=scheduled`, `?assigned_staff=1`, `?telescope=1`
**Search**: `?search=observations`

#### Schedules
- **List all schedules**: `GET /api/schedules/`
- **Get one schedule**: `GET /api/schedules/{id}/`
- **Create schedule**: `POST /api/schedules/`
- **Update schedule**: `PUT /api/schedules/{id}/`
- **Delete schedule**: `DELETE /api/schedules/{id}/`

**Filters**: `?status=published`

---

## Example Requests

### Get all staff members
```bash
curl http://localhost:8000/api/staff/members/
```

### Get night shifts only
```bash
curl http://localhost:8000/api/shifts/?shift_type=night
```

### Create a new shift
```bash
curl -X POST http://localhost:8000/api/shifts/ \
  -H "Content-Type: application/json" \
  -d '{
    "shift_type": "night",
    "status": "scheduled",
    "start_time": "2025-10-15T20:00:00Z",
    "end_time": "2025-10-16T06:00:00Z",
    "assigned_staff": 1,
    "telescope": 1
  }'
```

---

## Response Format

All list endpoints return paginated results:

```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "full_name": "John Doe",
      "role": "astronomer",
      // ... more fields
    }
  ]
}
```

---

## Authentication

⚠️ **Currently**: Authentication is DISABLED for testing
🔐 **Production**: Will require JWT token in header:
```
Authorization: Bearer <token>
```

---

## Testing in Browser

You can test all endpoints in your browser using Django REST Framework's browsable API:
- Open any endpoint URL in Chrome
- You'll see a nice interface to browse and test the API
- Use the HTML form at the bottom to POST/PUT/DELETE
