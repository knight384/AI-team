import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import jwt

from ..main import app
from ..database import get_db
from ..models import Base, User
from ..security import (
    hash_password,
    verify_password,
    create_refresh_token,
    generate_token_fingerprint,
    SECRET_KEY,
    ALGORITHM
)

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }


@pytest.fixture
def create_test_user(test_db):
    """Factory fixture to create test users."""
    def _create_user(email: str, password: str):
        db = TestingSessionLocal()
        hashed_password = hash_password(password)
        user = User.create_user(db, email, hashed_password)
        db.close()
        return user
    return _create_user


class TestRegistration:
    """Test cases for /api/auth/register endpoint."""
    
    def test_register_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert data["message"] == "User registered successfully"
        assert "data" in data
        assert "metadata" in data
        
        # Check token data
        token_data = data["data"]
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["expires_in"] > 0
        assert token_data["refresh_expires_in"] > 0
        
        # Check metadata
        metadata = data["metadata"]
        assert metadata["version"] == "1.0.0"
        assert "timestamp" in metadata
    
    def test_register_duplicate_email(self, client, test_user_data, create_test_user):
        """Test registration with duplicate email."""
        # Create user first
        create_test_user(test_user_data["email"], test_user_data["password"])
        
        # Try to register again with same email
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePassword123!"
        })
        
        assert response.status_code == 422
    
    def test_register_short_password(self, client):
        """Test registration with password too short."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "short"
        })
        
        assert response.status_code == 422
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 422
    
    def test_register_password_hashed(self, client, test_user_data):
        """Test that password is hashed and not stored in plain text."""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        
        # Check database
        db = TestingSessionLocal()
        user = User.get_by_email(db, test_user_data["email"])
        db.close()
        
        # Password should be hashed
        assert user.hashed_password != test_user_data["password"]
        assert verify_password(test_user_data["password"], user.hashed_password)


class TestLogin:
    """Test cases for /api/auth/login endpoint."""
    
    def test_login_success(self, client, test_user_data, create_test_user):
        """Test successful login."""
        create_test_user(test_user_data["email"], test_user_data["password"])
        
        response = client.post("/api/auth/login", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert data["message"] == "Login successful"
        assert "data" in data
        assert "metadata" in data
        
        # Check token data
        token_data = data["data"]
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["expires_in"] > 0
        assert token_data["refresh_expires_in"] > 0
        
        # Check metadata
        metadata = data["metadata"]
        assert metadata["version"] == "1.0.0"
        assert "timestamp" in metadata
    
    def test_login_wrong_password(self, client, test_user_data, create_test_user):
        """Test login with incorrect password."""
        create_test_user(test_user_data["email"], test_user_data["password"])
        
        response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "Password123!"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower()
    
    def test_login_inactive_user(self, client, test_user_data, create_test_user):
        """Test login with inactive user account."""
        user = create_test_user(test_user_data["email"], test_user_data["password"])
        
        # Deactivate user
        db = TestingSessionLocal()
        user = User.get_by_id(db, user.id)
        user.is_active = False
        db.commit()
        db.close()
        
        response = client.post("/api/auth/login", json=test_user_data)
        
        assert response.status_code == 403
        data = response.json()
        assert "inactive" in data["detail"].lower()
    
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format."""
        response = client.post("/api/auth/login", json={
            "email": "not-an-email",
            "password": "Password123!"
        })
        
        assert response.status_code == 422
    
    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        response = client.post("/api/auth/login", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 422


class TestRefresh:
    """Test cases for /api/auth/refresh endpoint."""
    
    def test_refresh_success(self, client, test_user_data, create_test_user):
        """Test successful token refresh."""
        create_test_user(test_user_data["email"], test_user_data["password"])
        
        # Login to get tokens
        login_response = client.post("/api/auth/login", json=test_user_data)
        assert login_response.status_code == 200
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # Refresh token
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert data["message"] == "Token refreshed successfully"
        assert "data" in data
        assert "metadata" in data
        
        # Check token data
        token_data = data["data"]
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # New tokens should be different
        assert token_data["access_token"] != login_response.json()["data"]["access_token"]
        assert token_data["refresh_token"] != refresh_token
    
    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token."""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid.token.here"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()
    
    def test_refresh_expired_token(self, client, test_user_data, create_test_user):
        """Test refresh with expired token."""
        user = create_test_user(test_user_data["email"], test_user_data["password"])
        
        # Create an expired refresh token
        expired_token = jwt.encode(
            {
                "sub": str(user.id),
                "type": "refresh",
                "exp": datetime.utcnow() - timedelta(days=1)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        response = client.post("/api/auth/refresh", json={
            "refresh_token": expired_token
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()
    
    def test_refresh_access_token_rejected(self, client, test_user_data, create_test_user):
        """Test that access token is rejected for refresh endpoint."""
        create_test_user(test_user_data["email"], test_user_data["password"])
        
        # Login to get tokens
        login_response = client.post("/api/auth/login", json=test_user_data)
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]
        
        # Try to use access token for refresh
        response = client.post("/api/auth/refresh", json={
            "refresh_token": access_token
        })
        
        assert response.status_code == 401
    
    def test_refresh_nonexistent_user(self, client):
        """Test refresh with token for non-existent user."""
        # Create a token for non-existent user
        fake_token = jwt.encode(
            {
                "sub": "99999",
                "type": "refresh",
                "exp": datetime.utcnow() + timedelta(days=1)
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        response = client.post("/api/auth/refresh", json={
            "refresh_token": fake_token
        })
        
        assert response.status_code == 401
    
    def test_refresh_inactive_user(self, client, test_user_data, create_test_user):
        """Test refresh with inactive user."""
        user = create_test_user(test_user_data["email"], test_user_data["password"])
        
        # Login to get tokens
        login_response = client.post("/api/auth/login", json=test_user_data)
        assert login_response.status_code == 200
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # Deactivate user
        db = TestingSessionLocal()
        user = User.get_by_id(db, user.id)
        user.is_active = False
        db.commit()
        db.close()
        
        # Try to refresh
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 403
        data = response.json()
        assert "inactive" in data["detail"].lower()
    
    def test_refresh_missing_token(self, client):
        """Test refresh without providing token."""
        response = client.post("/api/auth/refresh", json={})
        
        assert response.status_code == 422


class TestTokenGeneration:
    """Test cases for token generation and validation."""
    
    def test_access_token_contains_user_data(self, client, test_user_data, create_test_user):
        """Test that access token contains user email."""
        create_test_user(test_user_data["email"], test_user_data["password"])
        
        response = client.post("/api/auth/login", json=test_user_data)
        assert response.status_code == 200
        
        access_token = response.json()["data"]["access_token"]
        
        # Decode token
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["email"] == test_user_data["email"]
        assert payload["type"] == "access"
    
    def test_refresh_token_type(self, client, test_user_data, create_test_user):
        """Test that refresh token has correct type."""
        create_test_user(test_user_data["email"], test_user_data["password"])
        
        response = client.post("/api/auth/login", json=test_user_data)
        assert response.status_code == 200
        
        refresh_token = response.json()["data"]["refresh_token"]
        
        # Decode token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["type"] == "refresh"
        assert "email" not in payload  # Refresh tokens should not contain email


class TestResponseMetadata:
    """Test cases for response metadata."""
    
    def test_metadata_in_all_responses(self, client, test_user_data):
        """Test that all successful responses include metadata."""
        # Register
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "metadata" in data
        assert data["metadata"]["version"] == "1.0.0"
        assert "timestamp" in data["metadata"]
        
        # Login
        response = client.post("/api/auth/login", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert data["metadata"]["version"] == "1.0.0"
        
        # Refresh
        refresh_token = response.json()["data"]["refresh_token"]
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert data["metadata"]["version"] == "1.0.0"
    
    def test_metadata_timestamp_format(self, client, test_user_data):
        """Test that metadata timestamp is in correct format."""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        
        timestamp = response.json()["metadata"]["timestamp"]
        # Should be able to parse as ISO format datetime
        parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert isinstance(parsed, datetime)


class TestPasswordSecurity:
    """Test cases for password security."""
    
    def test_password_hashing(self):
        """Test that password hashing works correctly."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Should verify correctly
        assert verify_password(password, hashed)
        
        # Should not verify with wrong password
        assert not verify_password("WrongPassword", hashed)
    
    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # Both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestDatabaseModels:
    """Test cases for database models and helper methods."""
    
    def test_user_created_at_default(self, test_db):
        """Test that user created_at has default value."""
        db = TestingSessionLocal()
        user = User.create_user(db, "test@example.com", hash_password("password"))
        
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
        db.close()
    
    def test_user_get_by_email(self, test_db):
        """Test User.get_by_email helper method."""
        db = TestingSessionLocal()
        email = "test@example.com"
        User.create_user(db, email, hash_password("password"))
        
        user = User.get_by_email(db, email)
        assert user is not None
        assert user.email == email
        
        # Test non-existent email
        user = User.get_by_email(db, "nonexistent@example.com")
        assert user is None
        db.close()
    
    def test_user_get_by_id(self, test_db):
        """Test User.get_by_id helper method."""
        db = TestingSessionLocal()
        user = User.create_user(db, "test@example.com", hash_password("password"))
        user_id = user.id
        
        found_user = User.get_by_id(db, user_id)
        assert found_user is not None
        assert found_user.id == user_id
        
        # Test non-existent id
        found_user = User.get_by_id(db, 99999)
        assert found_user is None
        db.close()
    
    def test_user_is_active_default(self, test_db):
        """Test that user is_active defaults to True."""
        db = TestingSessionLocal()
        user = User.create_user(db, "test@example.com", hash_password("password"))
        
        assert user.is_active is True
        db.close()


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_auth_flow(self, client):
        """Test complete authentication flow: register -> login -> refresh."""
        user_data = {
            "email": "e2e@example.com",
            "password": "SecurePassword123!"
        }
        
        # 1. Register
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        assert register_response.json()["success"] is True
        
        # 2. Login
        login_response = client.post("/api/auth/login", json=user_data)
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["success"] is True
        
        # 3. Refresh
        refresh_token = login_data["data"]["refresh_token"]
        refresh_response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        assert refresh_data["success"] is True
        
        # Tokens should be rotated
        new_refresh_token = refresh_data["data"]["refresh_token"]
        assert new_refresh_token != refresh_token
