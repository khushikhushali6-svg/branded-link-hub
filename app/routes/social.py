from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)

from app.extensions import db
from app.models import SocialLink


social_bp = Blueprint(
    "social",
    __name__,
    url_prefix="/api/social"
)


@social_bp.get("")
@jwt_required()
def get_social_links():
    user_id = int(get_jwt_identity())

    links = SocialLink.query.filter_by(
        user_id=user_id
    ).order_by(
        SocialLink.display_order.asc()
    ).all()

    return jsonify({
        "social_links": [
            {
                "id": link.id,
                "platform": link.platform,
                "url": link.url,
                "display_order": link.display_order,
                "is_visible": link.is_visible
            }
            for link in links
        ]
    }), 200


@social_bp.post("")
@jwt_required()
def create_social_link():
    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    platform = data.get("platform", "").strip()
    url = data.get("url", "").strip()

    if not platform or not url:
        return jsonify({
            "error": "Platform and URL are required."
        }), 400

    social_link = SocialLink(
        user_id=user_id,
        platform=platform,
        url=url,
        display_order=data.get("display_order", 0),
        is_visible=data.get("is_visible", True)
    )

    db.session.add(social_link)
    db.session.commit()

    return jsonify({
        "message": "Social link created successfully.",
        "social_link": {
            "id": social_link.id,
            "platform": social_link.platform,
            "url": social_link.url
        }
    }), 201


@social_bp.patch("/<int:link_id>")
@jwt_required()
def update_social_link(link_id):
    user_id = int(get_jwt_identity())

    link = SocialLink.query.filter_by(
        id=link_id,
        user_id=user_id
    ).first()

    if not link:
        return jsonify({
            "error": "Social link not found."
        }), 404

    data = request.get_json(silent=True) or {}

    if "platform" in data:
        platform = str(data["platform"]).strip()

        if not platform:
            return jsonify({
                "error": "Platform cannot be empty."
            }), 400

        link.platform = platform

    if "url" in data:
        url = str(data["url"]).strip()

        if not url:
            return jsonify({
                "error": "URL cannot be empty."
            }), 400

        link.url = url

    if "display_order" in data:
        link.display_order = data["display_order"]

    if "is_visible" in data:
        link.is_visible = bool(data["is_visible"])

    db.session.commit()
    db.session.refresh(link)

    return jsonify({
        "message": "Social link updated successfully.",
        "social_link": {
            "id": link.id,
            "platform": link.platform,
            "url": link.url,
            "display_order": link.display_order,
            "is_visible": link.is_visible
        }
    }), 200


@social_bp.delete("/<int:link_id>")
@jwt_required()
def delete_social_link(link_id):
    user_id = int(get_jwt_identity())

    link = SocialLink.query.filter_by(
        id=link_id,
        user_id=user_id
    ).first()

    if not link:
        return jsonify({
            "error": "Social link not found."
        }), 404

    db.session.delete(link)
    db.session.commit()

    return jsonify({
        "message": "Social link deleted successfully."
    }), 200