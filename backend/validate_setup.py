#!/usr/bin/env python3
"""
Validate EmberLearn backend setup
Checks dependencies, configuration, and database connectivity
"""

import sys
import importlib
from pathlib import Path

# Colors for terminal output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def check_python_version():
    """Check Python version is 3.11+"""
    print(f"{BLUE}[1/5] Checking Python version...{NC}")
    version = sys.version_info
    if version.major > 3 or (version.major == 3 and version.minor >= 11):
        print(f"{GREEN}✓ Python {version.major}.{version.minor}.{version.micro}{NC}")
        return True
    else:
        print(f"{RED}✗ Python 3.11+ required (found {version.major}.{version.minor}){NC}")
        return False

def check_dependencies():
    """Check all required packages are installed"""
    print(f"{BLUE}[2/5] Checking dependencies...{NC}")

    required_packages = {
        'fastapi': 'FastAPI',
        'sqlalchemy': 'SQLAlchemy',
        'pydantic': 'Pydantic',
        'pydantic_settings': 'Pydantic Settings',
        'passlib': 'Passlib',
        'python_jose': 'PyJOSE',
        'openai': 'OpenAI',
        'structlog': 'Structlog',
        'aiosqlite': 'aiosqlite',
    }

    all_ok = True
    for package, name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"  {GREEN}✓{NC} {name}")
        except ImportError:
            print(f"  {RED}✗{NC} {name} - Run 'pip install -r requirements.txt'")
            all_ok = False

    return all_ok

def check_config():
    """Check configuration files"""
    print(f"{BLUE}[3/5] Checking configuration...{NC}")

    config_files = {
        '.env': 'Backend environment',
        'app/config.py': 'Configuration module',
        'app/models.py': 'Database models',
        'app/agents.py': 'Agent implementations',
    }

    all_ok = True
    for file_path, name in config_files.items():
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"  {GREEN}✓{NC} {name}")
        else:
            print(f"  {RED}✗{NC} {name} - Missing {file_path}")
            all_ok = False

    return all_ok

def check_config_values():
    """Check configuration values"""
    print(f"{BLUE}[4/5] Checking configuration values...{NC}")

    try:
        from app.config import settings

        checks = [
            ('DATABASE_URL', settings.database_url),
            ('JWT_SECRET_KEY', '***' if settings.jwt_secret_key else 'NOT SET'),
            ('OPENAI_MODEL', settings.openai_model),
            ('CORS_ORIGINS', ','.join(settings.cors_origins)),
        ]

        all_ok = True
        for name, value in checks:
            if value and value != 'NOT SET':
                print(f"  {GREEN}✓{NC} {name}: {value}")
            else:
                print(f"  {YELLOW}⚠{NC}  {name}: {value}")

        return all_ok
    except Exception as e:
        print(f"  {RED}✗{NC} Failed to load configuration: {e}")
        return False

def check_database():
    """Check database connectivity"""
    print(f"{BLUE}[5/5] Checking database...{NC}")

    try:
        from app.config import settings
        db_path = settings.database_url.replace('sqlite:///', '')

        if 'sqlite' in settings.database_url:
            print(f"  {GREEN}✓{NC} Database type: SQLite")
            print(f"  {GREEN}✓{NC} Database file: {db_path}")
            print(f"  {YELLOW}ℹ{NC}  Run 'python main.py' to initialize tables")
        else:
            print(f"  {GREEN}✓{NC} Database type: {settings.database_url.split('://')[0]}")

        return True
    except Exception as e:
        print(f"  {RED}✗{NC} Database check failed: {e}")
        return False

def main():
    """Run all validation checks"""
    print(f"\n{BLUE}{'='*50}{NC}")
    print(f"{BLUE}EmberLearn Backend Setup Validation{NC}")
    print(f"{BLUE}{'='*50}{NC}\n")

    checks = [
        check_python_version(),
        check_dependencies(),
        check_config(),
        check_config_values(),
        check_database(),
    ]

    print(f"\n{BLUE}{'='*50}{NC}")
    if all(checks):
        print(f"{GREEN}✓ All checks passed!{NC}")
        print(f"{BLUE}{'='*50}{NC}\n")
        print(f"{YELLOW}Next steps:{NC}")
        print(f"1. Run: python main.py")
        print(f"2. Open: http://localhost:8000/docs")
        print(f"3. Test: http://localhost:8000/health\n")
        return 0
    else:
        print(f"{RED}✗ Some checks failed. See above for details.{NC}")
        print(f"{BLUE}{'='*50}{NC}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
