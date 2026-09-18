import hashlib
import threading
from datetime import datetime

from flask import Blueprint, current_app, redirect, jsonify, request

from app.extensions import db, limiter
from app.models import ClickEvent, Link


public_bp = Blueprint("public_redirect", __name__)


def save_click_event(
    app,
    link_id,
    referrer,
    device_type,
    ip_hash
):
    with app.app_context():
        try:
            click_event = ClickEvent(
                link_id=link_id,
                clicked_at=datetime.utcnow(),
                referrer=referrer,
                device_type=device_type,
                ip_hash=ip_hash
            )

            db.session.add(click_event)
            db.session.commit()

        except Exception:
            db.session.rollback()

        finally:
            db.session.remove()


def log_click_async(
    app,
    link_id,
    referrer,
    device_type,
    ip_hash
):
    thread = threading.Thread(
        target=save_click_event,
        args=(
            app,
            link_id,
            referrer,
            device_type,
            ip_hash
        ),
        daemon=True
    )

    thread.start()


@public_bp.get("/r/<slug>")
@limiter.limit("60 per minute")
def redirect_link(slug):

    link = Link.query.filter(
        (Link.short_code == slug) |
        (Link.custom_slug == slug)
    ).first()

    if not link:
        return jsonify({
            "error": "Short link not found."
        }), 404

    if not link.is_active:
        return jsonify({
            "error": "This short link is inactive."
        }), 410

    user_agent = request.headers.get(
        "User-Agent",
        ""
    ).lower()

    if "tablet" in user_agent:
        device_type = "Tablet"

    elif any(
        mobile in user_agent
        for mobile in [
            "mobile",
            "android",
            "iphone",
            "ipad"
        ]
    ):
        device_type = "Mobile"

    else:
        device_type = "Desktop"

    referrer = request.referrer
    ip_address = request.remote_addr or ""

    ip_hash = hashlib.sha256(
        f"{ip_address}{current_app.config['SECRET_KEY']}".encode()
    ).hexdigest()

    app = current_app._get_current_object()

    log_click_async(
        app,
        link.id,
        referrer,
        device_type,
        ip_hash
    )
    return redirect(
        link.original_url,
        code=302
    )