from sqlalchemy import create_engine, inspect
from database import database_config


class DBColumn:
    def __init__(self, name, primary_key, data_type):
        self.name = name
        self.primary_key = primary_key
        self.data_type = data_type

    def __repr__(self):
        return f"DBColumn(name={self.name}, primary_key={self.primary_key}, data_type={self.data_type})"


class DBTable:
    def __init__(self, name):
        self.name = name
        self.columns = []

    def add_column(self, column):
        self.columns.append(column)

    def __repr__(self):
        return f"DBTable(name={self.name}, columns={self.columns})"


def connect_to_database():
    engine = create_engine(database_config.database_connection_uri)
    return engine


def query_schema(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    db_tables = []

    for table_name in tables:
        db_table = DBTable(table_name)

        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = (
            set(pk_constraint["constrained_columns"]) if pk_constraint else set()
        )

        for column in columns:
            column_name = column["name"]
            data_type = str(column["type"])
            primary_key = column_name in primary_keys
            db_column = DBColumn(column_name, primary_key, data_type)
            db_table.add_column(db_column)

        db_tables.append(db_table)

    return db_tables
