from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Profile


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