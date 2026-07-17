# Truck Driver HOS Planner

Full-stack Django + React freight planning app: enter current, pickup, and drop-off locations plus current cycle hours, then generate a mapped route, required fuel/rest stops, and drawn daily ELD-style log sheets.

## What It Does

- Geocodes locations with OpenStreetMap Nominatim.
- Routes current location -> pickup -> drop-off using the public OSRM routing API.
- Applies property-carrying HOS assumptions: 70 hours / 8 days, 11-hour drive limit, 14-hour duty window, 30-minute break after 8 driving hours, 10-hour rest reset, fuel at least every 1,000 miles, and 1 hour each for pickup/drop-off.
- Draws multiple daily log sheets for longer trips.
- Saves generated trip plans so recent planning history can be reviewed in Django Admin.
- Uses a polished React + Leaflet UI designed for recruiter demos.

## Tech Stack

- Backend: Django 6, Django REST Framework, django-cors-headers, requests.
- Frontend: React 19, TypeScript, Vite, Leaflet, React Leaflet, Lucide icons.
- Map APIs: Nominatim for geocoding and OSRM for route geometry/distance.

## Frontend Structure

The React app is organized by responsibility rather than kept in one large component:

- `src/api`: backend API calls.
- `src/types`: TypeScript request/response models.
- `src/utils`: shared formatting helpers.
- `src/components/layout`: page-level navigation and shell UI.
- `src/components/planner`: trip input and pre-plan cards.
- `src/components/results`: map, timeline, and ELD log output.

This keeps `App.tsx` focused on state orchestration while UI and data-access concerns live in smaller modules.

## Backend Structure

- `trips/views.py`: request validation, API responses, and saved trip history writes.
- `trips/services.py`: routing, geocoding, HOS planning, generated stops, and log-sheet construction.
- `trips/models.py`: persisted trip plan records for recruiter-friendly history/admin review.
- `trips/admin.py`: searchable Django Admin view for saved plans.

## Local Setup

### Required Installations

- Python 3.13+
- Node.js 22+
- npm 10+
- Git

### Backend

```powershell
cd backend
..\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/api`.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The app runs at `http://localhost:5173`.

If Vite reports that port `5173` is already in use, open the alternate URL it prints, such as `http://127.0.0.1:5174`. The Django backend allows local development requests from `localhost` and `127.0.0.1` on any port while `DJANGO_DEBUG=true`.

## Validation Commands

```powershell
cd backend
..\.venv\Scripts\python manage.py check
..\.venv\Scripts\python manage.py test trips
```

```powershell
cd frontend
npm run build
```
