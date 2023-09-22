import json
import os
from tempfile import NamedTemporaryFile

from tableau_builder.folder import FolderItem
from tableau_builder.metadata import RepositoryItem, Hierarchy, BaseRepository
from tableau_builder.package import package_tds
from tableau_builder.tableau import Tableau


TABLEAU_DATASOURCE_EXTENSION = '.tds'
CSV = 'csv'
EXCEL = 'Excel'
HYPER = 'hyper'


def create_tdsx_from_hyper(data_file=None, output_file=None, table_name='table', schema='public'):
    """
    Creates a Tableau Packaged Data Source (.tdsx) from the hyper file path supplied, and saves it
    at the specified location. Raises ValueError if either is not supplied, and FileNotFoundError
    if the data file does not exist.
    :param data_file: the path to the hyper data file
    :param output_file: the path to save the .tdsx
    :param table_name: the name of the table in the .hyper
    :param schema: the schema of the table, 'public' by default
    :return: None
    """
    if data_file is None or output_file is None:
        raise ValueError("Both a data file and an output path must be specified")
    if not os.path.exists(data_file):
        raise FileNotFoundError("Cannot find the CSV data file specified")
    with NamedTemporaryFile(suffix='.tds', prefix=os.path.basename(__file__)) as tf:
        tds = tf.name
        tableau = Tableau()
        tableau.create_connection(file_path=data_file, package=True, table_name=table_name, schema_name=schema, connection_type=HYPER)
        tableau.save(tds)
        package_tds(tds, data_file=data_file, output_file=output_file)


def create_tdsx_from_excel(data_file=None, output_file=None, sheet_name='sheet1'):
    """
    Creates a Tableau Packaged Data Source (.tdsx) from the csv file path supplied, and saves it
    at the specified location. Raises ValueError if either is not supplied, and FileNotFoundError
    if the data file does not exist.
    :param sheet_name: the sheet in the Excel workbook to use
    :param data_file: the path to the CSV data file
    :param output_file: the path to save the .tdsx
    :return: None
    """
    if data_file is None or output_file is None:
        raise ValueError("Both a data file and an output path must be specified")
    if not os.path.exists(data_file):
        raise FileNotFoundError("Cannot find the CSV data file specified")
    with NamedTemporaryFile(suffix='.tds', prefix=os.path.basename(__file__)) as tf:
        tds = tf.name
        tableau = Tableau()
        tableau.create_connection(file_path=data_file, package=True, table_name=sheet_name, connection_type=EXCEL)
        tableau.save(tds)
        package_tds(tds, data_file=data_file, output_file=output_file)


def create_tdsx_from_csv(data_file=None, output_file=None):
    """
    Creates a Tableau Packaged Data Source (.tdsx) from the csv file path supplied, and saves it
    at the specified location. Raises ValueError if either is not supplied, and FileNotFoundError
    if the data file does not exist.
    :param data_file: the path to the CSV data file
    :param output_file: the path to save the .tdsx
    :return: None
    """
    if data_file is None or output_file is None:
        raise ValueError("Both a data file and an output path must be specified")
    if not os.path.exists(data_file):
        raise FileNotFoundError("Cannot find the CSV data file specified")
    with NamedTemporaryFile(suffix='.tds', prefix=os.path.basename(__file__)) as tf:
        tds = tf.name
        tableau = Tableau()
        tableau.create_connection(file_path=data_file, package=True)
        tableau.save(tds)
        package_tds(tds, data_file=data_file, output_file=output_file)


def create_tdsx(
        dataset_file,
        metadata_repository=None,
        data_file='example.xls',
        table_name='Orders',
        schema_name='public',
        data_source_type=CSV,
        output_file='datasource',
        hide_unused=True,
        use_metadata_groups=True
) -> None:
    """
    Creates a new Tableau packaged data source (.tdsx) and saves it in the location specified
    :param schema_name: name of the schema if using hyper
    :param use_metadata_groups: if true, generates folders/groups from metadata
    :param metadata_repository: metadata repository object
    :param dataset_file: dataset description file path
    :param data_file: path to .csv or .xls or .hyper
    :param table_name: name of the sheet containing data for Excel, or table in Hyper
    :param data_source_type: 'Excel' or 'csv'
    :param output_file: Name of the output file. Don't include the extension as this is added automatically.
    :param hide_unused: if True, hide any fields not explicitly included
    :return:None
    """
    create_tds(metadata_repository=metadata_repository,
               dataset_file=dataset_file,
               data_file=data_file,
               output_file=output_file + TABLEAU_DATASOURCE_EXTENSION,
               table_name=table_name,
               schema_name=schema_name,
               data_source_type=data_source_type,
               hide_unused=hide_unused,
               package=True,
               use_metadata_groups=use_metadata_groups)
    package_tds(tds_file=output_file + TABLEAU_DATASOURCE_EXTENSION,
                data_file=data_file,
                output_file=output_file)


def create_tds(
        metadata_repository: BaseRepository = None,
        dataset_file=None,
        data_file='example.xls',
        table_name='Orders',
        schema_name='public',
        data_source_type=CSV,
        output_file='test2.tds',
        package=False,
        hide_unused=True,
        use_metadata_groups=True
) -> None:
    """
    Creates a new Tableau data source (.tds) and saves it in the location specified
    :param use_metadata_groups: if true, generates folders/groups from metadata
    :param metadata_repository: the metadata repository
    :param hide_unused: if True, hide any fields not explicitly included
    :param dataset_file: dataset description file path
    :param data_file: path to .csv or .xls or .hyper
    :param schema_name: name of the schema if using a .hyper
    :param table_name: name of the sheet containing data for Excel, or table in Hyper
    :param data_source_type: 'Excel' or 'csv'
    :param output_file: Name of the output file. Don't include the extension as this is added automatically.
    :param package: True if the TDS is being created for a TDSX package, otherwise False
    :return: None
    """
    with open(dataset_file) as file:
        manifest = json.load(file)

    tableau = Tableau()
    tableau.create_connection(
        file_path=data_file,
        table_name=table_name,
        connection_type=data_source_type,
        package=package,
        schema_name=schema_name
    )

    # Dimensions
    if 'fields' in manifest['dimensions']:
        dimensions = manifest['dimensions']['fields']
    else:
        dimensions = manifest['dimensions']

    for dimension in dimensions:
        if metadata_repository is not None:
            item = metadata_repository.get_metadata(dimension)
            add_field(tableau, item, 'dimension')
        else:
            item = RepositoryItem(name=dimension, description=dimension)
            add_field(tableau, item, 'dimension')

    # Measures
    if 'fields' in manifest['measures']:
        measures = manifest['measures']['fields']
    else:
        measures = manifest['measures']

    for measure in measures:
        if metadata_repository is not None:
            item = metadata_repository.get_metadata(measure)
            add_field(tableau, item, 'measure', datatype='real', type='quantitative')
        else:
            item = RepositoryItem(name=measure, description=measure)
            add_field(tableau, item, 'measure', datatype='real', type='quantitative')

    fields = measures + dimensions

    # Hierarchies
    if 'hierarchies' in manifest:
        for hierarchy in manifest['dimensions']['hierarchies']:
            hierarchy_object = Hierarchy(hierarchy['name'])
            hierarchy_object.set_members(hierarchy['members'])
            tableau.add_hierarchy(hierarchy_object)
    else:
        if metadata_repository is not None:
            for hierarchy in metadata_repository.get_hierarchies_for_items(fields):
                tableau.add_hierarchy(hierarchy)

    # Folders
    if use_metadata_groups and metadata_repository is not None:
        groups = {}
        for field in fields:
            item = metadata_repository.get_metadata(field)
            if item.groups is not None:
                item_to_add = FolderItem(item.name)
                if item.hierarchies is not None and len(item.hierarchies)>0:
                    item_to_add = FolderItem(item.hierarchies[0].name, 'drillpath')
                for group in item.groups:
                    if group in groups:
                        if not any(member.name == item_to_add.name for member in groups[group]):
                            groups[group].append(item_to_add)
                    else:
                        groups[group] = [item_to_add]
        for group in groups:
            tableau.add_folder(group, groups[group])
    else:
        if 'groups' in manifest['dimensions']:
            for group in manifest['dimensions']['groups']:
                tableau.add_folder(group['name'], group['members'])

    # Hide unused fields
    if hide_unused:
        tableau.hide_other_fields()

    tableau.save(output_file)


def add_field(tableau, field, role, datatype='string', type='nominal') -> None:
    tableau.add_field(
        name=field.name,
        role=role,
        description=field.description,
        formula=field.formula,
        datatype=datatype,
        type=type,
        default_format=field.default_format,
        semantic_role=field.semantic_role
    )
