from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import User


pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/login")
def login_page():
    return render_template("login.html")


@pages_bp.get("/register")
def register_page():
    return render_template("register.html")


@pages_bp.get("/dashboard")
@jwt_required()
def dashboard_page():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    return render_template(
        "dashboard.html",
        username=user.username
    )


@pages_bp.get("/forgot-password")
def forgot_password_page():
    return render_template("forgot-password.html")


@pages_bp.get("/reset-password/<token>")
def reset_password_page(token):
    return render_template(
        "reset-password.html"
    )