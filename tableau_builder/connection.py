import csv
import os.path
import pandas as pd
from typing import List
from lxml import etree

EXCEL_CLASS = 'excel-direct'
CSV_CLASS = 'textscan'
HYPER_CLASS = 'hyper'


class Connection:

    def __init__(self, file_path,
                 table_name=None,
                 schema_name=None,
                 connection_type=EXCEL_CLASS,
                 package=False,
                 cleaning='no',
                 compat='no',
                 data_refresh_time='',
                 interpretation_mode='0',
                 password='',
                 server='',
                 validate='no'
                 ):
        """
        :param file_path: The path to the data file
        :param table_name: The name of the Excel sheet or Hyper table
        :param connection_type: CSV, EXCEL or HYPER
        :param package: True if the connection is the data is to be packaged, False if a live connection to the datasource path will be used.
        :param cleaning: Not used
        :param compat: Not used
        :param data_refresh_time: Not used
        :param interpretation_mode: Not used
        :param password: Not used
        :param server: Not used
        :param validate: Not used
        """
        self.file_path = file_path
        self.class_name = connection_type
        self.cleaning = cleaning
        self.compat = compat
        self.data_refresh_time = data_refresh_time
        self.interpretation_mode = interpretation_mode
        self.password = password
        self.server = server
        self.validate = validate
        self.schema_name = schema_name
        self.dbname = None

        directory_name, file_name = os.path.split(file_path)

        if package:
            self.directory = 'Data'
        else:
            self.directory = directory_name

        if connection_type == CSV_CLASS:
            self.table_name = str.replace(file_name, '.', '#')
            self.file_name = file_name
        elif connection_type == HYPER_CLASS:
            if table_name is None:
                raise ValueError("No table name has been specified")
            self.table_name = table_name
            self.dbname = os.path.join(self.directory, file_name)
            self.file_name = os.path.join(self.directory, file_name)
        else:
            if table_name is None:
                raise ValueError("No sheet name has been specified")
            else:
                self.table_name = table_name
            self.file_name = os.path.join(directory_name, file_name)

    def get_table_name(self) -> str:
        if self.class_name == HYPER_CLASS:
            return str.format('[{0}].[{1}]', self.schema_name, self.table_name)
        return '[' + self.table_name + ']'

    def get_columns(self) -> List[str]:
        if self.class_name == EXCEL_CLASS:
            columns = pd.read_excel(self.file_path).columns.to_list()
        else:
            with open(self.file_path, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                columns = list(reader.fieldnames)
        return columns

    def get_relation_name(self) -> str:
        if self.class_name == CSV_CLASS:
            return '[' + self.file_name + ']'
        elif self.class_name == HYPER_CLASS:
            return self.table_name
        else:
            return self.get_table_name()

    def to_xml(self) -> etree.Element:
        element = etree.Element('connection',
                                cleaning=self.cleaning,
                                compat=self.compat,
                                dataRefreshTime=self.data_refresh_time,
                                filename=self.file_name,
                                interpretationMode=self.interpretation_mode,
                                password=self.password,
                                server=self.server,
                                validate=self.validate,
                                directory=self.directory
                                )
        element.set('class', self.class_name)
        if self.dbname is not None:
            element.set('dbname', self.dbname)
        return element


class Federation:

    def __init__(self, caption='Data', table='Table'):
        self.caption = caption
        self.name = 'connection'
        self.table = table
        self.connection = None

    def get_columns(self) -> List[str]:
        return self.connection.get_columns()

    def connect_to_excel(self, excel_path, table_name='table', package=False) -> None:
        self.connection = Connection(excel_path, table_name=table_name + '$', connection_type=EXCEL_CLASS,
                                     package=package)

    def connect_to_csv(self, csv_path, package=False) -> None:
        table_name = str.replace(csv_path, '.', '#')
        self.connection = Connection(csv_path, table_name=table_name, connection_type=CSV_CLASS, package=package)

    def connect_to_hyper(self, hyper_path, table_name, schema_name, package=False) -> None:
        self.connection = Connection(hyper_path, table_name=table_name, schema_name=schema_name, connection_type=HYPER_CLASS, package=package)

    def to_xml(self) -> etree.Element:
        if self.connection is None:
            raise ValueError("No connection is available to render as XML")
        element = etree.Element('connection')
        element.set('class', 'federated')
        named_connections = etree.SubElement(element, 'named-connections')
        named_connection = etree.SubElement(named_connections, 'named-connection', caption=self.caption, name=self.name)
        named_connection.append(self.connection.to_xml())
        etree.SubElement(element, 'relation',
                         connection=self.name,
                         name=self.connection.get_relation_name(),
                         table=self.connection.get_table_name(),
                         type='table'
                         )
        return element
