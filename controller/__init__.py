from flask import Flask

app = Flask(__name__,static_folder='../static')
app.config.from_pyfile('config.cfg')

from controller.shop.routes import mod

app.register_blueprint(shop.routes.mod)
