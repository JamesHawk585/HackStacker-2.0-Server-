from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restful import Api
from flask_marshmallow import Marshmallow


# Do I need to import and use API if I am using app.route? 
# Is there any benefit to using Flask RESTful instead? 

app = Flask(__name__)

# Generating Secret Key:
# In the terminal, run: python -c 'import os; print(os.urandom(16))'

app.secret_key = b'\xbep/TF\x19.eh)v}\xb1\x9a\x9fO'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db = SQLAlchemy()

migrate = Migrate(app, db)
db.init_app(app)
ma = Marshmallow(app)

bcrypt = Bcrypt(app)

CORS(app)

api = Api(app)