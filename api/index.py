import os
import sys

# Add the project root to sys.path so we can import server.py and other modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server import app

# Vercel requires the app variable to be at the top level
# or to be accessible via the module name.
# Here we just re-export it.
