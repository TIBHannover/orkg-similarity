from extensions import db
from ._base import ModelMixin


class VisualizationResponse(db.Model, ModelMixin):
    __tablename__ = "visualization_models"

    resource_id = db.Column(db.String)
    data = db.Column(db.JSON)

    def __init__(self, resource_id, data):
        self.resource_id = resource_id
        self.data = data

    def __repr__(self):
        return '{"orkgOrigin": "%s", "data":%s }' % (self.resource_id, self.data)

    @classmethod
    def add_visualization(cls, resource_id, data):
        new_entry = VisualizationResponse(resource_id, data)
        db.session.add(new_entry)
        db.session.commit()

    @classmethod
    def get_by_resource_id(cls, resource_id):
        response = VisualizationResponse.query.filter(cls.resource_id == resource_id).first()
        return response
