from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a72ea501e9d46cb20c58123dd74e8b02'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['ALLOWED_ADMIN_EMAILS'] = ['admin@example.com', 'boss@yourcompany.com']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SCHEDULER_API_ENABLED'] = True



# -------------------- APScheduler Setup -------------------- #
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from flasklibrary import routes


