#!/usr/bin/env python3
"""
Generate top-level project files for EmberLearn.
"""

import os
from pathlib import Path

ROOT_FILES = {
    "package.json": """{
  "name": "emberlearn",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "setup": "bash setup.sh",
    "start": "bash start.sh"
  }
}
""",
    ".gitignore": """node_modules/
venv/
.venv/
__pycache__/
.next/
.env
*.db
""",
    # ... more files
}

def main():
    print("Generating root project files...")
    
    for filename, content in ROOT_FILES.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Generated {filename}")
    
    print("✓ Root files generation complete.")

if __name__ == "__main__":
    main()
