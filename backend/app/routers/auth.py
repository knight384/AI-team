from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from ..database import get_db
from ..models import User
from ..schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    AuthResponse,
    TokenResponse,
    ResponseMetadata
)
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_token_fingerprint,
    check_rate_limit,
    store_refresh_token_fingerprint,
    verify_refresh_token_fingerprint,
    generate_rate_limit_key,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from ..redis_client import redis_client

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Configure logging to exclude sensitive data
logger = logging.getLogger(__name__)
logger.addFilter(lambda record: not any(
    field in str(record.msg).lower() 
    for field in ['password', 'token', 'secret']
))


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Creates a new user account with the provided email and password.
    Passwords are hashed using bcrypt before storage.
    Returns access and refresh tokens upon successful registration.
    """
    # Rate limiting check
    rate_limit_key = generate_rate_limit_key(request.email, "register")
    if not await check_rate_limit(redis_client.client, rate_limit_key, max_attempts=5, window_seconds=3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Check if user already exists
    existing_user = User.get_by_email(db, request.email)
    if existing_user:
        logger.info(f"Registration attempt with existing email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password (never log the password)
    hashed_password = hash_password(request.password)
    
    # Create user
    try:
        user = User.create_user(db, request.email, hashed_password)
        logger.info(f"New user registered: {user.email}")
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Generate tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )
    
    # Store refresh token fingerprint in Redis
    refresh_fingerprint = generate_token_fingerprint(refresh_token)
    refresh_expires_seconds = int(refresh_token_expires.total_seconds())
    await store_refresh_token_fingerprint(
        redis_client.client,
        user.id,
        refresh_fingerprint,
        refresh_expires_seconds
    )
    
    # Build response
    token_data = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        refresh_token=refresh_token,
        refresh_expires_in=refresh_expires_seconds
    )
    
    return AuthResponse(
        success=True,
        message="User registered successfully",
        data=token_data,
        metadata=ResponseMetadata()
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return tokens.
    
    Validates credentials and returns access and refresh tokens.
    Implements rate limiting to prevent brute-force attacks.
    """
    # Rate limiting check
    rate_limit_key = generate_rate_limit_key(request.email, "login")
    if not await check_rate_limit(redis_client.client, rate_limit_key, max_attempts=10, window_seconds=600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Find user
    user = User.get_by_email(db, request.email)
    if not user:
        logger.info(f"Login attempt with non-existent email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password (never log the password)
    if not verify_password(request.password, user.hashed_password):
        logger.info(f"Failed login attempt for user: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        logger.info(f"Login attempt for inactive user: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Generate tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )
    
    # Store refresh token fingerprint in Redis
    refresh_fingerprint = generate_token_fingerprint(refresh_token)
    refresh_expires_seconds = int(refresh_token_expires.total_seconds())
    await store_refresh_token_fingerprint(
        redis_client.client,
        user.id,
        refresh_fingerprint,
        refresh_expires_seconds
    )
    
    logger.info(f"User logged in successfully: {user.email}")
    
    # Build response
    token_data = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        refresh_token=refresh_token,
        refresh_expires_in=refresh_expires_seconds
    )
    
    return AuthResponse(
        success=True,
        message="Login successful",
        data=token_data,
        metadata=ResponseMetadata()
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    
    Validates the refresh token and issues a new access token.
    Implements token rotation by issuing a new refresh token.
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify refresh token fingerprint in Redis
    refresh_fingerprint = generate_token_fingerprint(request.refresh_token)
    is_valid = await verify_refresh_token_fingerprint(
        redis_client.client,
        user_id,
        refresh_fingerprint
    )
    
    if not is_valid:
        logger.warning(f"Refresh token fingerprint not found for user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )
    
    # Get user from database
    user = User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Generate new tokens (token rotation)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    new_access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )
    
    # Store new refresh token fingerprint and invalidate old one
    new_refresh_fingerprint = generate_token_fingerprint(new_refresh_token)
    refresh_expires_seconds = int(refresh_token_expires.total_seconds())
    
    # Store new fingerprint
    await store_refresh_token_fingerprint(
        redis_client.client,
        user.id,
        new_refresh_fingerprint,
        refresh_expires_seconds
    )
    
    logger.info(f"Tokens refreshed for user: {user.email}")
    
    # Build response
    token_data = TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        refresh_token=new_refresh_token,
        refresh_expires_in=refresh_expires_seconds
    )
    
    return AuthResponse(
        success=True,
        message="Token refreshed successfully",
        data=token_data,
        metadata=ResponseMetadata()
    )
