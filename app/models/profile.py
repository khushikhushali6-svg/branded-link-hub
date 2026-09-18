from datetime import datetime

from app.extensions import db


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    display_name = db.Column(
        db.String(100),
        nullable=False
    )

    bio = db.Column(
        db.Text,
        nullable=True
    )

    avatar_url = db.Column(
        db.String(500),
        nullable=True
    )

    theme = db.Column(
        db.String(50),
        default="default"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="profile"
    )