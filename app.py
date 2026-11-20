import os

from dotenv import load_dotenv
from flask import Flask

from errors import register_errors
from routes.apiaries import bp as apiaries_bp
from routes.harvests import bp as harvests_bp
from routes.hives import bp as hives_bp
from routes.home import bp as home_bp


def create_app(test_config: dict | None = None) -> Flask:
    if os.getenv("APP_ENV", "development") == "development":
        load_dotenv()

    app = Flask(__name__)

    app.config.from_mapping(
        APP_ENV=os.getenv("APP_ENV", "development"),
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        HONEY_PRICE_KSH=int(os.getenv("HONEY_PRICE_KSH", "900")),
    )

    if test_config is not None:
        app.config.update(test_config)

    register_errors(app)

    app.register_blueprint(home_bp)
    app.register_blueprint(apiaries_bp)
    app.register_blueprint(hives_bp)
    app.register_blueprint(harvests_bp)

    return app