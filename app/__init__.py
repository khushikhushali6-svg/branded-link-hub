from flask import Flask, app, render_template

from .config import Config
from .extensions import db, jwt, limiter
from . import models
from .routes.auth import auth_bp
from .routes.links import links_bp
from .routes.profile import profile_bp
from .routes.social import social_bp
from .routes.public import public_bp as public_redirect_bp
from .routes.public_bio import public_bp as public_bio_bp
from .routes.pages import pages_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(public_redirect_bp)
    app.register_blueprint(public_bio_bp)
    app.register_blueprint(pages_bp)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return render_template("home.html")

    return app