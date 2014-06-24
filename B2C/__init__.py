from flask import Flask
from json import JSONEncoder, JSONDecoder

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')
app.config.from_envvar('B2C_SETTINGS', silent = True)

#database
db = SQLAlchemy(app)

json_decoder = JSONDecoder()
json_encoder = JSONEncoder()

from B2C import views