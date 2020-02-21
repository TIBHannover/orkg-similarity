from marshmallow import Schema, validate, validate
from webargs import fields

class ComparisonGetParams(Schema):

    contributions = fields.DelimitedList(fields.String(), required=True, validate=validate.Length(min=2))

    response_hash = fields.String()

    save_response = fields.Boolean()

    
class ComparisonResponseGetParams(Schema):

    response_hash = fields.String(location="view_args", required=True)
