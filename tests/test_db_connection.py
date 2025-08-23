#!/usr/bin/env python3
"""
Database connection test script
Run this to verify your PostgreSQL connection is working
"""

import sys
from sqlalchemy import text
from app.core.database import engine, create_tables
from app.core.config import settings

def test_basic_connection():
    """Test basic database connection"""
    print("🔗 Testing basic database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📊 PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_database_info():
    """Get database information"""
    print("\n📋 Database configuration:")
    print(f"   URL: {settings.DATABASE_URL}")
    print(f"   Pool size: {settings.DB_POOL_SIZE}")
    print(f"   Max overflow: {settings.DB_MAX_OVERFLOW}")

def test_table_creation():
    """Test table creation"""
    print("\n🏗️  Testing table creation...")
    try:
        create_tables()
        print("✅ Tables created/verified successfully!")
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

def test_table_existence():
    """Check if our tables exist"""
    print("\n📊 Checking table existence...")
    tables_to_check = ['users', 'roles', 'user_roles', 'customers', 'trainers']
    
    try:
        with engine.connect() as conn:
            for table in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """))
                exists = result.fetchone()[0]
                status = "✅" if exists else "❌"
                print(f"   {status} Table '{table}': {'exists' if exists else 'missing'}")
        return True
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def test_basic_operations():
    """Test basic database operations"""
    print("\n🧪 Testing basic operations...")
    try:
        with engine.connect() as conn:
            # Test counting records
            result = conn.execute(text("SELECT COUNT(*) FROM roles"))
            role_count = result.fetchone()[0]
            print(f"   📊 Roles in database: {role_count}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"   📊 Users in database: {user_count}")
            
            # Test if basic roles exist
            result = conn.execute(text("SELECT name FROM roles ORDER BY name"))
            roles = [row[0] for row in result.fetchall()]
            if roles:
                print(f"   📋 Available roles: {', '.join(roles)}")
            else:
                print("   ⚠️  No roles found in database")
            
        print("✅ Basic operations successful!")
        return True
    except Exception as e:
        print(f"❌ Basic operations failed: {e}")
        return False

def main():
    """Run all connection tests"""
    print("🚀 BodyBack FastAPI Database Connection Test")
    print("=" * 50)
    
    test_database_info()
    
    # Run tests in sequence
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Table Creation", test_table_creation),
        ("Table Existence", test_table_existence),
        ("Basic Operations", test_basic_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your database connection is working perfectly!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check your database configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())