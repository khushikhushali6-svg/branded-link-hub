import re
import secrets

from datetime import datetime, timedelta
from urllib import response

from email_validator import (
    EmailNotValidError,
    validate_email
)

from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)

from sqlalchemy import or_

from app.extensions import db
from app.models import User, user


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)

active_refresh_tokens = {}

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


    username = data.get(
        "username",
        ""
    ).strip()


    email = data.get(
        "email",
        ""
    ).strip().lower()


    password = data.get(
        "password",
        ""
    )


    if not validate_username(username):

        return jsonify({
            "error":
            "Username must be 3-50 characters and contain only letters, numbers, and underscores."
        }),400



    if not validate_password(password):

        return jsonify({
            "error":
            "Password must be at least 8 characters long."
        }),400



    try:

        validated_email = validate_email(
            email,
            check_deliverability=False
        )

        email = validated_email.normalized


    except EmailNotValidError:

        return jsonify({
            "error":
            "Please provide a valid email address."
        }),400




    existing_user = User.query.filter(

        or_(

            User.username == username,

            User.email == email

        )

    ).first()



    if existing_user:

        if existing_user.username == username:

            return jsonify({
                "error":
                "Username already exists."
            }),409


        return jsonify({
            "error":
            "Email already exists."
        }),409




    user = User(

        username=username,

        email=email

    )


    user.set_password(password)


    db.session.add(user)

    db.session.commit()



    return jsonify({

        "message":
        "Registration successful. Please verify your email.",


        "verification_url":
        f"/api/auth/verify/{user.id}",


        "user":{

            "id":user.id,

            "username":user.username,

            "email":user.email,

            "is_verified":user.is_verified

        }

    }),201





@auth_bp.get("/verify/<int:user_id>")
def verify_email(user_id):


    user = User.query.get(user_id)


    if not user:

        return jsonify({
            "error":
            "User not found."
        }),404



    user.is_verified = True


    db.session.commit()



    return jsonify({

        "message":
        "Email verified successfully."

    }),200





@auth_bp.post("/login")
def login():


    data = request.get_json(silent=True) or {}



    identifier = data.get(
        "identifier",
        ""
    ).strip()



    password = data.get(
        "password",
        ""
    )



    if not identifier or not password:

        return jsonify({

            "error":
            "Identifier and password are required."

        }),400





    user = User.query.filter(

        or_(

            User.username == identifier,

            User.email == identifier.lower()

        )

    ).first()




    if not user or not user.check_password(password):

        return jsonify({

            "error":
            "Invalid username/email or password."

        }),401




    if not user.is_verified:

        return jsonify({

            "error":
            "Please verify your email first."

        }),403



    access_token = create_access_token(
        identity=str(user.id)
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    refresh_token_data = decode_token(
    refresh_token
    )

    active_refresh_tokens[str(user.id)] = (
        refresh_token_data["jti"]

    )



    response = jsonify({
        "message": "Login successful.",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 200





@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = str(get_jwt_identity())
    current_jti = get_jwt()["jti"]

    if active_refresh_tokens.get(user_id) != current_jti:
        return jsonify({
            "error": "Refresh token has been revoked or replaced."
        }), 401

    new_access_token = create_access_token(
        identity=user_id
    )

    new_refresh_token = create_refresh_token(
        identity=user_id
    )

    new_refresh_token_data = decode_token(
        new_refresh_token
    )

    active_refresh_tokens[user_id] = (
        new_refresh_token_data["jti"]
    )

    response = jsonify({
        "message": "Tokens refreshed successfully."
    })

    set_access_cookies(
        response,
        new_access_token
    )

    set_refresh_cookies(
        response,
        new_refresh_token
    )

    return response, 200



@auth_bp.post("/logout")
def logout():
    response = jsonify({
        "message": "Logout successful."
    })

    unset_jwt_cookies(response)

    return response, 200

@auth_bp.post("/forgot-password")
def forgot_password():


    data = request.get_json(silent=True) or {}



    email = data.get(
        "email",
        ""
    ).strip().lower()




    user = User.query.filter_by(

        email=email

    ).first()




    if not user:

        return jsonify({

            "message":
            "If this email exists, a reset link has been generated."

        }),200





    token = secrets.token_urlsafe(32)



    user.reset_token = token



    user.reset_token_expiry = (

        datetime.utcnow()

        +

        timedelta(minutes=15)

    )



    db.session.commit()




    return jsonify({

        "message":
        "Password reset link generated.",


        "reset_url":
        f"/reset-password/{token}"

    }),200





@auth_bp.post("/reset-password/<token>")
def reset_password(token):


    data = request.get_json(silent=True) or {}



    new_password = data.get(
        "password",
        ""
    )



    if not validate_password(new_password):

        return jsonify({

            "error":
            "Password must be at least 8 characters long."

        }),400





    user = User.query.filter_by(

        reset_token=token

    ).first()




    if not user:

        return jsonify({

            "error":
            "Invalid reset token."

        }),400





    if (

        user.reset_token_expiry

        and

        user.reset_token_expiry < datetime.utcnow()

    ):

        return jsonify({

            "error":
            "Reset token expired."

        }),400





    user.set_password(new_password)



    user.reset_token = None

    user.reset_token_expiry = None



    db.session.commit()




    return jsonify({

        "message":
        "Password reset successfully."

    }),200