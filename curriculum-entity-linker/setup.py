#!/usr/bin/env python3
"""
Setup script for Curriculum Entity Linker
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file from example"""
    env_example = os.path.join(os.path.dirname(__file__), '.env.example')
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    if not os.path.exists(env_example):
        print("❌ .env.example not found")
        return False
    
    try:
        with open(env_example, 'r') as src:
            content = src.read()
        
        with open(env_file, 'w') as dst:
            dst.write(content)
        
        print("✅ Created .env file from .env.example")
        print("⚠️  Please update .env file with your Neo4j credentials")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_curriculum_file():
    """Check if curriculum CQL file exists"""
    cql_file = os.path.join(os.path.dirname(__file__), '..', 'curriculum-syllabus-example.cql')
    
    if os.path.exists(cql_file):
        print("✅ Curriculum CQL file found")
        return True
    else:
        print("❌ Curriculum CQL file not found")
        print(f"   Expected: {cql_file}")
        return False

def main():
    """Setup process"""
    print("Curriculum Entity Linker - Setup")
    print("=" * 40)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Create .env file
    if not create_env_file():
        success = False
    
    # Check curriculum file
    if not check_curriculum_file():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your Neo4j credentials")
        print("2. Run: python test_linker.py")
        print("3. Run: python curriculum_linker.py")
    else:
        print("❌ Setup failed! Please check the errors above.")

if __name__ == "__main__":
    main()
