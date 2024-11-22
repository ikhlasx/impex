import os
class Config:
    # Get secret key from environment variable or use a default for development
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this-in-production'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'video_player.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Video upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join('app', 'static', 'videos')
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv'}
