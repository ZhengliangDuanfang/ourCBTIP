import os
from flask import Flask
from .config import Config
from .plugin import db, cors, siwa
from ..predict import prediction_setup
from .mock_param import get_params

def _load_plugins(app):
    db.init_app(app)
    cors.init_app(app)
    siwa.init_app(app)


def _load_config(app):
    app.config.from_object(Config)
    params = get_params()
    setups = prediction_setup(params, params.model_filename)
    app.config['SETUPS'] = dict(zip(
        ['decoder_inter', 'emb_inter', 'drug_cnt', 'relation2id', 'id2relation', 'id2drug', 'drug2id', 'id2target', 'target2id'],
        setups
    ))


def _init_blueprint(app):
    from .routes.views import bp
    
    app.register_blueprint(bp)


def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    instance_path = os.path.join(base_dir, "instance")
    print(instance_path)
    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
    
    # 初始化配置
    _load_config(app)

    # 初始化插件
    _load_plugins(app)

    # 初始化蓝图
    _init_blueprint(app)

    return app
