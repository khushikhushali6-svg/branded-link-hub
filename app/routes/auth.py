import re

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
)
from sqlalchemy import or_

from app.extensions import db
from app.models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def validate_password(password):
    if not password or len(password) < 8:
        return False
    return True


def validate_username(username):
    if not username:
        return False

    return re.fullmatch(
        r"[A-Za-z0-9_]{3,50}",
        username
    ) is not None


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not validate_username(username):
        return jsonify({
            "error": "Username must be 3-50 characters and contain only letters, numbers, and underscores."
        }), 400

    if not validate_password(password):
        return jsonify({
            "error": "Password must be at least 8 characters long."
        }), 400

    try:
        validated_email = validate_email(
            email,
            check_deliverability=False
        )
        email = validated_email.normalized
    except EmailNotValidError:
        return jsonify({
            "error": "Please provide a valid email address."
        }), 400

    existing_user = User.query.filter(
        or_(
            User.username == username,
            User.email == email
        )
    ).first()

    if existing_user:
        if existing_user.username == username:
            return jsonify({
                "error": "Username already exists."
            }), 409

        return jsonify({
            "error": "Email already exists."
        }), 409

    user = User(
        username=username,
        email=email
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    identifier = data.get("identifier", "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({
            "error": "Identifier and password are required."
        }), 400

    user = User.query.filter(
        or_(
            User.username == identifier,
            User.email == identifier.lower()
        )
    ).first()

    if not user or not user.check_password(password):
        return jsonify({
            "error": "Invalid username/email or password."
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    response = jsonify({
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })

    set_access_cookies(
        response,
        access_token
    )

    set_refresh_cookies(
        response,
        refresh_token
    )

    return response, 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()

    new_access_token = create_access_token(
        identity=str(user_id)
    )

    response = jsonify({
        "message": "Access token refreshed successfully."
    })

    set_access_cookies(
        response,
        new_access_token
    )

    return response, 200