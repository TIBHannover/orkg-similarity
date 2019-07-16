from sqlalchemy.dialects.postgresql.base import UUID
from extensions import db
from ._base import ModelMixin


class Link(db.Model, ModelMixin):
    __tablename__ = "links"

    long_url = db.Column(db.String(1000), index=True)