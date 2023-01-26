from flask import Flask
from config import Config
from .models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager

from .api.routes import api

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)

login_manager.login_view='loginPage'
# if they're not logged in and Log in is required, redirect to the Login Page

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

app.register_blueprint(api)

from . import routes
from . import models