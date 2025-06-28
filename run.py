#!/usr/bin/env python3
"""
Development server runner for Punk Eco application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set default environment to development if not set
os.environ['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
os.environ['FLASK_APP'] = 'app:create_app()'

# Import app after setting environment variables
from app import create_app

def run():
    """Run the development server."""
    # Create the application
    app = create_app(os.getenv('FLASK_ENV').lower())
    
    # Configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    
    print(f"Starting Punk Eco server in {os.getenv('FLASK_ENV')} mode...")
    print(f" * Environment: {os.getenv('FLASK_ENV')}")
    print(f" * Debug mode: {debug}")
    print(f" * Running on http://{host}:{port}")
    
    # Run the application
    app.run(host=host, port=port, debug=debug, use_reloader=debug)

if __name__ == '__main__':
    run()
