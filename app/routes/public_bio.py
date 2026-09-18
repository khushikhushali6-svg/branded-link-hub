from flask import Blueprint, jsonify

from app.models import User


public_bp = Blueprint(
    "public",
    __name__
)


@public_bp.get("/bio/<username>")
def public_profile(username):

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({
            "error": "Profile not found."
        }), 404

    profile = user.profile

    if not profile:
        return jsonify({
            "error": "Bio profile not created."
        }), 404

    social_links = [
        {
            "platform": link.platform,
            "url": link.url
        }
        for link in user.social_links
        if link.is_visible
    ]

    links = [
        {
            "title": link.title,
            "url": f"/{link.get_slug()}"
        }
        for link in user.links
        if link.is_active
    ]

    return jsonify({
        "profile": {
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "theme": profile.theme
        },
        "social_links": social_links,
        "links": links
    }), 200