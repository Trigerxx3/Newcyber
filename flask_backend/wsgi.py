"""
WSGI entry point for production deployment (Render, Railway, etc.)
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Force production mode
os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app

app = create_app('production')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
