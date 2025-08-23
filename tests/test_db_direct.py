#!/usr/bin/env python3
import psycopg2
import sys
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("Testing database connection...")
print(f"DATABASE_URL from env: {os.getenv('DATABASE_URL')}")

try:
    conn = psycopg2.connect(
        host='localhost',
        database='bodyback_db',
        user='postgres',
        password='25thBaam',
        port=5432
    )
    print('✅ Direct connection successful!')
    
    # Test a simple query
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    print(f'PostgreSQL version: {version[0]}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Connection failed: {e}')
    sys.exit(1)