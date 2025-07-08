#!/usr/bin/env python3
"""
Clean up sensitive data from notebook files before git push
"""

import os
import json
import re
from pathlib import Path

def clean_notebook(notebook_path):
    """Clean sensitive data from a Jupyter notebook"""
    print(f"🔍 Cleaning: {notebook_path}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_data = json.load(f)
    
    changes_made = False
    
    for cell in notebook_data.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            new_source = []
            
            for line in source:
                # Remove lines with actual API keys
                if re.search(r'sk-[A-Za-z0-9]{40,}', line):
                    new_source.append('# API key removed for security\n')
                    changes_made = True
                    print(f"  ⚠️  Removed API key from line: {line.strip()[:50]}...")
                
                # Replace actual API keys with placeholder
                elif '"sk-' in line and len(line) > 20:
                    cleaned_line = re.sub(r'"sk-[A-Za-z0-9]{40,}"', '"YOUR_API_KEY_HERE"', line)
                    if cleaned_line != line:
                        changes_made = True
                        print(f"  🔄 Replaced API key in line")
                    new_source.append(cleaned_line)
                
                # Replace actual API keys with placeholder (single quotes)
                elif "'sk-" in line and len(line) > 20:
                    cleaned_line = re.sub(r"'sk-[A-Za-z0-9]{40,}'", "'YOUR_API_KEY_HERE'", line)
                    if cleaned_line != line:
                        changes_made = True
                        print(f"  🔄 Replaced API key in line")
                    new_source.append(cleaned_line)
                
                else:
                    new_source.append(line)
            
            cell['source'] = new_source
    
    if changes_made:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook_data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Updated: {notebook_path}")
        return True
    else:
        print(f"  ✨ Clean: {notebook_path}")
        return False

def main():
    """Clean all notebooks in the experiments directory"""
    print("🚀 Cleaning Notebooks for Git Push")
    print("=" * 50)
    
    experiments_dir = Path(__file__).parent / "experiments"
    
    if not experiments_dir.exists():
        print(f"❌ Directory not found: {experiments_dir}")
        return
    
    notebooks = list(experiments_dir.glob("*.ipynb"))
    
    if not notebooks:
        print("📝 No notebooks found")
        return
    
    total_changes = 0
    
    for notebook in notebooks:
        if clean_notebook(notebook):
            total_changes += 1
    
    print(f"\n🎯 Summary: {total_changes} notebooks updated")
    
    if total_changes > 0:
        print("💡 Don't forget to commit these changes before pushing!")
    else:
        print("✅ All notebooks are clean!")

if __name__ == "__main__":
    main()
