# BodyBack FastAPI Backend - Project Instructions

## Project Overview
FastAPI backend serving the BodyBack mobile application and future web clients. Handles authentication, user management, session tracking, and business logic.

## Tech Stack
- **Framework**: FastAPI with Python 3.x
- **Database**: PostgreSQL (bodyback_db) with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh mechanism
- **Validation**: Pydantic schemas
- **Migrations**: Alembic
- **Server**: Uvicorn ASGI server
- **Caching**: Redis (configured but optional)

## Project Structure
```
/app
  /api/v1/          - API endpoints
  /core/            - Core configuration and dependencies
  /crud/            - Database CRUD operations
  /models/          - SQLAlchemy models
  /schemas/         - Pydantic schemas
  main.py           - Application entry point
/alembic/           - Database migrations
/tests/             - Test files
```

## Key Features Implemented

### Authentication & Authorization
- JWT access tokens (15 min expiry)
- Refresh tokens (7 day expiry)
- Role-based access control (Admin, Trainer, Customer)
- Token refresh endpoint
- Password hashing with bcrypt
- User activation/deactivation

### User Management
- User CRUD operations
- Profile management (separate from user table)
- Role assignment
- Active/inactive status
- Soft deletes (deleted_at timestamp)

### Trainer Features
- Trainer profile management
- Customer assignment to trainers
- Trainer statistics (customer count, sessions)
- Get trainer's customer list
- Admin-only customer assignment/removal

### Customer Features
- Customer profile management
- Trainer assignment
- Customer statistics

### Session Volume Tracking (✅ Recently Enhanced)
- Create session volumes (trainer → customer, monthly)
- Status workflow: draft → submitted → read → approved/rejected
- Duplicate prevention (unique per trainer-customer-period)
- Edit restrictions (only draft/rejected can be edited)
- Role-based permissions:
  - Trainers: create, update draft/rejected, submit
  - Customers: view, approve, reject, mark as read
  - Admins: full access
- Filter by trainer, customer, status, date range
- Get volumes by period (year/month)

### QR Code Management
- Generate QR codes for customers
- QR code verification
- Check-in tracking

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /login` - Login with email/password
- `POST /refresh` - Refresh access token
- `POST /logout` - Logout (optional - client-side token deletion)

### Users (`/api/v1/users`)
- `GET /users` - List users (admin only)
- `GET /users/me` - Get current user
- `POST /users` - Create user (admin only)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Soft delete user (admin only)

### Trainers (`/api/v1/trainers`)
- `GET /trainers` - List all trainers
- `GET /trainers/{trainer_id}` - Get trainer details
- `GET /trainers/{trainer_id}/customers` - Get trainer's customers (✅ returns only active)
- `GET /trainers/me/stats` - Get current trainer's statistics
- `POST /trainers/{trainer_id}/assign-customer` - Assign customer (admin only)
- `DELETE /trainers/{trainer_id}/remove-customer` - Remove customer (admin only)

### Customers (`/api/v1/customers`)
- `GET /customers` - List customers (admin only)
- `GET /customers/{customer_id}` - Get customer details
- `PUT /customers/{customer_id}` - Update customer

### Session Volumes (`/api/v1/session-volumes`)
- `GET /session-volumes` - List with filters (role-based)
- `POST /session-volumes` - Create new volume (trainer/admin)
- `GET /session-volumes/{volume_id}` - Get volume details
- `PUT /session-volumes/{volume_id}` - Update volume (draft/rejected only)
- `DELETE /session-volumes/{volume_id}` - Soft delete (admin only)
- `POST /session-volumes/{volume_id}/submit` - Submit to customer (trainer)
- `POST /session-volumes/{volume_id}/approve` - Approve volume (customer)
- `POST /session-volumes/{volume_id}/reject` - Reject volume (customer, reason required)
- `POST /session-volumes/{volume_id}/reopen` - Reopen rejected volume (trainer)
- `GET /session-volumes/period/{year}/{month}` - Get volumes by period

### Profiles (`/api/v1/profiles`)
- `GET /profiles/me` - Get current user's profile
- `PUT /profiles/me` - Update current user's profile
- `GET /profiles/{user_id}` - Get user profile

### QR Codes (`/api/v1/qr-codes`)
- `GET /qr-codes/my-code` - Get customer's QR code
- `POST /qr-codes/generate` - Generate new QR code
- `POST /qr-codes/verify` - Verify and check-in with QR code

## Database Models

### Core Tables
- `users` - Authentication and core user data
- `profiles` - Extended user profile information
- `trainers` - Trainer-specific data
- `customers` - Customer-specific data (includes trainer_id)
- `session_volumes` - Monthly session volume tracking
- `qr_codes` - Customer QR codes for check-in

### Key Relationships
- User → Profile (1:1)
- User → Trainer (1:1, role-based)
- User → Customer (1:1, role-based)
- Trainer → Customers (1:N via customer.trainer_id)
- Customer → SessionVolumes (1:N via customer_id)
- Trainer → SessionVolumes (1:N via trainer_id)

## Important Business Logic

### Session Volume Workflow
1. **Draft** - Trainer creates and edits
2. **Submitted** - Trainer submits to customer for review
3. **Read** - Customer has viewed (auto-marked on approve/reject)
4. **Approved** - Customer approves (final state)
5. **Rejected** - Customer rejects with reason
6. After rejection, trainer can **Reopen** back to draft

### Permission Rules
- Trainers can only see their own customers and volumes
- Customers can only see volumes where they are the customer
- Admins can see everything
- Only draft/rejected volumes can be edited
- Cannot delete approved volumes
- Duplicate prevention enforced at database level

### Data Validation
- Email format validation
- Role validation (Admin, Trainer, Customer)
- Status validation for state transitions
- Unique constraints on critical fields
- Required fields enforced

## Recent Bug Fixes & Enhancements

### Fixed: Duplicate Session Volume Creation
**Issue**: Could create multiple draft volumes for same period
**Fix**: Changed from `get_or_create_for_period()` to direct existence check
**Location**: `/app/api/v1/session_volumes.py` lines 118-135
**Result**: Now properly prevents duplicates regardless of session_count value

### Enhanced: Session Volume Editing
**What**: Added status-based edit restrictions
**Logic**:
- Editable: draft, rejected
- Read-only: submitted, read, approved
**Enforced**: Both in API validation and React Native UI

## Configuration
- Database connection via environment variables
- JWT secret key configuration
- Token expiry times configurable
- CORS configured for React Native app
- File upload handling configured

## Testing Accounts
- Admin: (check database)
- Trainer: `trainer@bodyback.co.za`
- Customer: `customer@bodyback.co.za`

## Development Notes
- All timestamps in UTC
- Soft deletes used (deleted_at field)
- Foreign key constraints enforced
- Transactions handled by SQLAlchemy
- Error responses standardized with HTTPException
- All list endpoints support pagination (skip/limit)

## TODO / Known Issues
1. Session counting not yet implemented in trainer stats (returns 0)
2. Need to implement actual session tracking (check-ins)
3. Consider moving phone_number/location from users to profiles table
4. Add email notifications for session volume submissions/approvals
5. Add file upload for session plans (PDFs, images)
6. Implement session attendance tracking

## Running the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Integration with React Native App
- Base URL configured in app's `services/api.ts`
- JWT tokens passed in Authorization header
- Refresh token handled automatically by interceptor
- All endpoints return JSON
- Error responses include detail message
- Success responses follow consistent schema patterns
