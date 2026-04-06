# CMPS_432 — Cloud Storage

AWS-backed cloud file storage with tag filtering, comparable to OneDrive.

## Tech Stack

| Layer     | Technology            |
|-----------|-----------------------|
| Front-end | Vue.js 3 + Vite       |
| API       | FastAPI (Python)      |
| ORM / DB  | SQLAlchemy + SQLite*  |
| Server    | NGINX (reverse proxy) |

> \* SQLite is used by default for local development. Swap `DATABASE_URL` to a PostgreSQL connection string for production.

---

## Project Structure

```
.
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py       # FastAPI entry point & CORS config
│   │   ├── config.py     # Pydantic settings (reads .env)
│   │   ├── database.py   # SQLAlchemy engine / session / Base
│   │   ├── models.py     # ORM models: User, File, Tag
│   │   ├── schemas.py    # Pydantic request/response schemas
│   │   ├── auth.py       # JWT auth helpers, OAuth2 bearer
│   │   └── routers/
│   │       ├── auth.py   # /api/auth/*  register · login · me
│   │       ├── files.py  # /api/files/* upload · list · delete
│   │       └── tags.py   # /api/tags/*  create · list · delete
│   ├── tests/
│   │   ├── conftest.py   # pytest fixtures (TestClient, in-memory DB)
│   │   └── test_api.py   # 10 integration tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/             # Vue 3 + Vite SPA
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── api.js        # Axios wrapper for all API calls
│   │   ├── router/       # Vue Router (/ · /dashboard · /settings · /login · /register)
│   │   ├── stores/       # Pinia stores: auth · files
│   │   ├── views/        # Home · HomeView · LoginView · RegisterView · SettingsView
│   │   └── components/   # FileUpload · FileList
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── Dockerfile
│
├── nginx/
│   ├── nginx.conf        # Reverse-proxy /api → FastAPI; serve Vue static files
│   └── Dockerfile        # Builds Vue then bakes into NGINX image
│
├── docker-compose.yml    # Orchestrates backend + nginx services
└── README.md
```

---

## Quick Start (Docker Compose)

```bash
# Build and start all services
docker compose up --build

# The app will be available at http://localhost:80
```

---

## Local Development (without Docker)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload      # http://localhost:8000
# Interactive API docs: http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
# The dev server proxies /api calls to http://localhost:8000
```

### Running Both Services

Open two terminals:

**Terminal 1 (Backend):**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Then navigate to `http://localhost:5173` in your browser.

**Login Flow:**
1. Click "Register" to create a new account
2. Log in with your credentials
3. Access your dashboard at `/dashboard` to upload and manage files
4. Visit `/settings` to manage your account details
5. Return to `/` (home) to leave feedback

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Key Features

- **User registration & JWT authentication**
- **File upload** with drag-and-drop support (up to 100 MB via NGINX)
- **Tag management** — attach tags during upload or later
- **Tag filtering** — click any tag in the sidebar or the file list to filter
- **Delete files** from the UI
- NGINX rate-limiting (10 req/s per IP, burst 20)
- Aggressive caching headers for static assets

