import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_wtf import CSRFProtect
from flask_login import LoginManager
import logging

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
login_manager = LoginManager()

# create the app
app = Flask(__name__)

# setup a secret key, required by sessions and CSRF protection
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///educational_platform.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extensions
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

def create_test_user():
    from models import User
    from werkzeug.security import generate_password_hash
    
    test_user = User.query.filter_by(email='test@example.com').first()
    if not test_user:
        test_user = User(
            username='Test User',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            areas_of_expertise='Testing',
            preferred_subjects='Unit Tests'
        )
        db.session.add(test_user)
        try:
            db.session.commit()
            logging.debug(f"Test user created: {test_user}")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating test user: {str(e)}")

with app.app_context():
    # Import models and create tables
    import models
    db.create_all()
    create_test_user()

# Import and register routes
from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
