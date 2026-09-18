from datetime import datetime

from app.extensions import db


class Link(db.Model):
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    original_url = db.Column(db.String(2048), nullable=False)

    short_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        index=True
    )

    custom_slug = db.Column(
        db.String(100),
        unique=True,
        nullable=True,
        index=True
    )

    title = db.Column(db.String(150), nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="links"
    )

    click_events = db.relationship(
        "ClickEvent",
        back_populates="link",
        cascade="all, delete-orphan"
    )

    def get_slug(self):
        return self.custom_slug or self.short_code

    def __repr__(self):
        return f"<Link {self.get_slug()}>"