from flask import Flask
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, root_path="/api")
csrf = CSRFProtect()
csrf.init_app(app)
