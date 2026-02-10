"""
Run the Django dev server from any directory.
Usage: python launch.py   (from backend folder)
   or: python backend/launch.py   (from project root)
"""
import os
import sys

# Ensure we're in the backend directory (where this file lives)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BACKEND_DIR)

# Add backend to path so manage.py can be found
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

def main():
    try:
        import django
    except ImportError:
        print("Django is not installed.")
        print("Run: pip install -r requirements.txt")
        print("(From the backend folder, or: pip install -r backend/requirements.txt)")
        input("Press Enter to exit...")
        sys.exit(1)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.management import execute_from_command_line
    argv = [sys.argv[0], "runserver", "127.0.0.1:8000"]
    print("\n  Open in Chrome: http://127.0.0.1:8000/admin/\n")
    execute_from_command_line(argv)

if __name__ == "__main__":
    main()
