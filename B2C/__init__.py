from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')
app.config.from_envvar('B2C_SETTINGS', silent = True)

#database
db = SQLAlchemy(app)

from B2C import views