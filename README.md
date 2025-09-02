# Full Stack Application

A full-stack web application with a FastAPI backend and React frontend, featuring user authentication, organization management, todos, and notes functionality.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Development Setup](#development-setup)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Database Management](#database-management)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Option 1: Using Nix (Recommended)
If you have Nix with flakes enabled:
```bash
nix develop
```
This will provide all necessary dependencies (Docker, Docker Compose, Node.js 20, npm).

### Option 2: Manual Installation
Ensure you have the following installed:
- **Docker** (version 20.10 or later)
- **Docker Compose** (version 2.0 or later)
- **Node.js** (version 20.x or later)
- **npm** (comes with Node.js)

## 🚀 Quick Start with Docker

The fastest way to get the entire application running:

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd assignment
   ```
   
   **Or if setting up locally:**
   ```bash
   cd assignment
   git init  # Initialize git repository
   git add .
   git commit -m "Initial commit"
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - **Frontend:** http://localhost:3000
   - **Backend API:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

## 🛠️ Development Setup

For development with hot reloading and easier debugging:

### Backend Development

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start PostgreSQL database:**
   ```bash
   docker-compose up db -d
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Set environment variables:**
   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/app_db"
   export SECRET_KEY="your-secret-key-change-this"
   ```

7. **Start the backend server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Development

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

The frontend will be available at http://localhost:3000 and will proxy API requests to the backend.

## 🔧 Backend Setup

### Technology Stack
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **PostgreSQL** - Database
- **JWT** - Authentication
- **Pytest** - Testing framework

### Key Features
- User authentication and authorization
- Organization-based multi-tenancy
- CRUD operations for todos and notes
- Role-based access control (RBAC)
- Database migrations

### Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Migration Commands
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Revert to previous migration
alembic downgrade -1

# Check current migration version
alembic current
```

## 🎨 Frontend Setup

### Technology Stack
- **React** - Frontend framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **TanStack Query** - Data fetching and caching
- **Context API** - State management

### Key Features
- User authentication with JWT
- Protected routes
- Organization switching
- Todo and notes management
- Responsive design

### Available Scripts
```bash
npm start          # Start development server
npm run build      # Create production build
npm test           # Run tests
npm run eject      # Eject from Create React App (not recommended)
```

## 🗄️ Database Management

### Using Docker Compose
The PostgreSQL database runs in a Docker container and persists data in a named volume.

```bash
# Start only the database
docker-compose up db -d

# Stop the database
docker-compose stop db

# Remove database and all data
docker-compose down -v
```

### Direct Database Access
```bash
# Connect to the database container
docker-compose exec db psql -U postgres -d app_db

# Or using psql if installed locally
psql -h localhost -U postgres -d app_db
```

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_todos.py

# Run tests in verbose mode
pytest -v
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in CI mode
npm test -- --ci
```

## 📁 Project Structure

```
assignment/
├── docker-compose.yml          # Docker services configuration
├── flake.nix                   # Nix development environment
├── package.json                # Root package.json
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API routes
│   │   ├── core/              # Core configurations
│   │   ├── crud/              # Database operations
│   │   ├── db/                # Database configuration
│   │   ├── models/            # SQLAlchemy models
│   │   └── schemas/           # Pydantic schemas
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend Docker image
└── frontend/                   # React frontend
    ├── src/
    │   ├── api/               # API client functions
    │   ├── components/        # Reusable components
    │   ├── context/           # React context providers
    │   ├── hooks/             # Custom React hooks
    │   └── pages/             # Page components
    ├── public/                # Static assets
    ├── package.json           # Frontend dependencies
    └── Dockerfile            # Frontend Docker image
```

## 📚 API Documentation

When the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key API Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /organizations/` - List organizations
- `GET /todos/` - List todos
- `POST /todos/` - Create todo
- `GET /notes/` - List notes
- `POST /notes/` - Create note

## 🔍 Troubleshooting

### Common Issues

**1. Port conflicts:**
```bash
# Check what's using the ports
sudo lsof -i :3000  # Frontend
sudo lsof -i :8000  # Backend
sudo lsof -i :5432  # PostgreSQL

# Kill processes using the ports
sudo kill -9 <PID>
```

**2. Database connection issues:**
```bash
# Check database is running
docker-compose ps

# View database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up db -d
```

**3. Backend migration issues:**
```bash
# Check migration status
docker-compose exec backend alembic current

# Reset migrations (WARNING: This will lose data)
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

**4. Frontend build issues:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Docker Issues

**Remove all containers and volumes:**
```bash
docker-compose down -v
docker system prune -a
```

**Rebuild containers:**
```bash
docker-compose build --no-cache
docker-compose up
```

### Development vs Production

**Development (with hot reload):**
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm start`
- Database: Docker container

**Production (Docker):**
```bash
docker-compose up -d
```

## 🚀 Deployment

For production deployment:

1. **Update environment variables** in `docker-compose.yml`:
   - Change `SECRET_KEY` to a secure random string
   - Update database credentials
   - Set appropriate CORS origins

2. **Build and run:**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Set up reverse proxy** (nginx/traefik) for HTTPS and domain routing

## 📝 Additional Notes

- The application uses JWT tokens for authentication
- Each user belongs to an organization for data isolation
- The backend includes comprehensive test coverage
- The frontend uses React Query for efficient data fetching
- Database migrations are automatically applied on backend startup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

For questions or issues, please open an issue in the repository.
