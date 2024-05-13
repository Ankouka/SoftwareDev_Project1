from flask import Flask
import os

app = Flask("Authentication Web App")
if 'SECRET_KEY' not in os.environ:
    raise EnvironmentError('SECRET_KEY not set in environment')
app.secret_key = os.environ['SECRET_KEY']

#app.secret_key = os.environ['SECRET_KEY']

# db initialization
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
#app.config['UPLOADED_PICTURES_DEST']= 'C:\\Users\\nkouk\\project-1-windoors-dream-team'
db.init_app(app)

from app import models
with app.app_context(): 
    db.create_all()

# login manager
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


from app.models import User

# user_loader callback
@login_manager.user_loader
def load_user(id):
    try: 
        return db.session.query(User).filter(User.id==id).one()
    except: 
        return None

from app import routes