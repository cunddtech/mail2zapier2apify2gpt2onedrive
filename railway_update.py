#!/usr/bin/env python3
"""
Quick Railway Update Script - Deploy only the fixed orchestrator
"""

import os
import sys
from pathlib import Path

# Copy just the fixed file to a clean directory
def create_clean_deploy():
    clean_dir = Path("railway_deploy_clean")
    clean_dir.mkdir(exist_ok=True)
    
    # Copy only essential files without secrets
    files_to_copy = [
        "production_langgraph_orchestrator.py",
        "requirements.txt",
        "Dockerfile"
    ]
    
    for file_name in files_to_copy:
        src = Path(file_name)
        if src.exists():
            dst = clean_dir / file_name
            dst.write_text(src.read_text())
            print(f"✅ Copied {file_name}")
        else:
            print(f"⚠️ Missing {file_name}")
    
    print(f"🚀 Clean deploy directory created: {clean_dir}")

if __name__ == "__main__":
    create_clean_deploy()