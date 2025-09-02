# Full Stack Application - Hiring Assignment

A full-stack web application with a FastAPI backend and React frontend, featuring user authentication, organization management, todos, and notes functionality with comprehensive role-based access control (RBAC) and multi-tenancy.

## 🎯 Assignment Overview

This project demonstrates:
- **Multi-tenant Architecture**: Organization-based data isolation
- **Role-Based Access Control (RBAC)**: Per-organization admin/member roles
- **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **RESTful API Design**: Well-structured FastAPI backend with comprehensive validation
- **Modern Frontend**: React with TanStack Query for efficient state management
- **Database Management**: PostgreSQL with Alembic migrations
- **Comprehensive Testing**: 37+ backend tests covering all functionality
- **Docker Deployment**: Production-ready containerized setup

## 📋 Table of Contents

- [Assignment Overview](#assignment-overview)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Development Setup](#development-setup)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Database Management](#database-management)
- [Testing](#testing)
- [Test Documentation](#test-documentation)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Role-Based Access Control](#role-based-access-control)
- [Multi-Tenancy & Organization Isolation](#multi-tenancy--organization-isolation)
- [Troubleshooting](#troubleshooting)

## � Key Features

### Authentication & Security
- JWT-based authentication with secure token handling
- Bcrypt password hashing
- Protected routes and endpoints
- Session management

### Multi-Tenant Architecture
- Organization-based data isolation
- Users can belong to multiple organizations
- Complete data separation between organizations
- Secure cross-organization access prevention

### Role-Based Access Control (RBAC)
- **Per-organization roles**: Admin and Member roles per organization
- **Admin permissions**: 
  - Create/update/delete todos and notes
  - Invite users to organization
  - Update member roles
  - Manage organization settings
  - Remove members (except last admin)
- **Member permissions**: 
  - Create/update todos and notes
  - View organization resources
  - Cannot delete resources or manage users

### Core Functionality
- **Todo Management**: Create, read, update, delete todos with completion tracking
- **Notes Management**: Create, read, update, delete notes with rich content
- **Organization Management**: Create organizations, invite users, manage members
- **User Management**: Registration, authentication, profile management

## �🔧 Prerequisites

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
- User authentication and authorization with JWT
- **Per-organization role-based access control (RBAC)**
- **Multi-tenant architecture** with complete data isolation
- Organization management with member invitation system
- CRUD operations for todos and notes with role-based permissions
- Database migrations with Alembic
- **Comprehensive test suite** (37+ tests)

### Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Test Database Configuration
Tests use a separate PostgreSQL database:
```env
TEST_DATABASE_URL=postgresql://postgres:postgres@db:5432/test_db
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

# Run tests with detailed output
pytest -s -v
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

## 📊 Test Documentation

The application includes **37+ comprehensive backend tests** covering all critical functionality:

### Test Architecture
- **PostgreSQL Test Database**: Uses separate test database for isolation
- **Session-based Testing**: Each test gets a fresh database session
- **Fixture-based Setup**: Reusable test fixtures for users, organizations, and data
- **Authentication Helpers**: Utility functions for JWT token generation in tests

### Test Coverage by Category

#### 1. Authentication Tests (`test_auth.py`) - 1 test
- ✅ **User Registration & Login Flow**
  - `test_signup_and_login()`: Complete signup → login → JWT token flow

#### 2. Organization Management Tests (`test_organizations.py`) - 13 tests
- ✅ **Organization Creation**
  - `test_create_organization()`: New organization creation
  - `test_can_create_multiple_orgs()`: Multiple organization support
- ✅ **Organization Membership**
  - `test_get_my_organizations()`: List user organizations with members
  - `test_user_multiple_organizations()`: Multi-organization membership
  - `test_add_existing_user_to_organization()`: Adding existing users
- ✅ **User Invitation System**
  - `test_invite_user_to_organization()`: Invite new users with temporary passwords
- ✅ **Role Management**
  - `test_update_member_role()`: Admin-only role updates
  - `test_cannot_remove_last_admin()`: Last admin protection
  - `test_member_cannot_invite_users()`: Permission validation
- ✅ **Organization Administration**
  - `test_list_organization_members()`: Member listing
  - `test_remove_member_from_organization()`: Member removal (admin only)
  - `test_update_organization_details()`: Organization updates (admin only)
  - `test_member_cannot_update_organization()`: Permission validation
- ✅ **Security & Validation**
  - `test_unauthorized_access_to_org_endpoints()`: Authentication requirements
  - `test_invite_duplicate_user_fails()`: Duplicate user handling
  - `test_validate_organization_name()`: Input validation

#### 3. Todo Management Tests (`test_todos.py` + `test_todos_crud.py`) - 15 tests
- ✅ **RBAC for Todos**
  - `test_member_can_create_but_not_delete_todo()`: Role-based permissions
  - `test_admin_can_delete_todo()`: Admin deletion rights
  - `test_member_can_update_todos()`: Member update permissions
  - `test_admin_can_delete_member_todo()`: Admin can delete any todo
- ✅ **CRUD Operations**
  - `test_create_todo_as_member()`: Member todo creation
  - `test_create_todo_as_admin()`: Admin todo creation
  - `test_list_todos()`: Organization-scoped listing
  - `test_get_individual_todo()`: Individual todo retrieval
  - `test_update_todo_as_member()`: Member updates
  - `test_update_todo_as_admin()`: Admin updates
- ✅ **Security & Isolation**
  - `test_users_can_only_see_todos_from_their_organization()`: Organization isolation
  - `test_unauthorized_access_to_todos()`: Authentication requirements
- ✅ **Error Handling**
  - `test_todo_not_found_errors()`: 404 error handling
  - `test_todo_validation_errors()`: Input validation
  - `test_member_cannot_delete_todo()`: Permission validation

#### 4. Notes & RBAC Tests (`test_rbac.py`) - 4 tests
- ✅ **Role-Based Access Control**
  - `test_admin_can_create_and_delete_notes()`: Admin permissions for notes
  - `test_member_can_create_but_not_delete_notes()`: Member restrictions
  - `test_member_cannot_delete_admin_notes()`: Cross-user restrictions
  - `test_users_can_only_see_notes_from_their_organization()`: Organization isolation

#### 5. Organization Isolation Tests (`test_org_isolation.py`) - 4 tests
- ✅ **Multi-Tenancy Security**
  - `test_user_cannot_access_other_org_notes()`: Cross-org note isolation
  - `test_user_cannot_access_other_org_todos()`: Cross-org todo isolation
  - `test_list_endpoints_respect_org_boundaries()`: List endpoint isolation
  - `test_cross_org_admin_cannot_delete_other_org_resources()`: Admin isolation

#### 6. Frontend Tests (`App.test.js`) - 1 test
- ✅ **Basic React Rendering**
  - Basic component rendering test (minimal coverage)

### Test Quality Features
- **Unique Test Data**: Uses UUID to prevent test interference
- **Proper Cleanup**: Database rollback after each test
- **Comprehensive Fixtures**: Reusable test data setup
- **Error Scenario Coverage**: Tests both success and failure cases
- **Permission Matrix Testing**: Validates all role combinations
- **Data Isolation Verification**: Ensures multi-tenancy works correctly

### Test Database Setup
Tests use a dedicated PostgreSQL test database (`test_db`) with:
- Automatic schema creation/teardown
- Session-based isolation
- Transactional rollbacks for cleanup
- Same schema as production database

## 📊 Test Documentation

The application includes **37+ comprehensive backend tests** covering all critical functionality:

### Test Architecture
- **PostgreSQL Test Database**: Uses separate test database for isolation
- **Session-based Testing**: Each test gets a fresh database session
- **Fixture-based Setup**: Reusable test fixtures for users, organizations, and data
- **Authentication Helpers**: Utility functions for JWT token generation in tests

### Test Coverage by Category

#### 1. Authentication Tests (`test_auth.py`) - 1 test
- ✅ **User Registration & Login Flow**
  - `test_signup_and_login()`: Complete signup → login → JWT token flow

#### 2. Organization Management Tests (`test_organizations.py`) - 13 tests
- ✅ **Organization Creation**
  - `test_create_organization()`: New organization creation
  - `test_can_create_multiple_orgs()`: Multiple organization support
- ✅ **Organization Membership**
  - `test_get_my_organizations()`: List user organizations with members
  - `test_user_multiple_organizations()`: Multi-organization membership
  - `test_add_existing_user_to_organization()`: Adding existing users
- ✅ **User Invitation System**
  - `test_invite_user_to_organization()`: Invite new users with temporary passwords
- ✅ **Role Management**
  - `test_update_member_role()`: Admin-only role updates
  - `test_cannot_remove_last_admin()`: Last admin protection
  - `test_member_cannot_invite_users()`: Permission validation
- ✅ **Organization Administration**
  - `test_list_organization_members()`: Member listing
  - `test_remove_member_from_organization()`: Member removal (admin only)
  - `test_update_organization_details()`: Organization updates (admin only)
  - `test_member_cannot_update_organization()`: Permission validation
- ✅ **Security & Validation**
  - `test_unauthorized_access_to_org_endpoints()`: Authentication requirements
  - `test_invite_duplicate_user_fails()`: Duplicate user handling
  - `test_validate_organization_name()`: Input validation

#### 3. Todo Management Tests (`test_todos.py` + `test_todos_crud.py`) - 15 tests
- ✅ **RBAC for Todos**
  - `test_member_can_create_but_not_delete_todo()`: Role-based permissions
  - `test_admin_can_delete_todo()`: Admin deletion rights
  - `test_member_can_update_todos()`: Member update permissions
  - `test_admin_can_delete_member_todo()`: Admin can delete any todo
- ✅ **CRUD Operations**
  - `test_create_todo_as_member()`: Member todo creation
  - `test_create_todo_as_admin()`: Admin todo creation
  - `test_list_todos()`: Organization-scoped listing
  - `test_get_individual_todo()`: Individual todo retrieval
  - `test_update_todo_as_member()`: Member updates
  - `test_update_todo_as_admin()`: Admin updates
- ✅ **Security & Isolation**
  - `test_users_can_only_see_todos_from_their_organization()`: Organization isolation
  - `test_unauthorized_access_to_todos()`: Authentication requirements
- ✅ **Error Handling**
  - `test_todo_not_found_errors()`: 404 error handling
  - `test_todo_validation_errors()`: Input validation
  - `test_member_cannot_delete_todo()`: Permission validation

#### 4. Notes & RBAC Tests (`test_rbac.py`) - 4 tests
- ✅ **Role-Based Access Control**
  - `test_admin_can_create_and_delete_notes()`: Admin permissions for notes
  - `test_member_can_create_but_not_delete_notes()`: Member restrictions
  - `test_member_cannot_delete_admin_notes()`: Cross-user restrictions
  - `test_users_can_only_see_notes_from_their_organization()`: Organization isolation

#### 5. Organization Isolation Tests (`test_org_isolation.py`) - 4 tests
- ✅ **Multi-Tenancy Security**
  - `test_user_cannot_access_other_org_notes()`: Cross-org note isolation
  - `test_user_cannot_access_other_org_todos()`: Cross-org todo isolation
  - `test_list_endpoints_respect_org_boundaries()`: List endpoint isolation
  - `test_cross_org_admin_cannot_delete_other_org_resources()`: Admin isolation

#### 6. Frontend Tests (`App.test.js`) - 1 test
- ✅ **Basic React Rendering**
  - Basic component rendering test (minimal coverage)

### Test Quality Features
- **Unique Test Data**: Uses UUID to prevent test interference
- **Proper Cleanup**: Database rollback after each test
- **Comprehensive Fixtures**: Reusable test data setup
- **Error Scenario Coverage**: Tests both success and failure cases
- **Permission Matrix Testing**: Validates all role combinations
- **Data Isolation Verification**: Ensures multi-tenancy works correctly

### Running Specific Test Categories
```bash
# Run only organization tests
pytest tests/test_organizations.py -v

# Run only RBAC tests
pytest tests/test_rbac.py -v

# Run only isolation tests
pytest tests/test_org_isolation.py -v

# Run only todo tests
pytest tests/test_todos*.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

## 🎯 Assignment Evaluation Guide

### Quick Test Run for Evaluation
```bash
# 1. Start the application
docker-compose up --build -d

# 2. Run the full test suite
cd backend && pytest -v

# 3. Check API documentation
# Visit: http://localhost:8000/docs

# 4. Test the frontend
cd ../frontend && npm test

# 5. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Key Areas Demonstrated
1. **Authentication System**: Secure JWT-based authentication
2. **Multi-Tenancy**: Complete organization-based data isolation
3. **RBAC Implementation**: Per-organization admin/member roles
4. **API Design**: RESTful endpoints with proper HTTP status codes
5. **Database Design**: Normalized schema with proper relationships
6. **Testing Strategy**: Comprehensive test coverage (37+ tests)
7. **Security**: Cross-organization access prevention
8. **Error Handling**: Proper validation and error responses
9. **DevOps**: Docker containerization and development environment

## � Role-Based Access Control

### Organization Roles
The application uses **per-organization roles** :

- **ADMIN**: Full permissions within their organization
  - Create, read, update, delete todos and notes
  - Invite new users to organization
  - Update member roles (except cannot demote last admin)
  - Remove members from organization
  - Update organization settings
  
- **MEMBER**: Limited permissions within their organization
  - Create, read, update todos and notes
  - Cannot delete todos or notes
  - Cannot invite users or manage organization
  - Cannot change roles or remove members

### Permission Matrix

| Action | Admin | Member |
|--------|-------|--------|
| Create Todo/Note | ✅ | ✅ |
| Read Todo/Note | ✅ | ✅ |
| Update Todo/Note | ✅ | ✅ |
| Delete Todo/Note | ✅ | ❌ |
| Invite Users | ✅ | ❌ |
| Update Roles | ✅ | ❌ |
| Remove Members | ✅ | ❌ |
| Update Organization | ✅ | ❌ |

### Security Features
- Users can only access resources from their own organizations
- Cross-organization data access is completely blocked
- Last admin protection (cannot remove or demote the last admin)
- JWT token validation on all protected endpoints

## 🏢 Multi-Tenancy & Organization Isolation

### Data Isolation
- **Complete Separation**: Users can only see data from organizations they belong to
- **API Filtering**: All endpoints automatically filter by user's organization
- **Cross-Organization Protection**: Even admins cannot access other organizations' data
- **Database Level**: Data isolation implemented at the query level

### Organization Features
- Users can belong to multiple organizations simultaneously
- Each organization maintains separate data spaces
- Role permissions are organization-specific
- Secure invitation system with temporary passwords

```
## 📁 Project Structure

```
assignment/                     # Hiring Assignment Project
├── docker-compose.yml          # Docker services configuration
├── flake.nix                   # Nix development environment
├── package.json                # Root package.json
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API routes and endpoints
│   │   │   ├── deps.py        # Dependency injection
│   │   │   └── endpoints/     # Route handlers
│   │   ├── core/              # Core configurations
│   │   │   ├── config.py      # App configuration
│   │   │   └── security.py    # JWT and password hashing
│   │   ├── crud/              # Database operations
│   │   │   ├── crud_note.py   # Notes CRUD operations
│   │   │   ├── crud_organization.py # Organization CRUD
│   │   │   └── crud_todo.py   # Todos CRUD operations
│   │   ├── db/                # Database configuration
│   │   │   ├── base.py        # Base model imports
│   │   │   └── session.py     # Database session management
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py        # User model with per-org roles
│   │   │   ├── organization.py # Organization model
│   │   │   ├── user_organization.py # Many-to-many with roles
│   │   │   ├── todo.py        # Todo model
│   │   │   └── note.py        # Note model
│   │   └── schemas/           # Pydantic schemas for API
│   │       ├── user.py        # User request/response schemas
│   │       ├── organization.py # Organization schemas
│   │       ├── todo.py        # Todo schemas
│   │       └── note.py        # Note schemas
│   ├── alembic/               # Database migrations
│   │   ├── versions/          # Migration files
│   │   └── env.py            # Migration environment
│   ├── tests/                 # Comprehensive test suite (37+ tests)
│   │   ├── conftest.py        # Test configuration and fixtures
│   │   ├── test_auth.py       # Authentication tests
│   │   ├── test_organizations.py # Organization management tests
│   │   ├── test_todos.py      # Todo functionality tests
│   │   ├── test_todos_crud.py # Todo CRUD operation tests
│   │   ├── test_rbac.py       # Role-based access control tests
│   │   └── test_org_isolation.py # Multi-tenancy isolation tests
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend Docker image
└── frontend/                   # React frontend
    ├── src/
    │   ├── api/               # API client functions
    │   │   ├── auth.js        # Authentication API calls
    │   │   ├── client.js      # Base HTTP client
    │   │   ├── organizations.js # Organization API calls
    │   │   ├── todos.js       # Todo API calls
    │   │   └── notes.js       # Notes API calls
    │   ├── components/        # Reusable React components
    │   │   ├── Navigation.js  # Navigation component
    │   │   ├── LoadingSpinner.js # Loading states
    │   │   └── ErrorBoundary.js # Error handling
    │   ├── context/           # React context providers
    │   ├── hooks/             # Custom React hooks
    │   └── pages/             # Page components
    ├── public/                # Static assets
    ├── package.json           # Frontend dependencies
    └── Dockerfile            # Frontend Docker image
```
```

## 🏗️ Database Schema

### Core Models
- **User**: Authentication and user information
- **Organization**: Multi-tenant organization entities
- **UserOrganization**: Many-to-many relationship with per-organization roles
- **Todo**: Task management with organization isolation
- **Note**: Note-taking with organization isolation

### Role System
```python
class UserOrganizationRole(str, enum.Enum):
    ADMIN = "ADMIN"    # Full permissions within organization
    MEMBER = "MEMBER"  # Limited permissions within organization
```

### Relationships
- Users ↔ Organizations: Many-to-many with roles
- Users → Todos: One-to-many (creator relationship)
- Users → Notes: One-to-many (creator relationship)
- Organization isolation enforced at query level

## 📚 API Documentation

When the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key API Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT token)

#### Organizations
- `GET /organizations/my` - List user's organizations with members
- `POST /organizations/` - Create new organization
- `PUT /organizations/{org_id}` - Update organization details (admin only)
- `POST /organizations/{org_id}/invite` - Invite user to organization (admin only)
- `GET /organizations/{org_id}/members` - List organization members
- `PUT /organizations/{org_id}/members/{user_id}/role` - Update member role (admin only)
- `DELETE /organizations/{org_id}/members/{user_id}` - Remove member (admin only)
- `POST /organizations/{org_id}/members/{user_id}` - Add existing user to organization

#### Todos
- `GET /todos/` - List todos (organization-scoped)
- `POST /todos/` - Create todo (all users)
- `GET /todos/{todo_id}` - Get specific todo
- `PUT /todos/{todo_id}` - Update todo (all users)
- `DELETE /todos/{todo_id}` - Delete todo (admin only)

#### Notes
- `GET /notes/` - List notes (organization-scoped)
- `POST /notes/` - Create note (all users)
- `GET /notes/{note_id}` - Get specific note
- `PUT /notes/{note_id}` - Update note (all users)
- `DELETE /notes/{note_id}` - Delete note (admin only)

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

### Running the Complete Test Suite
```bash
# Clone the repository
git clone <repository-url>
cd assignment

# Start with Docker (recommended for evaluation)
docker-compose up --build

# Or run tests directly
cd backend
pip install -r requirements.txt
pytest -v --cov=app

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

For questions or issues, please open an issue in the repository.
