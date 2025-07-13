#!/usr/bin/env python3
"""
Quick test for help command without dependencies
"""

import sys

def show_help():
    print("""
Curriculum Entity Linker - Usage:

python curriculum_linker.py              # Normal mode: Link only new documents
python curriculum_linker.py --force      # Force mode: Relink ALL documents  
python curriculum_linker.py --status     # Status mode: Show linking statistics only

Options:
  --force, -f     Force relink all documents (including already linked)
  --status, -s    Show linking status only (no processing)
  --help, -h      Show this help message

Examples:
  python curriculum_linker.py                    # Link chỉ documents mới
  python curriculum_linker.py --status           # Xem thống kê hiện tại
  python curriculum_linker.py --force            # Link lại tất cả
  python auto_linker.py                          # Monitor mode
  python auto_linker.py CMP170                   # Link specific course
    """)

if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv or len(sys.argv) == 1:
        show_help()
    else:
        print("✅ Command parsed successfully!")
        print("Args:", sys.argv[1:])
