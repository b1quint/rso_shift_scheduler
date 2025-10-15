# Vera Rubin Observatory - Realistic Implementation

## Overview
Updated the shift scheduler to support real-world scenarios for Vera Rubin Observatory with team-specific shift types and custom shift codes.

---

## Database Model Changes

### 1. **New `Team` Model**
Represents different teams/departments at the observatory:
- **Fields**: name, code, description, is_active
- **Examples**: 
  - Observing Specialists (OBS)
  - Support Scientists (SCI)

### 2. **New `ShiftType` Model**
Team-specific shift types with custom codes and colors:
- **Fields**: team (FK), name, code, description, color, default_start_time, default_end_time, default_duration_hours, is_active, sort_order
- **Unique constraint**: team + code combination

**Observing Specialists Shift Types:**
- `1` = Day Shift Lead (orange #f59e0b)
- `2` = Day Shift (amber #fbbf24)
- `3` = Late Shift Lead (indigo #4338ca)
- `4` = Late Shift (blue #6366f1)
- `T` = Training (purple #8b5cf6)
- `B` = Backup (green #10b981)

**Support Scientists Shift Types:**
- `D` = Day Shift (orange #f59e0b)
- `L` = Late Night Shift (indigo #4338ca)

### 3. **Updated `StaffMember` Model**
- Added `team` ForeignKey to Team model
- Staff members now belong to specific teams

### 4. **Updated `Shift` Model**
- Changed `shift_type` from CharField to ForeignKey(ShiftType)
- Removed hardcoded SHIFT_TYPE_CHOICES
- Added `shift_code` property to get display code

---

## API Changes

### New Endpoints

**Teams:**
- `GET /api/staff/teams/` - List all teams
- `GET /api/staff/teams/{id}/` - Get team details

**Shift Types:**
- `GET /api/staff/shift-types/` - List all shift types
- `GET /api/staff/shift-types/?team={id}` - Filter by team

### Updated Endpoints

**Staff Members:**
- Now includes: `team`, `team_name`, `team_code`
- Can filter by: `?team={id}`

**Shifts:**
- Now includes: `shift_code`, `shift_name`, `shift_color`, `shift_type_details`
- Shift codes come from ShiftType model (e.g., "1", "2", "D", "L")
- Colors come from ShiftType model

---

## Frontend Changes

### ScheduleCalendar Component

**New Features:**
1. **Team Filter Dropdown**
   - Located at the top of the page
   - Filters staff by selected team
   - "All Teams" option shows everyone

2. **Dynamic Shift Codes**
   - Shift codes now come from API (`shift_code` field)
   - Colors come from API (`shift_color` field)
   - No hardcoded mappings needed

3. **Team Badges**
   - Staff members show their team code badge (OBS, SCI)
   - Blue badge next to role description

4. **Multiple Shifts Numbering**
   - If staff has multiple shifts on same day: D1, D2, L1, L2, etc.
   - Numbers added automatically when count > 1

---

## Sample Data

### Staff Created (10 total):

**Observing Specialists (6):**
- Sarah Johnson (OBS001)
- Michael Chen (OBS002)
- Emily Rodriguez (OBS003)
- David Kim (OBS004)
- Jessica Williams (OBS005)
- Robert Martinez (OBS006)

**Support Scientists (4):**
- Dr. James Anderson (SCI001)
- Dr. Lisa Thompson (SCI002)
- Dr. Daniel Garcia (SCI003)
- Dr. Maria Lopez (SCI004)

### Shifts Created:
- **84 shifts** for the next 14 days
- **Observing Specialists**: 4 shifts/day (Day Lead, Day, Late Lead, Late)
- **Support Scientists**: 2 shifts/day (Day, Late Night)
- Rotating through staff members

---

## How to Use

### 1. View All Teams
```bash
curl http://localhost:8000/api/staff/teams/
```

### 2. Filter Staff by Team
In the calendar, select "Observing Specialists" or "Support Scientists" from the dropdown.

### 3. View Shift Types
```bash
curl http://localhost:8000/api/staff/shift-types/
```

### 4. Create Custom Team
```python
python manage.py shell

from apps.staff.models import Team, ShiftType

# Create new team
team = Team.objects.create(
    name='Maintenance Crew',
    code='MAINT',
    description='Facility maintenance team'
)

# Create shift types for the team
ShiftType.objects.create(
    team=team,
    name='Morning Shift',
    code='M',
    color='#f59e0b',
    sort_order=1
)
```

---

## Benefits of This Approach

1. **Flexible**: Each team can have completely different shift types
2. **Scalable**: Easy to add new teams and shift types
3. **No Code Changes**: Adding teams doesn't require code modifications
4. **Custom Codes**: Teams can use their preferred shift naming conventions
5. **Visual Distinction**: Each shift type has its own color
6. **Database Driven**: All configuration in database, not hardcoded

---

## Management Commands

### Setup Teams and Shift Types
```bash
python manage.py setup_teams
```

### Seed Vera Rubin Data
```bash
python manage.py seed_rubin_data
```

---

## Next Steps / Future Enhancements

1. **Shift Type Configuration UI**: Web interface to create/edit shift types
2. **Team Management**: UI to manage teams and assign staff
3. **Shift Templates**: Pre-defined shift schedules per team
4. **Conflict Detection**: Prevent overlapping shifts
5. **Team-specific Rules**: Different constraints per team (max hours, rest periods, etc.)
6. **Reporting**: Team-based shift statistics and coverage reports
7. **Export**: PDF/Excel export filtered by team
8. **Notifications**: Team-specific shift notifications

---

## Migration Notes

- **Database Reset**: Since this was a major model change with existing data, the database was reset
- **Data Loss**: Previous test shifts were deleted
- **New Data**: Fresh Vera Rubin data seeded with realistic teams and shifts
- **Production**: In production, would need careful data migration strategy

---

## Testing

### Test Team Filter:
1. Open calendar: http://localhost:5174/schedule
2. Select "Observing Specialists" - should show 6 staff
3. Select "Support Scientists" - should show 4 staff
4. Select "All Teams" - should show all 10 staff

### Test Shift Codes:
- Observing Specialists should show: 1, 2, 3, 4, T, B
- Support Scientists should show: D, L
- Colors should match team's shift type colors

### Test Multiple Shifts:
- If same staff has 2 Day Shifts: shows "21" and "22"
- If same staff has 2 Late Shifts: shows "41" and "42"

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│           React Frontend                 │
│  • Team Filter Dropdown                  │
│  • Dynamic Shift Code Display            │
│  • Team Badge on Staff                   │
└──────────────┬──────────────────────────┘
               │
               │ API Requests
               │ GET /api/staff/teams/
               │ GET /api/staff/members/?team={id}
               │ GET /api/shifts/
               │
┌──────────────▼──────────────────────────┐
│         Django REST API                  │
│  • TeamViewSet                           │
│  • ShiftTypeViewSet                      │
│  • StaffMemberViewSet (filtered)         │
│  • ShiftViewSet (with codes & colors)    │
└──────────────┬──────────────────────────┘
               │
               │ ORM Queries
               │
┌──────────────▼──────────────────────────┐
│         Database Models                  │
│                                          │
│  Team ──┬─→ ShiftType                   │
│         │     ├─ code (1,2,D,L,etc)     │
│         │     ├─ name                    │
│         │     └─ color                   │
│         │                                │
│         └─→ StaffMember                  │
│               └─→ Shift                  │
│                     └─ shift_type (FK)   │
└─────────────────────────────────────────┘
```

---

**This implementation makes the scheduler much more flexible and production-ready for real observatory operations!** 🎉
