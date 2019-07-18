from marshmallow import Schema, validate, fields


class LinkGetParams(Schema):

    short_code = fields.String(location="view_args", required=True)


class ShortCodeCreateParams(Schema):

    long_url = fields.String(required=True)

    contributions = fields.List(fields.String)

    properties = fields.List(fields.String)

    transpose = fields.Boolean()

    json_code = fields.Boolean()
