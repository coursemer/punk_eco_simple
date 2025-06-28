"""
Database configuration for the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig:
    """Database configuration settings."""
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///punk_eco.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # Connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,  # Recycle connections after 5 minutes
        'pool_size': 10,
        'max_overflow': 20,
    }
    
    # Migration settings
    MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'migrations')
    
    @classmethod
    def init_app(cls, app):
        """Initialize the Flask app with database configuration."""
        app.config['SQLALCHEMY_DATABASE_URI'] = cls.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = cls.SQLALCHEMY_TRACK_MODIFICATIONS
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = cls.SQLALCHEMY_ENGINE_OPTIONS
        
        # Set echo flag if in debug mode
        if app.debug:
            app.config['SQLALCHEMY_ECHO'] = True
