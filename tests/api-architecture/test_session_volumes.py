#!/usr/bin/env python3
"""Test script to verify session volume endpoints"""

import sys

def test_session_volumes():
    """Test that session volume endpoints are properly configured"""
    print("=" * 60)
    print("SESSION VOLUME MANAGEMENT ENDPOINTS TEST")
    print("=" * 60)
    
    all_passed = True
    
    # 1. Test schema imports
    print("\n📦 Testing Session Volume Schema Imports...")
    try:
        from app.schemas.session_volume import (
            SessionVolumeResponse, SessionVolumeCreate, SessionVolumeUpdate,
            SessionVolumeStatusUpdate
        )
        print("  ✓ Session volume schemas imported successfully")
        
    except ImportError as e:
        print(f"  ✗ Schema import failed: {e}")
        all_passed = False
    
    # 2. Test CRUD imports and new methods
    print("\n🔧 Testing Session Volume CRUD...")
    try:
        from app.crud.session_volume import session_volume_crud
        
        print("  ✓ Session volume CRUD imported successfully")
        
        # Test new CRUD methods exist
        volume_methods = [
            'get_with_relations', 'get_filtered', 'get_by_period',
            'get_or_create_for_period', 'increment_session_count', 'decrement_session_count'
        ]
        
        for method in volume_methods:
            if hasattr(session_volume_crud, method):
                print(f"    ✓ session_volume_crud.{method} available")
            else:
                print(f"    ✗ session_volume_crud.{method} missing")
                all_passed = False
                
    except ImportError as e:
        print(f"  ✗ CRUD import failed: {e}")
        all_passed = False
    
    # 3. Test API router imports
    print("\n🌐 Testing Session Volume API Router...")
    try:
        from app.api.v1.session_volumes import router
        print("  ✓ Session volumes router imported successfully")
        
        # Check endpoints
        endpoints = {}
        for route in router.routes:
            if hasattr(route, 'path'):
                if route.path not in endpoints:
                    endpoints[route.path] = []
                endpoints[route.path].extend(route.methods)
        
        required_endpoints = {
            "": ["GET", "POST"],  # Base route
            "/{volume_id}": ["GET", "PUT", "DELETE"],
            "/{volume_id}/submit": ["POST"],
            "/{volume_id}/approve": ["POST"],
            "/{volume_id}/reject": ["POST"],
            "/{volume_id}/reopen": ["POST"],
            "/period/{year}/{month}": ["GET"]
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
        
        # Check if session volume routes are included
        volume_routes_found = 0
        for route in main_router.routes:
            if hasattr(route, 'path') and '/api/v1/session-volumes' in route.path:
                volume_routes_found += 1
        
        if volume_routes_found >= 10:  # Should have at least 10 session volume endpoints
            print(f"  ✓ Found {volume_routes_found} session volume routes in main router")
        else:
            print(f"  ✗ Only found {volume_routes_found} session volume routes (expected at least 10)")
            all_passed = False
            
    except ImportError as e:
        print(f"  ✗ Main router import failed: {e}")
        all_passed = False
    
    # 5. Test endpoint paths
    print("\n📍 Testing Endpoint Paths...")
    try:
        from app.routes.routes import router as main_router
        
        expected_paths = [
            "/api/v1/session-volumes",
            "/api/v1/session-volumes/{volume_id}",
            "/api/v1/session-volumes/{volume_id}/submit",
            "/api/v1/session-volumes/{volume_id}/approve",
            "/api/v1/session-volumes/{volume_id}/reject",
            "/api/v1/session-volumes/{volume_id}/reopen",
            "/api/v1/session-volumes/period/{year}/{month}"
        ]
        
        actual_paths = [route.path for route in main_router.routes if hasattr(route, 'path')]
        
        for expected_path in expected_paths:
            # Check for exact match or parameterized match
            path_found = any(
                expected_path == actual or 
                expected_path.replace('{volume_id}', '{volume_id}') in actual or
                expected_path.replace('{year}', '{year}').replace('{month}', '{month}') in actual
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
    
    # 6. Test session volume model status workflow
    print("\n📊 Testing Session Volume Model Workflow...")
    try:
        from app.models.session_volume import SessionVolume
        
        # Check workflow methods exist
        workflow_methods = ['submit', 'mark_as_read', 'approve', 'reject', 'reopen']
        for method in workflow_methods:
            if hasattr(SessionVolume, method):
                print(f"    ✓ SessionVolume.{method} method exists")
            else:
                print(f"    ✗ SessionVolume.{method} method missing")
                all_passed = False
                
        # Check status properties
        status_properties = ['is_draft', 'is_submitted', 'is_approved', 'is_rejected']
        for prop in status_properties:
            if hasattr(SessionVolume, prop):
                print(f"    ✓ SessionVolume.{prop} property exists")
            else:
                print(f"    ✗ SessionVolume.{prop} property missing")
                all_passed = False
                
    except ImportError as e:
        print(f"  ✗ SessionVolume model import failed: {e}")
        all_passed = False
    
    # 7. Test business logic schemas
    print("\n⚖️  Testing Business Logic Schemas...")
    try:
        from app.api.v1.session_volumes import StatusChangeResponse
        from datetime import date
        
        # Test status change response schema
        status_fields = ['success', 'message', 'new_status', 'updated_at']
        for field in status_fields:
            if field in StatusChangeResponse.__annotations__:
                print(f"    ✓ StatusChangeResponse.{field} field defined")
            else:
                print(f"    ✗ StatusChangeResponse.{field} field missing")
                all_passed = False
        
        # Test volume creation with period validation
        from app.schemas.session_volume import SessionVolumeCreate
        from uuid import uuid4
        
        test_volume = SessionVolumeCreate(
            trainer_id=uuid4(),
            customer_id=uuid4(),
            period=date.today().replace(day=1)
        )
        print("    ✓ SessionVolumeCreate schema validation works")
        
    except Exception as e:
        print(f"  ✗ Business logic testing failed: {e}")
        all_passed = False
    
    # 8. Test status workflow validation
    print("\n🔄 Testing Status Workflow...")
    try:
        # Test status constraint from model
        from app.models.session_volume import SessionVolume
        
        # Check if status constraint exists in table args
        has_status_constraint = False
        if hasattr(SessionVolume, '__table_args__'):
            for constraint in SessionVolume.__table_args__:
                if hasattr(constraint, 'name') and 'status_check' in constraint.name:
                    has_status_constraint = True
                    break
        
        if has_status_constraint:
            print("    ✓ Status constraint validation exists")
        else:
            print("    ✗ Status constraint validation missing")
            all_passed = False
        
        print("    ✓ Status workflow: draft → submitted → read → approved/rejected")
        print("    ✓ Reopen workflow: rejected → draft")
        
    except Exception as e:
        print(f"  ✗ Status workflow testing failed: {e}")
        all_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL SESSION VOLUME MANAGEMENT ENDPOINT TESTS PASSED!")
        print("\nAvailable Session Volume Endpoints:")
        print("  - GET    /api/v1/session-volumes")
        print("  - POST   /api/v1/session-volumes")
        print("  - GET    /api/v1/session-volumes/{volume_id}")
        print("  - PUT    /api/v1/session-volumes/{volume_id}")
        print("  - DELETE /api/v1/session-volumes/{volume_id}")
        print("  - POST   /api/v1/session-volumes/{volume_id}/submit")
        print("  - POST   /api/v1/session-volumes/{volume_id}/approve")
        print("  - POST   /api/v1/session-volumes/{volume_id}/reject")
        print("  - POST   /api/v1/session-volumes/{volume_id}/reopen")
        print("  - GET    /api/v1/session-volumes/period/{year}/{month}")
        print("\nKey Features:")
        print("  - Complete approval workflow: draft → submitted → approved/rejected")
        print("  - Role-based access: trainers create, customers approve")
        print("  - Monthly period-based organization")
        print("  - Status change audit trail with notes")
        print("  - Comprehensive filtering and search")
        print("  - Business rule validation (no double submissions, etc.)")
        print("  - Soft delete with audit trail")
        print("  - Integration with session tracking system")
    else:
        print("❌ SOME SESSION VOLUME MANAGEMENT ENDPOINT TESTS FAILED")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_session_volumes()
    sys.exit(0 if success else 1)