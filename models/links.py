from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy_utils import ScalarListType
from extensions import db
from basehash import base62
from ._base import ModelMixin

base62 = base62(6)

class Link(db.Model, ModelMixin):
    __tablename__ = "links"

    long_url = db.Column(db.String(1000), index=True)

    short_code = db.Column(db.Unicode(64), unique=True, index=True, default=None)

    contributions = db.Column(ScalarListType())

    properties = db.Column(ScalarListType())

    transpose = db.Column(db.Boolean)

    json_code = db.Column(db.String)

    response_hash = db.Column(db.String)

    @classmethod
    def generate_next_short_code(cls):
        base_id = Link.count_all()
        short_code = base62.hash(base_id + 1)
        while Link.query.filter(cls.short_code == short_code).count() > 0:
                base_id += 1
                short_code = base62.hash(base_id)
        return short_code

    @classmethod
    def get_by_code(cls, short_code):
        link = Link.query.filter(cls.short_code == short_code).first()
        return link

    @classmethod
    def get_by_long_url(cls, long_url):
        response = Link.query.filter(cls.long_url == long_url).first()
        return response