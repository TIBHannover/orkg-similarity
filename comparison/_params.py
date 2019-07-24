from marshmallow import Schema, validate, fields


class ComparisonResponseGetParams(Schema):

    response_hash = fields.String(location="view_args", required=True)
