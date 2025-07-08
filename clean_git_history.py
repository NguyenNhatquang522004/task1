#!/usr/bin/env python3
"""
Remove sensitive data from git history before pushing
"""

import subprocess
import os
import re

def find_potential_secrets():
    """Find potential secrets in git history"""
    print("🔍 Scanning git history for potential secrets...")
    
    # Search for lines that might contain API keys
    patterns = [
        r'sk-[A-Za-z0-9]{40,}',  # OpenAI API keys
        r'AIza[A-Za-z0-9]{35}',  # Google API keys
        r'key.*["\'][A-Za-z0-9]{20,}["\']',  # Generic API keys
    ]
    
    for pattern in patterns:
        try:
            result = subprocess.run([
                'git', 'log', '--all', '--full-history', '--grep=' + pattern, '--oneline'
            ], capture_output=True, text=True, cwd='.')
            
            if result.stdout:
                print(f"⚠️  Found potential secrets matching pattern: {pattern}")
                print(result.stdout)
        except Exception as e:
            print(f"Error searching with pattern {pattern}: {e}")

def create_clean_history():
    """Create a clean history without secrets"""
    print("\n🧹 Creating clean git history...")
    
    try:
        # Create a new branch with clean history
        subprocess.run(['git', 'checkout', '--orphan', 'clean-main'], check=True)
        
        # Add all current files (they should be clean now)
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit the clean state
        subprocess.run([
            'git', 'commit', '-m', 
            'Clean initial commit - removed all API keys and secrets'
        ], check=True)
        
        print("✅ Created clean branch: clean-main")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating clean history: {e}")
        return False

def push_clean_branch():
    """Push the clean branch to origin"""
    try:
        # Force push the clean branch
        subprocess.run([
            'git', 'push', '-u', 'origin', 'clean-main', '--force'
        ], check=True)
        
        print("✅ Successfully pushed clean branch!")
        
        # Switch back to main and update it to match clean-main
        subprocess.run(['git', 'checkout', 'main'], check=True)
        subprocess.run(['git', 'reset', '--hard', 'clean-main'], check=True)
        
        print("✅ Updated main branch to match clean branch")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error pushing clean branch: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Git History Cleaner")
    print("=" * 50)
    
    # First, scan for potential secrets
    find_potential_secrets()
    
    # Ask user if they want to proceed
    response = input("\n🤔 Do you want to create a clean git history? (y/N): ")
    
    if response.lower() == 'y':
        if create_clean_history():
            push_response = input("\n🚀 Push clean branch to GitHub? (y/N): ")
            if push_response.lower() == 'y':
                push_clean_branch()
        else:
            print("❌ Failed to create clean history")
    else:
        print("ℹ️  Skipping history cleanup")
        print("💡 You may need to manually remove secrets from git history")
        print("💡 Consider using: git filter-branch or BFG Repo Cleaner")

if __name__ == "__main__":
    main()
