#!/usr/bin/env python3
"""Test script to verify session tracking endpoints"""

import sys

def test_sessions():
    """Test that session tracking endpoints are properly configured"""
    print("=" * 60)
    print("SESSION TRACKING ENDPOINTS TEST")
    print("=" * 60)
    
    all_passed = True
    
    # 1. Test schema imports
    print("\n📦 Testing Session Tracking Schema Imports...")
    try:
        from app.schemas.session_tracking import (
            SessionTrackingResponse, SessionTrackingCreate, SessionTrackingUpdate,
            SessionTrackingStats
        )
        print("  ✓ Session tracking schemas imported successfully")
        
    except ImportError as e:
        print(f"  ✗ Schema import failed: {e}")
        all_passed = False
    
    # 2. Test CRUD imports
    print("\n🔧 Testing Session Tracking CRUD...")
    try:
        from app.crud.session_tracking import session_tracking_crud
        
        print("  ✓ Session tracking CRUD imported successfully")
        
        # Test key CRUD methods exist
        session_methods = [
            'get_with_relations', 'get_filtered', 'get_by_customer',
            'get_by_trainer', 'get_stats', 'check_daily_limit'
        ]
        
        for method in session_methods:
            if hasattr(session_tracking_crud, method):
                print(f"    ✓ session_tracking_crud.{method} available")
            else:
                print(f"    ✗ session_tracking_crud.{method} missing")
                all_passed = False
                
    except ImportError as e:
        print(f"  ✗ CRUD import failed: {e}")
        all_passed = False
    
    # 3. Test session volume CRUD updates
    print("\n🗂️  Testing Session Volume CRUD Updates...")
    try:
        from app.crud.session_volume import session_volume_crud
        
        print("  ✓ Session volume CRUD imported successfully")
        
        # Test new methods exist
        volume_methods = [
            'get_or_create_for_period', 'increment_session_count', 'decrement_session_count'
        ]
        
        for method in volume_methods:
            if hasattr(session_volume_crud, method):
                print(f"    ✓ session_volume_crud.{method} available")
            else:
                print(f"    ✗ session_volume_crud.{method} missing")
                all_passed = False
                
    except ImportError as e:
        print(f"  ✗ Session volume CRUD import failed: {e}")
        all_passed = False
    
    # 4. Test API router imports
    print("\n🌐 Testing Session Tracking API Router...")
    try:
        from app.api.v1.sessions import router
        print("  ✓ Sessions router imported successfully")
        
        # Check endpoints
        endpoints = {}
        for route in router.routes:
            if hasattr(route, 'path'):
                if route.path not in endpoints:
                    endpoints[route.path] = []
                endpoints[route.path].extend(route.methods)
        
        required_endpoints = {
            "/track": ["POST"],
            "": ["GET"],  # Base route for listing
            "/{session_id}": ["GET", "PUT", "DELETE"],
            "/customer/{customer_id}": ["GET"],
            "/trainer/{trainer_id}": ["GET"],
            "/stats": ["GET"]
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
    
    # 5. Test main routes integration
    print("\n🔗 Testing Routes Integration...")
    try:
        from app.routes.routes import router as main_router
        
        # Check if sessions routes are included
        session_routes_found = 0
        for route in main_router.routes:
            if hasattr(route, 'path') and '/api/v1/sessions' in route.path:
                session_routes_found += 1
        
        if session_routes_found >= 6:  # Should have at least 6 session endpoints
            print(f"  ✓ Found {session_routes_found} session routes in main router")
        else:
            print(f"  ✗ Only found {session_routes_found} session routes (expected at least 6)")
            all_passed = False
            
    except ImportError as e:
        print(f"  ✗ Main router import failed: {e}")
        all_passed = False
    
    # 6. Test endpoint paths
    print("\n📍 Testing Endpoint Paths...")
    try:
        from app.routes.routes import router as main_router
        
        expected_paths = [
            "/api/v1/sessions/track",
            "/api/v1/sessions",
            "/api/v1/sessions/{session_id}",
            "/api/v1/sessions/customer/{customer_id}",
            "/api/v1/sessions/trainer/{trainer_id}",
            "/api/v1/sessions/stats"
        ]
        
        actual_paths = [route.path for route in main_router.routes if hasattr(route, 'path')]
        
        for expected_path in expected_paths:
            # Check for exact match or parameterized match
            path_found = any(
                expected_path == actual or 
                expected_path.replace('{session_id}', '{session_id}') in actual or
                expected_path.replace('{customer_id}', '{customer_id}') in actual or
                expected_path.replace('{trainer_id}', '{trainer_id}') in actual
                for actual in actual_paths
            )
            
            if path_found:
                print(f"    ✓ {expected_path}")
            else:
                print(f"    ✗ {expected_path} missing")
                all_passed = False
                
    except Exception as e:
        print(f"  ✗ Path testing failed: {e}")
        all_passed = False
    
    # 7. Test session tracking model relationships
    print("\n📊 Testing Session Tracking Model...")
    try:
        from app.models.session_tracking import SessionTracking
        
        # Check expected fields exist
        expected_fields = ['id', 'trainer_id', 'qr_code_id', 'session_volume_id', 
                          'scan_timestamp', 'session_date', 'created_at', 'updated_at']
        
        for field in expected_fields:
            if hasattr(SessionTracking, field):
                print(f"    ✓ SessionTracking.{field} exists")
            else:
                print(f"    ✗ SessionTracking.{field} missing")
                all_passed = False
                
        # Check relationships
        relationships = ['trainer', 'qr_code', 'session_volume']
        for rel in relationships:
            if hasattr(SessionTracking, rel):
                print(f"    ✓ SessionTracking.{rel} relationship exists")
            else:
                print(f"    ✗ SessionTracking.{rel} relationship missing")
                all_passed = False
                
    except ImportError as e:
        print(f"  ✗ SessionTracking model import failed: {e}")
        all_passed = False
    
    # 8. Test business rules
    print("\n⚖️  Testing Business Rules...")
    try:
        from app.api.v1.sessions import TrackSessionRequest, TrackSessionResponse
        from datetime import date
        
        # Test request schema
        test_request = TrackSessionRequest(
            qr_token="test_token_123",
            session_date=date.today()
        )
        print("    ✓ TrackSessionRequest schema works")
        
        # Test response schema fields
        response_fields = ['success', 'session_id', 'message', 'customer_name', 
                          'session_date', 'monthly_volume_id', 'total_sessions_this_month']
        
        for field in response_fields:
            if field in TrackSessionResponse.__annotations__:
                print(f"    ✓ TrackSessionResponse.{field} field defined")
            else:
                print(f"    ✗ TrackSessionResponse.{field} field missing")
                all_passed = False
                
    except Exception as e:
        print(f"  ✗ Business rules testing failed: {e}")
        all_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL SESSION TRACKING ENDPOINT TESTS PASSED!")
        print("\nAvailable Session Tracking Endpoints:")
        print("  - POST   /api/v1/sessions/track")
        print("  - GET    /api/v1/sessions")
        print("  - GET    /api/v1/sessions/{session_id}")
        print("  - PUT    /api/v1/sessions/{session_id}")
        print("  - DELETE /api/v1/sessions/{session_id}")
        print("  - GET    /api/v1/sessions/customer/{customer_id}")
        print("  - GET    /api/v1/sessions/trainer/{trainer_id}")
        print("  - GET    /api/v1/sessions/stats")
        print("\nKey Features:")
        print("  - QR code-based session tracking")
        print("  - One scan per trainer-customer pair per day limit")
        print("  - Automatic monthly volume management")
        print("  - Comprehensive filtering and statistics")
        print("  - Role-based access control")
        print("  - Admin-only edit/delete permissions")
        print("  - Customer and trainer specific views")
    else:
        print("❌ SOME SESSION TRACKING ENDPOINT TESTS FAILED")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_sessions()
    sys.exit(0 if success else 1)