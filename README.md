# BodyBack FastAPI Backend

A FastAPI-based REST API backend for the BodyBack fitness management platform. Handles authentication, user management, trainer-customer relationships, session tracking, and volume management.

## What is this?

This is the main backend API that serves the BodyBack mobile application (React Native) and manages:
- User authentication and authorization (JWT-based)
- Trainer and customer profiles
- Session volume tracking and approval workflows
- QR code generation for customer check-ins
- Database operations via PostgreSQL

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Redis** - Caching (optional)
- **Uvicorn** - ASGI server

## Project Structure

```
BodyBack-FastAPI/
|-- main.py                     # Application entry point
|-- requirements.txt            # Python dependencies
|-- .env                        # Environment configuration
|-- alembic.ini                 # Migration configuration
|
|-- app/
|   |-- api/v1/                 # API endpoints
|   |   |-- auth.py             # Authentication (login, refresh)
|   |   |-- users.py            # User management
|   |   |-- profiles.py         # User profiles
|   |   |-- trainers.py         # Trainer-specific endpoints
|   |   |-- customers.py        # Customer-specific endpoints
|   |   |-- session_volumes.py # Session volume tracking
|   |   |-- sessions.py         # Session tracking
|   |   |-- qr_codes.py         # QR code management
|   |
|   |-- core/                   # Core configuration
|   |   |-- config.py           # Settings and configuration
|   |   |-- database.py         # Database connection
|   |   |-- auth.py             # Auth utilities
|   |   |-- security.py         # Security functions
|   |
|   |-- models/                 # SQLAlchemy database models
|   |-- schemas/                # Pydantic validation schemas
|   |-- crud/                   # Database CRUD operations
|   |-- routes/                 # Route organization
|   |-- services/               # Business logic
|
|-- alembic/                    # Database migrations
|   |-- versions/               # Migration files
|
|-- tests/                      # Test suite
```

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### Setup

1. **Clone and navigate to the project**
   ```bash
   cd /home/alex/dev/BodyBack/BodyBack-FastAPI
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create or edit `.env` file:
   ```bash
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://postgres:password@localhost:5432/bodyback_db
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

## Running the Application

### Development Mode

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Option 1: Run with Python
python main.py

# Option 2: Run with Uvicorn (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

All API endpoints are prefixed with `/api/v1`:

- **Authentication**: `/api/v1/auth` - Login, token refresh
- **Users**: `/api/v1/users` - User CRUD operations
- **Profiles**: `/api/v1/profiles` - User profile management
- **Trainers**: `/api/v1/trainers` - Trainer operations and stats
- **Customers**: `/api/v1/customers` - Customer management
- **Session Volumes**: `/api/v1/session-volumes` - Volume tracking and approval
- **Sessions**: `/api/v1/sessions` - Session tracking
- **QR Codes**: `/api/v1/qr-codes` - QR code generation and verification

Visit `http://localhost:8000/docs` for interactive API documentation.

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## Common Tasks

### Creating a new endpoint

1. Add route handler in `app/api/v1/`
2. Create Pydantic schemas in `app/schemas/`
3. Add CRUD operations in `app/crud/`
4. Update `app/models/` if new database tables needed
5. Run migrations if database changes made

### Adding a new database model

1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Create migration: `alembic revision --autogenerate -m "add model_name"`
4. Review and apply: `alembic upgrade head`

## Configuration

Key configuration options in `.env`:

```bash
# Security
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# JWT Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server
HOST=0.0.0.0
PORT=8000

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Troubleshooting

**Database connection errors:**
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check DATABASE_URL in `.env` is correct
- Ensure database exists: `createdb bodyback_db`

**Module import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Migration errors:**
- Check alembic.ini has correct database URL
- Try: `alembic stamp head` then `alembic upgrade head`

## Additional Documentation

- See `CLAUDE.md` for detailed project documentation
- API documentation: `http://localhost:8000/docs`
- For auth endpoints: `docs/auth_endpoints.md`

## Notes

- All timestamps are stored in UTC
- Soft deletes are used (deleted_at field)
- JWT tokens are used for authentication
- Role-based access control: Admin, Trainer, Customer
