from flask import Flask
import logging
import configparser
from datetime import  timedelta
from controllers.authentication import auth_bp
from controllers.settings import settings_bp
from controllers.algorithms import algo_bp
from controllers.routes import user_bp
from controllers.education import education_bp

logging.basicConfig(filename="main.log",
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    filemode="w")

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.secret_key = config.get('app', 'secret_key')
is_test = config.getboolean('app', 'is_test')
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

app.register_blueprint(auth_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(algo_bp)
app.register_blueprint(user_bp)
app.register_blueprint(education_bp)

if __name__ == '__main__':
    print(is_test)
    if is_test:
        app.run()
    else:
        app.run(host='0.0.0.0', port=5000) 