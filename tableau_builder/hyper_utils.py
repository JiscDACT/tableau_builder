from typing import List, Dict
import logging
import pandas as pd
import pantab
from tableauhyperapi import HyperProcess, Telemetry, Connection, TableDefinition, escape_name, TableName

log = logging.getLogger(__name__)


def get_default_table_and_schema(hyper_path) -> Dict[str, str]:
    tables = []
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, 'test') as hyper:
        with Connection(hyper.endpoint, hyper_path) as connection:
            # The `connection.catalog` provides us with access to the meta-data we are interested in
            catalog = connection.catalog
            # Iterate over all schemas
            schemas = catalog.get_schema_names()
            for schema_name in schemas:
                # For each schema, iterate over all tables
                schema_tables = catalog.get_table_names(schema=schema_name)
                if len(schema_tables) > 0:
                    tables = schema_tables
    table = tables[0].name.unescaped
    schema = tables[0].schema_name
    if schema is None:
        schema = 'public'
    else:
        schema = schema.name.unescaped
    return {"table": table, "schema": schema}


def create_hyper_from_csv(csv_path: str, hyper_path: str, table_name="default") -> None:
    csv_df = pd.read_csv(csv_path)
    pantab.frame_to_hyper(csv_df, hyper_path, table=table_name)


def get_table(hyper_path: str, table_name='default', schema_name='public') -> TableDefinition:
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, 'test') as hyper:
        with Connection(hyper.endpoint, hyper_path) as connection:
            table_name_tuple = TableName(schema_name, table_name)
            table: TableDefinition = connection.catalog.get_table_definition(table_name_tuple)
    return table


def check_type(hyper_path: str, column_name: str, expected_type: str = 'text', table_name='default', schema_name='public'):
    table = get_table(hyper_path=hyper_path, table_name=table_name, schema_name=schema_name)
    column = table.get_column_by_name(column_name)
    if expected_type is None:
        expected_type = 'text'
    if str(column.type).lower() == expected_type.lower():
        return True
    else:
        log.error("Validation error: '" + str(column.type).lower() + "' is not the expected type (" + expected_type + ") for " + column_name)
        return False


def check_domain(hyper_path: str, field: str, domain: List, table_name='default', schema_name='public'):
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, 'test') as hyper:
        with Connection(hyper.endpoint, hyper_path) as connection:
            with connection.execute_query(
                    'SELECT DISTINCT "'+field+'" FROM "'+schema_name+'"."'+table_name+'"') as result:
                rows = list(result)
                hyper_domain = [str(item) for row in rows for item in row]
    for item in hyper_domain:
        if str(item) not in domain:
            log.error("Validation error: '" + str(item) + "' is not in domain of " + field)
            return False
    # If an item is in the domain but unused in the data, flag this as a warning
    for item in domain:
        if str(item) not in hyper_domain:
            log.warning("Warning: '" + str(item) + "' is not present in the data for " + field)
    return True


def check_range(hyper_path: str, field: str, min_value, max_value, table_name='default', schema_name='public'):
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, 'test') as hyper:
        with Connection(hyper.endpoint, hyper_path) as connection:
            with connection.execute_query(
                    'SELECT MIN("'+field+'") FROM "'+schema_name+'"."'+table_name+'"') as result:
                min_data = [item for row in list(result) for item in row][0]
            with connection.execute_query(
                    'SELECT MAX("'+field+'") FROM "'+schema_name+'"."'+table_name+'"') as result:
                max_data = [item for row in list(result) for item in row][0]

    try:
        if float(min_data) < min_value or float(max_data) > max_value:
            log.error("Validation error: Values out of range in data for " + field +
                      '; Data: ' + str(min_data) + ' to ' + str(max_data) +
                      '; Spec: ' + str(min_value) + ' to ' + str(max_value))
            return False
    except ValueError:
        log.error("Range could not be checked for " + field)
        return False

    return True


def subset_columns(columns_to_keep: List, hyper_path: str, schema_name: str, table_name: str):
    """
    Drops any columns from a hyper that are not in the list of columns. Used to subset a hyper
    to only the fields present in the specification
    """
    columns = get_hyper_columns(hyper_path, table_name, schema_name)

    # Fix columns with leading and/or trailing spaces in the hyper.
    columns_processed = []
    for column in columns:
        if column != column.strip():
            with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, 'test') as hyper:
                with Connection(hyper.endpoint, hyper_path) as connection:
                    command = ' '.join([
                        "ALTER TABLE",
                        get_qualified_name(table_name, schema_name),
                        "RENAME COLUMN",
                        escape_name(column),
                        "TO",
                        escape_name(column.strip())]
                    )
                    result = connection.execute_query(command)
                    result.close()
            columns_processed.append(column.strip())
            log.warning("Found and fixed an invalid column name '"+column+"'")
        else:
            columns_processed.append(column)
    columns = columns_processed

    columns_to_drop = []
    for column in columns:
        if column not in columns_to_keep:
            columns_to_drop.append(column)

    for column in columns_to_drop:
        with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, 'test') as hyper:
            with Connection(hyper.endpoint, hyper_path) as connection:
                command = " ".join([
                    "ALTER TABLE",
                    get_qualified_name(table_name, schema_name),
                    "DROP COLUMN",
                    escape_name(column)
                ])
                result = connection.execute_query(command)
                result.close()


def check_column_exists(column_name: str, hyper_path: str, table_name: str, schema_name: str) -> bool:
    columns = get_hyper_columns(hyper_path=hyper_path, table_name=table_name, schema_name=schema_name)
    return column_name in columns


def get_hyper_columns(hyper_path: str, table_name: str, schema_name: str) -> List[str]:
    """
    Gets a list of columns from the hyper
    """
    table = get_table(hyper_path=hyper_path, table_name=table_name, schema_name=schema_name)
    columns = []
    for column in table.columns:
            columns.append(column.name.unescaped)
    return columns


def get_qualified_name(table_name: str, schema_name: str) -> str:
    """
    Gets a qualified table name, i.e. schema.table with escaping
    """
    return escape_name(schema_name) + '.' + escape_name(table_name)


def get_table_name(table_name: str, schema_name: str) -> TableName:
    """
    Gets a TableName from components
    """
    return TableName(schema_name, table_name)
