from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import ForeignKey
from zope.sqlalchemy import register
import ziggurat_foundations.models 
from sqlalchemy import Column, Integer, func, SmallInteger, DateTime
from sqlalchemy.ext.declarative import declared_attr

session_factory = sessionmaker()
DBSession = scoped_session(session_factory)
register(DBSession)
ziggurat_foundations.models.DBSession = DBSession
TABLE_ARGS = dict(extend_existing=True, schema="public")



class DefaultModel(object):
    db_session = DBSession
    id = Column(Integer, primary_key=True)
 
    @classmethod
    def save(cls, values, row=None, **kwargs):
        if not row:
            row = cls()
        for key, value in values.items():
            if hasattr(row, key):
                setattr(row, key, value)
        return row

    @classmethod
    def count(cls):
         return cls.db_session.query(func.count(cls.id)).scalar()

    @classmethod
    def query(cls, filters=None):
        query = cls.db_session.query(cls)
        if filters:
            filter_expressions = []
            for d in filters:
                field = getattr(cls, d[0])
                operator = d[1]
                value = d[2]
                filter_expressions.append(field.op(operator)(value))
            query = query.filter(
                *[e for i, e in enumerate(filter_expressions) if e is not None])
        return query

    @classmethod
    def query_from(cls, columns=[], filters=None):
        query = cls.db_session.query().select_from(cls)
        for c in columns:
            query = query.add_columns(c)
        return query

    @classmethod
    def query_id(cls, row_id):
        return cls.query().filter_by(id=row_id)

    @classmethod
    def delete(cls, row_id):
        cls.query_id(row_id).delete()

class StandardModel(DefaultModel):
    status = Column(SmallInteger)
    
    @declared_attr
    def create_uid(self):
        return Column(
            Integer,
            ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            primary_key=True,
        )
    
    @declared_attr
    def update_uid(self):
        return Column(
            Integer,
            ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            primary_key=True,
        )

    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
