from flask import Flask
from .config import Config
from .plugin import db, cors, siwa


def _load_plugins(app):
    db.init_app(app)
    cors.init_app(app)
    siwa.init_app(app)


def _load_config(app):
    app.config.from_object(Config)


def _init_blueprint(app):
    from .routes.views import bp
    
    app.register_blueprint(bp)


def create_app():
    app = Flask(__name__)
    
    # 初始化配置
    _load_config(app)

    # 初始化插件
    _load_plugins(app)

    # 初始化蓝图
    _init_blueprint(app)

    return app
