import os
#configration
DEBUG = True
#DATABASE = '/.db'
SECRET_KEY = '****'
SQLALCHEMY_DATABASE_URI = 'sqlite:////home/jason/Flask/venv/B2C1/B2C.db'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('B2C/static/uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
