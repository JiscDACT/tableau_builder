import os

from tableau_builder.dataset import create_tdsx, create_tdsx_from_csv, create_tds, create_tdsx_from_excel, create_tdsx_from_hyper
from tableau_builder.package import package_tds
from tableau_builder.tableau import Tableau


def test_create_tdsx_from_examples(json_repository):

    if not os.path.exists('output'):
        os.makedirs('output')

    output_path = os.path.join('output', 'test_create_tdsx')

    create_tdsx(
        metadata_repository=json_repository,
        dataset_file='test' + os.sep + 'dataset.json',
        data_file='test' + os.sep + 'orders.csv',
        output_file=output_path,
        data_source_type='csv'
    )

    assert os.path.exists(output_path + '.tdsx')


def test_create_tdsx_without_additional_metadata():

    if not os.path.exists('output'):
        os.makedirs('output')

    create_tdsx(
        dataset_file='test' + os.sep + 'dataset.json',
        data_file='test' + os.sep + 'orders.csv',
        output_file='output' + os.sep + 'test_create_tdsx_no_meta',
        data_source_type='csv'
    )


def test_package():
    data_file = 'test' + os.sep + 'orders.csv'
    tds_file = "output" + os.sep + "output.tds"

    tableau = Tableau()
    tableau.create_connection(file_path=data_file, connection_type='csv',
                              package=True)
    tableau.add_measure('Sales')
    tableau.add_dimension('Ship Mode')
    tableau.hide_other_fields()
    tableau.save(tds_file)
    package_tds(tds_file, data_file=data_file, output_file='output' + os.sep + 'test_package_tds')


def test_minimal_csv_package():
    create_tdsx_from_csv(data_file='test' + os.sep + 'orders.csv', output_file='output' + os.sep + 'test_minimal_csv')


def test_create_tdsx_using_metadata(json_repository):

    if not os.path.exists('output'):
        os.makedirs('output')

    create_tdsx(
        metadata_repository=json_repository,
        dataset_file='test' + os.sep + 'dataset_min.json',
        data_file='test' + os.sep + 'orders.csv',
        output_file='output' + os.sep + 'test_create_tdsx_using_metadata',
        data_source_type='csv',
        use_metadata_groups=True
    )


def test_create_tds(csv_path, tmp_path, json_repository):
    dataset_file = os.path.join(tmp_path, "dataset.json")
    output_file = os.path.join(tmp_path, "test.tds")

    with open(dataset_file, "w") as f:
        f.write('{"dimensions": ["Ship Mode"], "measures": ["Sales"]}')

    create_tds(
        metadata_repository=json_repository,
        dataset_file=dataset_file,
        data_file=csv_path,
        table_name="Orders",
        data_source_type="csv",
        output_file=output_file,
    )

    assert os.path.exists(output_file)


def test_create_tdsx(csv_path, tmp_path, json_repository):
    dataset_file = os.path.join(tmp_path,"dataset.json")
    output_file = os.path.join(tmp_path, "test_create_tdsxr")

    with open(dataset_file, "w") as f:
        f.write('{"dimensions": ["Ship Mode"], "measures": ["Category"]}')

    create_tdsx(
        dataset_file=dataset_file,
        metadata_repository=json_repository,
        data_file=csv_path,
        table_name="Orders",
        data_source_type="csv",
        output_file=output_file,
    )

    assert os.path.exists(output_file + '.tdsx')


def test_create_tdsx_from_csv(csv_path, tmp_path):
    output_file = os.path.join(tmp_path, "test_create_tdsx_from_csv")
    create_tdsx_from_csv(data_file=csv_path, output_file=output_file)

    assert os.path.exists(output_file + '.tdsx')


def test_create_tdsx_from_excel(excel_path, tmp_path):
    output_file = os.path.join(tmp_path, "test_create_tdsx_from_excel")
    create_tdsx_from_excel(data_file=excel_path, output_file=output_file, sheet_name='Sheet1')

    assert os.path.exists(output_file + '.tdsx')


def test_create_tdsx_from_hyper():
    output_file = os.path.join('output', 'test_create_tdsx_from_hyper')
    create_tdsx_from_hyper(
        data_file='test' + os.sep + 'orders.hyper',
        output_file=output_file,
        table_name='orders',
        schema='public'
    )
    assert os.path.exists(output_file + '.tdsx')


def test_create_tds_using_hyper(csv_path, tmp_path, json_repository):
    dataset_file = os.path.join(tmp_path, "dataset.json")
    output_file = os.path.join('output', "test_create_tds_using_hyper.tds")

    with open(dataset_file, "w") as f:
        f.write('{"dimensions": ["Ship Mode"], "measures": ["Sales"]}')

    create_tds(
        metadata_repository=json_repository,
        dataset_file=dataset_file,
        data_file='test' + os.sep + 'orders.hyper',
        table_name="orders",
        data_source_type="hyper",
        output_file=output_file,
    )

    assert os.path.exists(output_file)


def test_create_tdsx_using_hyper(csv_path, tmp_path, json_repository):
    dataset_file = os.path.join(tmp_path,"dataset.json")
    output_file = os.path.join('output', "test_create_tdsx_using_hyper")

    with open(dataset_file, "w") as f:
        f.write('{"dimensions": ["Ship Mode"], "measures": ["Category"]}')

    create_tdsx(
        dataset_file=dataset_file,
        metadata_repository=json_repository,
        data_file='test' + os.sep + 'orders.hyper',
        table_name="orders",
        data_source_type="hyper",
        output_file=output_file,
    )

    assert os.path.exists(output_file + '.tdsx')


def test_create_tds_using_virtual_hyper(csv_path, tmp_path, json_repository):
    """
    Test we can still create a TDS even if we can't actually connect to the .hyper
    """
    dataset_file = os.path.join(tmp_path, "dataset.json")
    output_file = os.path.join('output', "test_create_tds_using_virtual_hyper.tds")

    with open(dataset_file, "w") as f:
        f.write('{"dimensions": ["Ship Mode"], "measures": ["Sales"]}')

    create_tds(
        metadata_repository=json_repository,
        dataset_file=dataset_file,
        data_file='\\\\server-name\\shared-resource-pathname\\data.hyper',
        table_name="orders",
        data_source_type="hyper",
        output_file=output_file,
    )

    assert os.path.exists(output_file)