from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
import uuid

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Profile


ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

MAX_AVATAR_SIZE = 2 * 1024 * 1024


profile_bp = Blueprint(
    "profile",
    __name__,
    url_prefix="/api/profile"
)


@profile_bp.get("")
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())

    profile = Profile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        return jsonify({
            "error": "Profile not found."
        }), 404

    return jsonify({
        "profile": {
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "theme": profile.theme
        }
    }), 200


@profile_bp.post("/avatar")
@jwt_required()
def upload_avatar():
    user_id = int(get_jwt_identity())

    if "avatar" not in request.files:
        return jsonify({
            "error": "Avatar image is required."
        }), 400

    file = request.files["avatar"]

    if not file or not file.filename:
        return jsonify({
            "error": "Please select an image."
        }), 400

    extension = file.filename.rsplit(
        ".",
        1
    )[-1].lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return jsonify({
            "error": "Only PNG, JPG, JPEG, and WEBP images are allowed."
        }), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_AVATAR_SIZE:
        return jsonify({
            "error": "Avatar image must be 2 MB or smaller."
        }), 400

    upload_folder = os.path.join(
        "app",
        "static",
        "uploads",
        "avatars"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    filename = (
        f"{uuid.uuid4().hex}."
        f"{secure_filename(extension)}"
    )

    file_path = os.path.join(
        upload_folder,
        filename
    )

    file.save(file_path)

    profile = Profile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        return jsonify({
            "error": "Profile not found."
        }), 404

    profile.avatar_url = (
        f"/static/uploads/avatars/{filename}"
    )

    db.session.commit()

    return jsonify({
        "message": "Avatar uploaded successfully.",
        "avatar_url": profile.avatar_url
    }), 200


@profile_bp.post("")
@jwt_required()
def create_or_update_profile():
    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    display_name = data.get(
        "display_name",
        ""
    ).strip()

    if not display_name:
        return jsonify({
            "error": "Display name is required."
        }), 400

    profile = Profile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        profile = Profile(
            user_id=user_id,
            display_name=display_name
        )
        db.session.add(profile)

    profile.display_name = display_name
    profile.bio = data.get("bio")
    profile.avatar_url = data.get("avatar_url")
    profile.theme = data.get(
        "theme",
        "default"
    )

    db.session.commit()

    return jsonify({
        "message": "Profile saved successfully.",
        "profile": {
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "theme": profile.theme
        }
    }), 200