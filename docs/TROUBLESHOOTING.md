# Troubleshooting: "Failed to load schedule data"

## Problem
The error "Failed to load schedule data" appears when accessing http://localhost:5173/schedule

## Root Cause
The Django backend server is not running on port 8000.

## Solution

### Step 1: Start the Django Server

Open a terminal and run:

```bash
cd /Users/bquint/GitHub/b1quint/unified_shift_scheduler/backend
python manage.py runserver
```

Or if you're using the virtual environment:

```bash
cd /Users/bquint/GitHub/b1quint/unified_shift_scheduler/backend
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows
python manage.py runserver
```

### Step 2: Verify the Server is Running

You should see output like:

```
Django version 5.0.14, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Step 3: Test the API

Open your browser or use curl to test:

```bash
curl http://localhost:8000/api/staff/teams/
```

You should see JSON data with teams.

### Step 4: Refresh the Frontend

Once the Django server is running, refresh http://localhost:5173/schedule and the calendar should load with data.

---

## Additional Checks

### Check if Django is listening on port 8000

```bash
lsof -i :8000
```

If nothing is returned, Django is not running.

### Check for Django errors

When you start `python manage.py runserver`, watch for any error messages about:
- Missing migrations
- Database errors
- Import errors
- Module not found errors

### Verify React is pointing to the right API

Check `frontend/vite.config.js` - it should have:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### Check browser console

Open Developer Tools (F12) → Console tab and look for:
- Network errors (404, 500, connection refused)
- CORS errors
- JavaScript errors

---

## Quick Checklist

- [ ] Django server running on port 8000
- [ ] React dev server running on port 5173
- [ ] Database has data (run `python manage.py seed_rubin_data` if needed)
- [ ] No errors in Django terminal
- [ ] No errors in browser console
- [ ] API endpoint works: `curl http://localhost:8000/api/staff/teams/`

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'django'"
**Solution**: Activate the virtual environment first

### Issue: "CORS policy" error
**Solution**: Check that `django-cors-headers` is installed and configured in settings.py

### Issue: "no such table" error
**Solution**: Run migrations: `python manage.py migrate`

### Issue: Empty calendar
**Solution**: Run seed data: `python manage.py seed_rubin_data`

---

Once Django is running, everything should work! 🚀
