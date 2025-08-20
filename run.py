#!/usr/bin/env python3
"""
Simple test script to verify HEBNORM project structure
"""

import os
import sys

def check_project_structure():
    """Check if all required files and directories exist"""
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/config.py',
        'app/routes/__init__.py',
        'app/routes/nikud.py',
        'app/routes/normalize.py',
        'app/routes/spellcheck.py',
        'app/utils/__init__.py',
        'app/utils/nikud.py',
        'app/utils/normalizer.py',
        'app/utils/spellcheck.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        'README.md',
        'LICENSE',
        '.gitignore'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files exist!")
        return True

def check_imports():
    """Check if basic imports work"""
    try:
        sys.path.append('.')
        from app.config import settings
        print("✅ Config import successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking HEBNORM project structure...")
    print()
    
    structure_ok = check_project_structure()
    print()
    
    if structure_ok:
        print("🔍 Checking basic imports...")
        imports_ok = check_imports()
        print()
        
        if imports_ok:
            print("🎉 HEBNORM project is ready!")
            print()
            print("To run the project:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Run with uvicorn: uvicorn app.main:app --reload")
            print("3. Or use Docker: docker-compose up --build")
            print()
            print("API endpoints:")
            print("   - Root: /")
            print("   - Health: /health")
            print("   - API v1: /api/v1/*")
        else:
            print("⚠️  Some imports failed. Check your Python environment.")
    else:
        print("⚠️  Project structure incomplete. Check missing files.")
