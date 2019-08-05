# -*- coding: utf-8 -*-
from sqlalchemy.dialects.postgresql.base import UUID
from extensions import db
from datetime import datetime
from uuid import uuid4
import six


class ModelMixin(object):
    __tablename__ = None

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    def save(self):
        try:
            self.updated_at = datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
            raise

    @classmethod
    def get_all(cls):
        return db.session.query(cls).all()

    @classmethod
    def count_all(cls):
        return db.session.query(cls).count()

    @classmethod
    def get(cls, id_):
        return db.session.query(cls).get(id_) if id_ else None

    @classmethod
    def query(cls):
        return db.session.query(cls)

    def __repr__(self):
        return "<%s (id=%s)>" % (self.__class__.__name__, self.id)

    def __str__(self):
        return self.__repr__()
