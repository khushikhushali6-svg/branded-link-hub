from datetime import datetime

from app.extensions import db


class ClickEvent(db.Model):
    __tablename__ = "click_events"

    id = db.Column(db.Integer, primary_key=True)

    link_id = db.Column(
        db.Integer,
        db.ForeignKey("links.id"),
        nullable=False,
        index=True
    )

    clicked_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    referrer = db.Column(db.String(2048), nullable=True)

    device_type = db.Column(
        db.String(20),
        nullable=True
    )

    ip_hash = db.Column(
        db.String(64),
        nullable=True
    )

    link = db.relationship(
        "Link",
        back_populates="click_events"
    )

    def __repr__(self):
        return f"<ClickEvent {self.id}>"