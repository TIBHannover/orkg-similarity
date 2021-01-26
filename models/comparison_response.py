from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy_utils import ScalarListType
from extensions import db
from basehash import base62
from ._base import ModelMixin

base62 = base62(6)


class ComparisonResponse(db.Model, ModelMixin):
    __tablename__ = "comparison_responses"

    response_hash = db.Column(db.String)

    data = db.Column(db.JSON)

    @classmethod
    def get_by_hash(cls, response_hash):
        response = ComparisonResponse.query.filter(cls.response_hash == response_hash).first()
        return response
