from marshmallow import Schema
from webargs import fields


class ReviewGetParams(Schema):
    resourceId = fields.String(required=True)
