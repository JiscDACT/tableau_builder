from typing import Union

from lxml import etree

from tableau_builder.column import Column, CalculatedColumn
from tableau_builder.connection import Federation
from tableau_builder.folder import Folder, Folders, FolderItem
from tableau_builder.hierarchy import Hierarchy

EXCEL_TYPE = 'Excel'
CSV_TYPE = 'csv'
HYPER_TYPE = 'hyper'

class Tableau:

    def __init__(self, name='data source'):
        self.name = name
        self.data_file_path = None
        self.document = None
        self.connection = None
        self.columns = []
        self.hierarchies = []
        self.folders = Folders()

    def set_csv_location(self, file_path) -> None:
        self.create_connection(file_path, connection_type=CSV_TYPE)

    def create_connection(self, file_path, table_name='Sheet1', schema_name='public', connection_type=CSV_TYPE, package=False) -> None:
        self.connection = Federation()
        if connection_type == EXCEL_TYPE:
            self.connection.connect_to_excel(file_path, table_name=table_name, package=package)
        elif connection_type == HYPER_TYPE:
            self.connection.connect_to_hyper(file_path, table_name=table_name, schema_name=schema_name, package=package)
        elif connection_type == CSV_TYPE:
            self.connection.connect_to_csv(file_path, package=package)

    def add_folder(self, name='folder', members=None) -> None:
        if members is None:
            members = []
        folder = Folder(name)
        for member in members:
            if isinstance(member, FolderItem):
                folder.folder_items.append(member)
            else:
                folder.add_field(member)
        self.folders.append(folder)

    def get_column_by_name(self, name) -> Union[str, None]:
        for column in self.columns:
            if column.name == name:
                return column
        return None

    def add_hierarchy(self, hierarchy) -> None:
        columns = []
        for field_name in hierarchy.get_members():
            column = self.get_column_by_name(field_name)
            if column is not None:
                columns.append(column)
        self.hierarchies.append(Hierarchy(name=hierarchy.name, members=columns))

    def hide_field(self, name) -> None:
        column = Column(name=name, hidden=True)
        self.columns.append(column)

    def hide_other_fields(self) -> None:
        # todo make this work with Excel and Hyper too
        if self.connection.connection.class_name == CSV_TYPE:
            for column in self.connection.get_columns():
                if not self.get_column_by_name(column):
                    self.hide_field(column)

    def add_dimension(self, name='field', description=None) -> None:
        self.add_field(name, datatype='string', role='dimension', type='nominal', description=description, default_format=None)

    def add_measure(self, name='field', description=None) -> None:
        self.add_field(name, datatype='real', role='measure', type='quantitative', description=description, default_format=None)

    def add_field(self,
                  name='field',
                  datatype='string',
                  role='dimension',
                  type='nominal',
                  description=None,
                  semantic_role=None,
                  default_format=None,
                  formula=None) -> None:

        # In columns
        if formula is None:
            column = Column(name=name, datatype=datatype, role=role, type=type, semantic_role=semantic_role, description=description, default_format=default_format)
        else:
            column = CalculatedColumn(name=name, datatype=datatype, role=role, type=type, semantic_role=semantic_role, description=description, formula=formula, default_format=default_format)
        self.columns.append(column)

    def save(self, file_path='test.tds') -> None:
        element = etree.Element('datasource', inline='true', version='18.1')
        element.set('source-platform', 'win')
        element.set('formatted-name', self.name)
        manifest = etree.SubElement(element, 'document-format-change-manifest')
        etree.SubElement(manifest, '_.fcp.ObjectModelEncapsulateLegacy.true...ObjectModelEncapsulateLegacy')
        etree.SubElement(manifest, '_.fcp.ObjectModelTableType.true...ObjectModelTableType')
        etree.SubElement(manifest, '_.fcp.SchemaViewerObjectModel.true...SchemaViewerObjectModel')
        element.append(self.connection.to_xml())
        for column in self.columns:
            element.append(column.to_xml())

        # Hierarchies
        if len(self.hierarchies) > 0:
            drill_paths = etree.SubElement(element, 'drill-paths')
            for hierarchy in self.hierarchies:
                drill_paths.append(hierarchy.to_xml())

        # Folders
        for folder in self.folders.folders:
            element.append(folder.to_xml())
        element.append(self.folders.to_xml())

        # Layout
        layout = etree.SubElement(element, 'layout')
        layout.set('show-structure', 'false')
        layout.set('dim-ordering', 'alphabetic')
        layout.set('measure-ordering', 'alphabetic')

        with open(file_path, mode='wb') as file:
            file.write(etree.tostring(element, encoding="UTF-8"))
            file.flush()
