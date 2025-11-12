from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register
import ziggurat_foundations.models 
from sqlalchemy import Column, Integer, func

session_factory = sessionmaker()
DBSession = scoped_session(session_factory)
register(DBSession)
ziggurat_foundations.models.DBSession = DBSession
TABLE_ARGS = dict(extend_existing=True, schema="public")



class DefaultModel(object):
    id = Column(Integer, primary_key=True)

    db_session = DBSession

    def __init__(self):
        super().__init__()
        self.db_session = DBSession

    @classmethod
    def save(cls, values, row=None, **kwargs):
        if not row:
            row = cls()
        row.from_dict(values)
        return row

    @classmethod
    def count(cls,  db_session=None):
        if not db_session:
            db_session = cls.db_session
        return db_session.query(func.count('id')).scalar()

    @classmethod
    def query(cls, db_session=None, filters=None):
        if not db_session:
            db_session = cls.db_session
        query = db_session.query(cls)
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
    def query_from(cls, db_session=None, columns=[], filters=None):
        if not db_session:
            db_session = cls.db_session
        query = db_session.query().select_from(cls)
        for c in columns:
            query = query.add_columns(c)
        return query

    @classmethod
    def query_id(cls, row_id, db_session=None):
        if not db_session:
            db_session = cls.db_session
        return cls.query(db_session).filter_by(id=row_id)

    @classmethod
    def delete(cls, row_id, db_session=None):
        if not db_session:
            db_session = cls.db_session
        cls.query_id(row_id, db_session).delete()
