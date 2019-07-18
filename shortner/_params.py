from marshmallow import Schema, validate, fields


class LinkGetParams(Schema):

    link_id = fields.UUID(location="view_args", required=True)


class ShortCodeCreateParams(Schema):

    link = fields.String(required=True)
