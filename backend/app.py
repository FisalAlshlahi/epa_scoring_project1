"""
EPA Scoring Engine - Main Application
File: backend/app.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Import our modules
from models.scoring_engine import EPAScoringEngine
from services.scoring_service import ScoringService
from services.quality_service import QualityService
from utils.database import DatabaseManager
from api.routes import api_bp

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    app.config['DB_CONFIG'] = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'epa_scoring'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'charset': 'utf8mb4'
    }
    
    # Initialize database manager
    db_manager = DatabaseManager(app.config['DB_CONFIG'])
    app.db_manager = db_manager
    
    # Initialize services
    app.scoring_service = ScoringService(app.config['DB_CONFIG'])
    app.quality_service = QualityService(app.config['DB_CONFIG'])
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Application health check"""
        try:
            # Test database connection
            db_status = db_manager.test_connection()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected' if db_status else 'disconnected',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    # Root endpoint
    @app.route('/')
    def index():
        """Root endpoint"""
        return jsonify({
            'message': 'EPA Scoring System API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'api': '/api',
                'docs': '/api/docs'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting EPA Scoring System API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )

