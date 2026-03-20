import os
import tempfile

class Config:
    """Application configuration"""
    
    # Flask config
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    
    # Upload config
    UPLOAD_FOLDER = tempfile.gettempdir()
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'js'}
    MAX_CONTENT_LENGTH = 150 * 1024 * 1024  # 150MB max file size
    
    # App settings
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
