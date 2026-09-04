from sqlalchemy.types import UserDefinedType


class LtreeType(UserDefinedType):
    """Maps Python str <-> PostgreSQL LTREE column type.

    Declared via UserDefinedType (rather than relying on a version-specific
    sqlalchemy.dialects.postgresql.LTREE export) so it works across SQLAlchemy
    2.0 point releases; production schema is created via the Alembic migration,
    which uses raw DDL for this column.
    """

    cache_ok = True

    def get_col_spec(self, **kw):
        return "LTREE"

    def bind_processor(self, dialect):
        return lambda value: value

    def result_processor(self, dialect, coltype):
        return lambda value: value
