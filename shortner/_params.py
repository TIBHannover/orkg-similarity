from marshmallow import Schema, validate, fields


class LinkGetParams(Schema):

    short_code = fields.String(location="view_args", required=True)


class ShortCodeCreateParams(Schema):

    link = fields.String(required=True)
