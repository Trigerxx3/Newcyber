"""
Production runner for Flask app
"""
import os
from app import create_app

# Create Flask app
app = create_app('production' if os.getenv('FLASK_ENV') == 'production' else 'development')

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.getenv('PORT', 5000))
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') != 'production'
    )