# Authentication API Endpoints

## Overview
Authentication endpoints for user login, password management, and token handling.

## Endpoints

### 1. Login
**POST** `/api/v1/auth/login`

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Expiration:**
- Access token: 15 minutes
- Refresh token: 7 days

---

### 2. Refresh Token
**POST** `/api/v1/auth/refresh`

Get a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Note:** Returns both new access and refresh tokens. The old refresh token becomes invalid.

---

### 3. Change Password
**POST** `/api/v1/auth/change-password`

Change the current user's password (requires authentication).

**Headers:**
- `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Incorrect current password or new password same as old
- `401 Unauthorized` - Invalid or missing token

---

### 4. Logout
**POST** `/api/v1/auth/logout`

Logout the current user (requires authentication).

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

**Note:** With JWT tokens, this endpoint serves as a placeholder for client-side token removal. Consider implementing a token blacklist for production.

---

### 5. Forgot Password
**POST** `/api/v1/auth/forgot-password`

Request a password reset token (sent via email in production).

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If an account exists with this email, a password reset link has been sent"
}
```

**Note:** Always returns success for security (doesn't reveal if email exists).

---

### 6. Reset Password
**POST** `/api/v1/auth/reset-password`

Reset password using a reset token.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid or expired reset token

---

## Implementation Notes

### Password Requirements
- Minimum 8 characters
- Enforced via Pydantic schema validation

### Token Management
- JWT tokens with configurable expiration
- Password reset tokens expire after 24 hours
- Reset tokens are single-use

### Security Considerations
1. Passwords are hashed using bcrypt
2. Forgot password endpoint doesn't reveal user existence
3. Reset tokens are cryptographically secure random strings
4. Old reset tokens are invalidated when new ones are created

### Database Schema
The implementation adds a `password_reset_tokens` table with:
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users table
- `token` (String) - Unique reset token
- `expires_at` (DateTime) - Token expiration time
- `used` (Boolean) - Whether token has been used
- `created_at` (DateTime) - Token creation time

### Migration
Run the following to apply the database migration:
```bash
alembic upgrade head
```

## Testing with curl

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Change Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"current_password":"oldpass","new_password":"newpass123"}'
```

### Forgot Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```