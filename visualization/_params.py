from marshmallow import Schema
from webargs import fields


class VisualizationGetParams(Schema):
    resourceId = fields.String(required=True)
