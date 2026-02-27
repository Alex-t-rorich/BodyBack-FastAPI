from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer, BadSignature
from uuid import UUID

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.crud.user import user_crud
from app.crud.customer import customer_crud
from app.crud.trainer import trainer_crud
from app.models.user import User
from app.models.customer import Customer
from app.schemas.user import UserCreate
from app.models.session_tracking import SessionTracking
from app.models.qr_code import QRCode
from sqlalchemy import func

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Session serializer for secure cookies
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def get_current_user_from_session(request: Request, db: Session = Depends(get_db)):
    """Get current user from session cookie"""
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None

    try:
        # Decode session cookie (expires after 7 days)
        user_id = serializer.loads(session_cookie, max_age=604800)
        user = user_crud.get(db, id=user_id)
        if user and user_crud.is_active(user):
            return user
    except (BadSignature, Exception):
        return None

    return None


def require_admin(request: Request, db: Session = Depends(get_db)):
    """Require admin user for web routes"""
    user = get_current_user_from_session(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Not authenticated",
            headers={"Location": "/login"}
        )

    if not user.has_role("Admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return user


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page"""
    # If already logged in, redirect to dashboard
    session_cookie = request.cookies.get("session")
    if session_cookie:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("login.html", {
        "request": request
    })


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form"""
    # Authenticate user
    user = user_crud.authenticate(db, email=email, password=password)

    if not user or not user_crud.is_active(user):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        }, status_code=status.HTTP_401_UNAUTHORIZED)

    # Check if user is admin
    if not user.has_role("Admin"):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Admin access only"
        }, status_code=status.HTTP_403_FORBIDDEN)

    # Create session cookie
    session_token = serializer.dumps(str(user.id))
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        max_age=604800,  # 7 days
        samesite="lax"
    )

    return response


@router.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session")
    return response


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, user = Depends(require_admin)):
    """Admin dashboard - requires admin login"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user = Depends(require_admin)):
    """Display user profile page"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })


@router.post("/profile/update")
async def update_profile(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(""),
    location: str = Form(""),
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        # Update user information
        update_data = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number if phone_number else None,
            "location": location if location else None
        }

        user_crud.update(db, db_obj=user, obj_in=update_data)

        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "success": "Profile updated successfully!"
        })
    except Exception as e:
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "error": f"Failed to update profile: {str(e)}"
        })


@router.post("/profile/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not verify_password(current_password, user.password_hash):
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "password_error": "Current password is incorrect"
        })

    if new_password != confirm_password:
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "password_error": "New passwords do not match"
        })

    if current_password == new_password:
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "password_error": "New password must be different from current password"
        })

    if len(new_password) < 8:
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "password_error": "Password must be at least 8 characters long"
        })

    try:
        hashed_password = get_password_hash(new_password)
        user_crud.update(db, db_obj=user, obj_in={"password_hash": hashed_password})

        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "password_success": "Password changed successfully!"
        })
    except Exception as e:
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "password_error": f"Failed to change password: {str(e)}"
        })


@router.get("/customers", response_class=HTMLResponse)
async def customers_page(
    request: Request,
    search: str = None,
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Display customers list with search"""
    # Get all active customers with user and trainer info
    all_customers = customer_crud.get_active(db, skip=0, limit=1000)

    # Get available trainers for assignment dropdown
    available_trainers = trainer_crud.get_active(db, skip=0, limit=1000)

    # Get session counts for all customers (via QR codes)
    # Query: Count session_tracking records grouped by customer's QR code
    session_counts = (
        db.query(
            QRCode.user_id,
            func.count(SessionTracking.id).label('session_count')
        )
        .outerjoin(SessionTracking, SessionTracking.qr_code_id == QRCode.id)
        .group_by(QRCode.user_id)
        .all()
    )

    # Create a dictionary of customer_id -> session_count
    session_count_dict = {str(user_id): count for user_id, count in session_counts}

    # Filter by search if provided
    if search:
        search_lower = search.lower()
        customers = [
            c for c in all_customers
            if (c.user.first_name and search_lower in c.user.first_name.lower()) or
               (c.user.last_name and search_lower in c.user.last_name.lower()) or
               (c.user.email and search_lower in c.user.email.lower())
        ]
    else:
        customers = all_customers

    return templates.TemplateResponse("customers.html", {
        "request": request,
        "user": user,
        "customers": customers,
        "total_customers": len(all_customers),
        "search": search,
        "session_counts": session_count_dict,
        "available_trainers": available_trainers
    })


@router.get("/trainers", response_class=HTMLResponse)
async def trainers_page(
    request: Request,
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Display trainers list"""
    # Get all active trainers
    trainers = trainer_crud.get_active(db, skip=0, limit=1000)

    # Get customer counts for all trainers
    customer_counts_query = (
        db.query(
            Customer.trainer_id,
            func.count(Customer.user_id).label('customer_count')
        )
        .filter(Customer.deleted_at.is_(None))
        .filter(Customer.trainer_id.isnot(None))
        .group_by(Customer.trainer_id)
        .all()
    )

    # Create dictionary of trainer_id -> customer_count
    customer_count_dict = {str(trainer_id): count for trainer_id, count in customer_counts_query}

    return templates.TemplateResponse("trainers.html", {
        "request": request,
        "user": user,
        "trainers": trainers,
        "customer_counts": customer_count_dict
    })


@router.get("/trainers/{trainer_id}", response_class=HTMLResponse)
async def trainer_detail_page(
    request: Request,
    trainer_id: str,
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Display trainer detail page with their customers"""
    # Get trainer
    trainer = trainer_crud.get_by_user_id(db, user_id=trainer_id)

    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    # Get trainer's customers
    customers = trainer_crud.get_customers(db, trainer_id=trainer_id, skip=0, limit=1000)

    # Get unassigned customers (for assignment modal)
    unassigned_customers = customer_crud.get_without_trainer(db, skip=0, limit=1000)

    # Get session counts for all customers
    session_counts = (
        db.query(
            QRCode.user_id,
            func.count(SessionTracking.id).label('session_count')
        )
        .outerjoin(SessionTracking, SessionTracking.qr_code_id == QRCode.id)
        .group_by(QRCode.user_id)
        .all()
    )

    # Create dictionary of customer_id -> session_count
    session_count_dict = {str(user_id): count for user_id, count in session_counts}

    # Calculate total sessions for this trainer
    total_sessions = sum(session_count_dict.get(str(c.user_id), 0) for c in customers)

    return templates.TemplateResponse("trainer_detail.html", {
        "request": request,
        "user": user,
        "trainer": trainer,
        "customers": customers,
        "unassigned_customers": unassigned_customers,
        "session_counts": session_count_dict,
        "total_sessions": total_sessions
    })


@router.post("/trainers/{trainer_id}/assign-customer")
async def assign_customer_to_trainer(
    request: Request,
    trainer_id: str,
    customer_id: str = Form(...),
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign a customer to a trainer"""
    try:
        # Convert string IDs to UUIDs
        trainer_uuid = UUID(trainer_id)
        customer_uuid = UUID(customer_id)

        # Use CRUD to assign customer
        customer = customer_crud.assign_trainer(
            db,
            customer_id=customer_uuid,
            trainer_id=trainer_uuid
        )

        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Redirect back to trainer detail page
        return RedirectResponse(
            url=f"/trainers/{trainer_id}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign customer: {str(e)}")


@router.post("/trainers/create")
async def create_trainer(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(""),
    location: str = Form(""),
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new trainer"""
    try:
        # Check if email already exists
        existing_user = user_crud.get_by_email(db, email=email)
        if existing_user:
            # TODO: Show error in modal instead of raising exception
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Create user with Trainer role
        user_create = UserCreate(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number if phone_number else None,
            location=location if location else None,
            role="Trainer",
            active=True
        )

        # Create the trainer (user_crud.create handles creating User + Trainer record + QR code)
        new_user = user_crud.create(db, obj_in=user_create)

        # Redirect back to trainers list
        return RedirectResponse(
            url="/trainers",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create trainer: {str(e)}")


@router.post("/customers/create")
async def create_customer(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(""),
    location: str = Form(""),
    trainer_id: str = Form(""),
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new customer"""
    try:
        # Check if email already exists
        existing_user = user_crud.get_by_email(db, email=email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Create user with Customer role
        user_create = UserCreate(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number if phone_number else None,
            location=location if location else None,
            role="Customer",
            active=True
        )

        # Create the customer (user_crud.create handles creating User + Customer record + QR code)
        new_user = user_crud.create(db, obj_in=user_create)

        # Assign trainer if selected
        if trainer_id:
            try:
                trainer_uuid = UUID(trainer_id)
                customer_crud.assign_trainer(
                    db,
                    customer_id=new_user.id,
                    trainer_id=trainer_uuid
                )
            except ValueError:
                pass  # Invalid UUID, skip trainer assignment

        # Redirect back to customers list
        return RedirectResponse(
            url="/customers",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(e)}")


@router.get("/users", response_class=HTMLResponse)
async def users_page(
    request: Request,
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Display admin users only"""
    # Get only admin users
    users = user_crud.get_admins(db, skip=0, limit=1000)

    return templates.TemplateResponse("users.html", {
        "request": request,
        "user": user,
        "users": users
    })


@router.post("/users/create")
async def create_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(""),
    location: str = Form(""),
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new admin user"""
    try:
        # Check if email already exists
        existing_user = user_crud.get_by_email(db, email=email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Create admin user
        user_create = UserCreate(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number if phone_number else None,
            location=location if location else None,
            role="Admin",
            active=True
        )

        # Create the admin user
        new_user = user_crud.create(db, obj_in=user_create)

        # Redirect back to users list
        return RedirectResponse(
            url="/users",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
