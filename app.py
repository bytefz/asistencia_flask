from flask import Flask
from config import config
from flask_cors import CORS
from flask_moment import Moment
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy

# App initialization
app = Flask(__name__)
# Setting configuration
app.config.from_object(config["production"])

# Available CORS
CORS(app)

# Incializa el login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Bootstrap initialization
bootstrap = Bootstrap5()
bootstrap.init_app(app)

# Moment initialization
moment = Moment()
moment.init_app(app)

# SQLAlchemy initialization
db = SQLAlchemy()
db.init_app(app)

# Migrate initialization
migrate = Migrate(app, db)

# Importing Routes
from routes.routes import *


# Configuration for WSGI
application = app