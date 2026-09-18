import io
import re
from urllib.parse import urlparse

import qrcode
from flask import Blueprint, current_app, jsonify, redirect, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func, or_

from app.extensions import db
from app.models import ClickEvent, Link
from app.utils.slug import generate_short_code


links_bp = Blueprint("links", __name__, url_prefix="/api/links")


def validate_url(url):
    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )
    except ValueError:
        return False


def validate_custom_slug(slug):
    if not slug:
        return False

    return re.fullmatch(
        r"[A-Za-z0-9_-]{3,100}",
        slug
    ) is not None


@links_bp.post("")
@jwt_required()
def create_link():
    data = request.get_json(silent=True) or {}

    original_url = data.get("original_url", "").strip()
    custom_slug = data.get("custom_slug")
    title = data.get("title")

    if not original_url:
        return jsonify({
            "error": "Original URL is required."
        }), 400

    if not validate_url(original_url):
        return jsonify({
            "error": "Please provide a valid HTTP or HTTPS URL."
        }), 400

    if custom_slug is not None:
        custom_slug = custom_slug.strip()

        if not validate_custom_slug(custom_slug):
            return jsonify({
                "error": "Custom slug must be 3-100 characters and contain only letters, numbers, underscores, and hyphens."
            }), 400

        existing_slug = Link.query.filter_by(
            custom_slug=custom_slug
        ).first()

        if existing_slug:
            return jsonify({
                "error": "Custom slug already exists."
            }), 409

    if title is not None:
        title = title.strip()

        if len(title) > 150:
            return jsonify({
                "error": "Title cannot exceed 150 characters."
            }), 400

    user_id = int(get_jwt_identity())

    link = Link(
        user_id=user_id,
        original_url=original_url,
        short_code=generate_short_code(),
        custom_slug=custom_slug,
        title=title
    )

    db.session.add(link)
    db.session.commit()

    slug = link.get_slug()

    return jsonify({
        "message": "Short link created successfully.",
        "link": {
            "id": link.id,
            "original_url": link.original_url,
            "short_code": link.short_code,
            "custom_slug": link.custom_slug,
            "slug": slug,
            "title": link.title,
            "is_active": link.is_active,
            "short_url": f"/{slug}"
        }
    }), 201


@links_bp.get("")
@jwt_required()
def get_links():
    user_id = int(get_jwt_identity())

    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if page < 1:
        page = 1

    if per_page < 1:
        per_page = 10

    if per_page > 50:
        per_page = 50

    query = Link.query.filter_by(
        user_id=user_id
    )

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Link.title.ilike(search_pattern),
                Link.original_url.ilike(search_pattern),
                Link.short_code.ilike(search_pattern),
                Link.custom_slug.ilike(search_pattern)
            )
        )

    pagination = query.order_by(
        Link.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "links": [
            {
                "id": link.id,
                "original_url": link.original_url,
                "short_code": link.short_code,
                "custom_slug": link.custom_slug,
                "slug": link.get_slug(),
                "title": link.title,
                "is_active": link.is_active,
                "created_at": link.created_at.isoformat()
            }
            for link in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }), 200

@links_bp.patch("/<int:link_id>")
@jwt_required()
def update_link(link_id):
    user_id = int(get_jwt_identity())

    link = Link.query.filter_by(
        id=link_id,
        user_id=user_id
    ).first()

    if not link:
        return jsonify({
            "error": "Link not found."
        }), 404

    data = request.get_json(silent=True) or {}

    title = data.get("title")

    if title is not None:
        title = title.strip()

        if len(title) > 150:
            return jsonify({
                "error": "Title cannot exceed 150 characters."
            }), 400

        link.title = title

    if "is_active" in data:
        if not isinstance(data["is_active"], bool):
            return jsonify({
                "error": "is_active must be true or false."
            }), 400

        link.is_active = data["is_active"]

    db.session.commit()

    return jsonify({
        "message": "Link updated successfully.",
        "link": {
            "id": link.id,
            "original_url": link.original_url,
            "short_code": link.short_code,
            "custom_slug": link.custom_slug,
            "slug": link.get_slug(),
            "title": link.title,
            "is_active": link.is_active
        }
    }), 200


@links_bp.delete("/<int:link_id>")
@jwt_required()
def delete_link(link_id):
    user_id = int(get_jwt_identity())

    link = Link.query.filter_by(
        id=link_id,
        user_id=user_id
    ).first()

    if not link:
        return jsonify({
            "error": "Link not found."
        }), 404

    db.session.delete(link)
    db.session.commit()

    return jsonify({
        "message": "Link deleted successfully."
    }), 200


@links_bp.get("/<int:link_id>/analytics")
@jwt_required()
def get_link_analytics(link_id):
    user_id = int(get_jwt_identity())

    link = Link.query.filter_by(
        id=link_id,
        user_id=user_id
    ).first()

    if not link:
        return jsonify({
            "error": "Link not found."
        }), 404

    total_clicks = ClickEvent.query.filter_by(
        link_id=link.id
    ).count()

    unique_visitors = db.session.query(
        func.count(func.distinct(ClickEvent.ip_hash))
    ).filter(
        ClickEvent.link_id == link.id
    ).scalar()

    device_rows = db.session.query(
        ClickEvent.device_type,
        func.count(ClickEvent.id)
    ).filter(
        ClickEvent.link_id == link.id
    ).group_by(
        ClickEvent.device_type
    ).all()

    device_breakdown = {
        "Mobile": 0,
        "Desktop": 0,
        "Tablet": 0
    }

    for device_type, count in device_rows:
        if device_type in device_breakdown:
            device_breakdown[device_type] = count

    referrer_rows = db.session.query(
        ClickEvent.referrer,
        func.count(ClickEvent.id)
    ).filter(
        ClickEvent.link_id == link.id
    ).group_by(
        ClickEvent.referrer
    ).order_by(
        func.count(ClickEvent.id).desc()
    ).all()

    referrers = [
        {
            "referrer": referrer or "Direct",
            "clicks": count
        }
        for referrer, count in referrer_rows
    ]

    clicks_over_time_rows = db.session.query(
        func.date(ClickEvent.clicked_at),
        func.count(ClickEvent.id)
    ).filter(
        ClickEvent.link_id == link.id
    ).group_by(
        func.date(ClickEvent.clicked_at)
    ).order_by(
        func.date(ClickEvent.clicked_at)
    ).all()

    clicks_over_time = [
        {
            "date": str(date),
            "clicks": count
        }
        for date, count in clicks_over_time_rows
    ]

    return jsonify({
        "link": {
            "id": link.id,
            "slug": link.get_slug(),
            "original_url": link.original_url,
            "title": link.title
        },
        "analytics": {
            "total_clicks": total_clicks,
            "unique_visitors": unique_visitors or 0,
            "devices": device_breakdown,
            "referrers": referrers,
            "clicks_over_time": clicks_over_time
        }
    }), 200


@links_bp.get("/<int:link_id>/qr")
@jwt_required()
def generate_qr_code(link_id):
    user_id = int(get_jwt_identity())

    link = Link.query.filter_by(
        id=link_id,
        user_id=user_id
    ).first()

    if not link:
        return jsonify({
            "error": "Link not found."
        }), 404

    slug = link.get_slug()

    short_url = request.host_url.rstrip("/") + f"/{slug}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(short_url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    image_buffer = io.BytesIO()
    qr_image.save(
        image_buffer,
        format="PNG"
    )

    image_buffer.seek(0)

    return send_file(
        image_buffer,
        mimetype="image/png",
        as_attachment=True,
        download_name=f"{slug}-qr.png"
    )