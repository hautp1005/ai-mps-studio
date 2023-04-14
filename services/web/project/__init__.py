"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import configparser

db = SQLAlchemy()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)

    logging.basicConfig(level=logging.DEBUG)
    x_config = configparser.ConfigParser()
    x_config.read('./project/configurations.cfg')
    REDIRECT_CALL_BACK_URI = x_config.get("uri", "REDIRECT_CALL_BACK_URI")

    app.config.from_object("project.config.Config")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "some-of-secret"
    app.config['OIDC_CLIENT_SECRETS'] = './project/client_secrets.json'
    app.config['OIDC_ID_TOKEN_COOKIE_SECURE'] = True
    app.config['OIDC_REQUIRE_VERIFIED_EMAIL'] = False
    app.config['OIDC_USER_INFO_ENABLED'] = True
    app.config['OIDC_INTROSPECTION_AUTH_METHOD'] = 'bearer'
    app.config['OIDC_INTROSPECTION_AUTH_METHOD'] = 'client_secret_post'
    app.config['OIDC_TOKEN_TYPE_HINT'] = 'access_token'
    app.config['OVERWRITE_REDIRECT_URI'] = True
    app.config['OVERWRITE_REDIRECT_URI'] = REDIRECT_CALL_BACK_URI

    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes

        db.create_all()  # Create database tables for our data models

        return app
