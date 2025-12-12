#!/usr/bin/env python3
"""
Verification script to ensure all components of the auth API are properly implemented.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def check_imports():
    """Verify all modules can be imported."""
    print("Checking module imports...")
    try:
        from app import models, schemas, security, database, redis_client
        from app.routers import auth
        from app import main
        print("✓ All modules import successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def check_endpoints():
    """Verify all required endpoints are defined."""
    print("\nChecking endpoint definitions...")
    from app.routers import auth
    
    endpoints = [r.path for r in auth.router.routes]
    required_endpoints = [
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/refresh"
    ]
    
    all_present = True
    for endpoint in required_endpoints:
        if endpoint in endpoints:
            print(f"✓ {endpoint} defined")
        else:
            print(f"✗ {endpoint} missing")
            all_present = False
    
    return all_present


def check_security_functions():
    """Verify security functions are implemented."""
    print("\nChecking security functions...")
    from app import security
    
    required_functions = [
        'hash_password',
        'verify_password',
        'create_access_token',
        'create_refresh_token',
        'verify_token',
        'generate_token_fingerprint',
        'check_rate_limit',
        'store_refresh_token_fingerprint',
        'verify_refresh_token_fingerprint',
    ]
    
    all_present = True
    for func_name in required_functions:
        if hasattr(security, func_name):
            print(f"✓ {func_name} implemented")
        else:
            print(f"✗ {func_name} missing")
            all_present = False
    
    return all_present


def check_models():
    """Verify database models are properly defined."""
    print("\nChecking database models...")
    from app.models import User
    
    required_fields = ['id', 'email', 'hashed_password', 'is_active', 'created_at']
    required_methods = ['get_by_email', 'get_by_id', 'create_user']
    
    all_present = True
    
    # Check fields
    for field in required_fields:
        if hasattr(User, field):
            print(f"✓ User.{field} defined")
        else:
            print(f"✗ User.{field} missing")
            all_present = False
    
    # Check methods
    for method in required_methods:
        if hasattr(User, method):
            print(f"✓ User.{method} implemented")
        else:
            print(f"✗ User.{method} missing")
            all_present = False
    
    return all_present


def check_schemas():
    """Verify Pydantic schemas are properly defined."""
    print("\nChecking Pydantic schemas...")
    from app import schemas
    
    required_schemas = [
        'ResponseMetadata',
        'RegisterRequest',
        'LoginRequest',
        'RefreshRequest',
        'TokenResponse',
        'AuthResponse',
    ]
    
    all_present = True
    for schema_name in required_schemas:
        if hasattr(schemas, schema_name):
            print(f"✓ {schema_name} defined")
        else:
            print(f"✗ {schema_name} missing")
            all_present = False
    
    return all_present


def check_password_security():
    """Verify password hashing works correctly."""
    print("\nChecking password security...")
    from app.security import hash_password, verify_password
    
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    # Verify password is hashed
    if hashed != password:
        print("✓ Password is hashed (not stored in plain text)")
    else:
        print("✗ Password not hashed properly")
        return False
    
    # Verify password verification works
    if verify_password(password, hashed):
        print("✓ Password verification works")
    else:
        print("✗ Password verification failed")
        return False
    
    # Verify wrong password fails
    if not verify_password("WrongPassword", hashed):
        print("✓ Wrong password correctly rejected")
    else:
        print("✗ Wrong password accepted (security issue!)")
        return False
    
    return True


def check_token_generation():
    """Verify JWT token generation works."""
    print("\nChecking JWT token generation...")
    from app.security import create_access_token, create_refresh_token, verify_token
    
    user_data = {"sub": "1", "email": "test@example.com"}
    
    # Create access token
    access_token = create_access_token(user_data)
    if access_token:
        print("✓ Access token created")
    else:
        print("✗ Failed to create access token")
        return False
    
    # Create refresh token
    refresh_token = create_refresh_token({"sub": "1"})
    if refresh_token:
        print("✓ Refresh token created")
    else:
        print("✗ Failed to create refresh token")
        return False
    
    # Verify access token
    payload = verify_token(access_token, expected_type="access")
    if payload and payload.get("type") == "access":
        print("✓ Access token verified")
    else:
        print("✗ Access token verification failed")
        return False
    
    # Verify refresh token
    payload = verify_token(refresh_token, expected_type="refresh")
    if payload and payload.get("type") == "refresh":
        print("✓ Refresh token verified")
    else:
        print("✗ Refresh token verification failed")
        return False
    
    # Verify tokens are unique (have JTI)
    access_token2 = create_access_token(user_data)
    if access_token != access_token2:
        print("✓ Tokens have unique identifiers (JTI)")
    else:
        print("✗ Tokens are not unique")
        return False
    
    return True


def check_metadata():
    """Verify response metadata is included."""
    print("\nChecking response metadata...")
    from app.schemas import ResponseMetadata
    
    metadata = ResponseMetadata()
    
    if hasattr(metadata, 'version') and metadata.version:
        print(f"✓ Metadata version: {metadata.version}")
    else:
        print("✗ Metadata version missing")
        return False
    
    if hasattr(metadata, 'timestamp') and metadata.timestamp:
        print(f"✓ Metadata timestamp present")
    else:
        print("✗ Metadata timestamp missing")
        return False
    
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("AUTH API IMPLEMENTATION VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Module Imports", check_imports),
        ("Endpoint Definitions", check_endpoints),
        ("Security Functions", check_security_functions),
        ("Database Models", check_models),
        ("Pydantic Schemas", check_schemas),
        ("Password Security", check_password_security),
        ("Token Generation", check_token_generation),
        ("Response Metadata", check_metadata),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Implementation is complete!")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please review the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
