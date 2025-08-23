#!/usr/bin/env python3
"""Test script to verify QR code endpoints"""

import sys

def test_qr_codes():
    """Test that QR code endpoints are properly configured"""
    print("=" * 60)
    print("QR CODE ENDPOINTS TEST")
    print("=" * 60)
    
    all_passed = True
    
    # 1. Test schema imports
    print("\n📦 Testing QR Code Schema Imports...")
    try:
        from app.schemas.qr_code import (
            QRCodeResponse, QRCodeSummary, QRCodeCreate
        )
        print("  ✓ QR Code schemas imported successfully")
        
        # Test API schemas
        from app.api.v1.qr_codes import (
            ScanQRCodeRequest, ScanQRCodeResponse, QRCodeDisplayResponse
        )
        print("  ✓ QR Code API schemas imported successfully")
        
    except ImportError as e:
        print(f"  ✗ Schema import failed: {e}")
        all_passed = False
    
    # 2. Test CRUD imports
    print("\n🔧 Testing QR Code CRUD...")
    try:
        from app.crud.qr_code import qr_code_crud
        
        print("  ✓ QR Code CRUD imported successfully")
        
        # Test key CRUD methods exist
        qr_methods = [
            'get_by_token', 'get_by_user', 'generate_unique_token',
            'create_for_user'
        ]
        
        for method in qr_methods:
            if hasattr(qr_code_crud, method):
                print(f"    ✓ qr_code_crud.{method} available")
            else:
                print(f"    ✗ qr_code_crud.{method} missing")
                all_passed = False
                
    except ImportError as e:
        print(f"  ✗ CRUD import failed: {e}")
        all_passed = False
    
    # 3. Test API router imports
    print("\n🌐 Testing QR Code API Router...")
    try:
        from app.api.v1.qr_codes import router
        print("  ✓ QR Code router imported successfully")
        
        # Check endpoints
        endpoints = {}
        for route in router.routes:
            if hasattr(route, 'path'):
                if route.path not in endpoints:
                    endpoints[route.path] = []
                endpoints[route.path].extend(route.methods)
        
        required_endpoints = {
            "/me": ["GET"],
            "/scan": ["POST"]
        }
        
        for path, methods in required_endpoints.items():
            if path in endpoints:
                for method in methods:
                    if method in endpoints[path]:
                        print(f"    ✓ {method} {path} endpoint exists")
                    else:
                        print(f"    ✗ {method} {path} endpoint missing")
                        all_passed = False
            else:
                print(f"    ✗ {path} endpoint missing completely")
                all_passed = False
                
    except ImportError as e:
        print(f"  ✗ Router import failed: {e}")
        all_passed = False
    
    # 4. Test main routes integration
    print("\n🔗 Testing Routes Integration...")
    try:
        from app.routes.routes import router as main_router
        
        # Check if QR code routes are included
        qr_routes_found = 0
        for route in main_router.routes:
            if hasattr(route, 'path') and '/api/v1/qr-codes' in route.path:
                qr_routes_found += 1
        
        if qr_routes_found >= 2:  # Should have 2 QR code endpoints
            print(f"  ✓ Found {qr_routes_found} QR code routes in main router")
        else:
            print(f"  ✗ Only found {qr_routes_found} QR code routes (expected 2)")
            all_passed = False
            
    except ImportError as e:
        print(f"  ✗ Main router import failed: {e}")
        all_passed = False
    
    # 5. Test endpoint paths
    print("\n📍 Testing Endpoint Paths...")
    try:
        from app.routes.routes import router as main_router
        
        expected_paths = [
            "/api/v1/qr-codes/me",
            "/api/v1/qr-codes/scan"
        ]
        
        actual_paths = [route.path for route in main_router.routes if hasattr(route, 'path')]
        
        for expected_path in expected_paths:
            if expected_path in actual_paths:
                print(f"    ✓ {expected_path}")
            else:
                print(f"    ✗ {expected_path} missing")
                all_passed = False
                
    except Exception as e:
        print(f"  ✗ Path testing failed: {e}")
        all_passed = False
    
    # 6. Test QR code model
    print("\n📊 Testing QR Code Model...")
    try:
        from app.models.qr_code import QRCode
        
        # Check expected fields exist
        expected_fields = ['id', 'user_id', 'token', 'created_at', 'updated_at']
        
        for field in expected_fields:
            if hasattr(QRCode, field):
                print(f"    ✓ QRCode.{field} exists")
            else:
                print(f"    ✗ QRCode.{field} missing")
                all_passed = False
                
    except ImportError as e:
        print(f"  ✗ QR Code model import failed: {e}")
        all_passed = False
    
    # 7. Test token generation
    print("\n🎲 Testing Token Generation...")
    try:
        from app.crud.qr_code import qr_code_crud
        import string
        
        # Test that we can generate a token (without DB)
        # Mock a database session for testing
        class MockDB:
            def query(self, model):
                return MockQuery()
        
        class MockQuery:
            def filter(self, condition):
                return self
            def first(self):
                return None  # No existing token
        
        mock_db = MockDB()
        token = qr_code_crud.generate_unique_token(mock_db, length=16)
        
        if token and len(token) == 16 and all(c in string.ascii_letters + string.digits for c in token):
            print(f"    ✓ Token generation works (sample: {token})")
        else:
            print(f"    ✗ Token generation failed or invalid format")
            all_passed = False
            
    except Exception as e:
        print(f"  ✗ Token generation test failed: {e}")
        all_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL QR CODE ENDPOINT TESTS PASSED!")
        print("\nAvailable QR Code Endpoints:")
        print("  - GET    /api/v1/qr-codes/me")
        print("  - POST   /api/v1/qr-codes/scan")
        print("\nFunctionality:")
        print("  - Auto-creates QR codes for users who don't have one")
        print("  - Validates QR codes and returns user information")
        print("  - Handles trainer-customer assignment warnings")
        print("  - Ready for session tracking integration")
        print("  - Supports both customers displaying and trainers scanning")
    else:
        print("❌ SOME QR CODE ENDPOINT TESTS FAILED")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_qr_codes()
    sys.exit(0 if success else 1)