import os
import shutil

from tableau_builder.hyper_utils import create_hyper_from_csv, check_domain, get_default_table_and_schema, check_range, get_hyper_columns, subset_columns


def test_create_hyper(tmp_path):
    test_output_path = os.path.join(tmp_path, "orders.hyper")
    create_hyper_from_csv('test'+os.sep+'orders.csv', test_output_path, table_name='orders')


def test_check_domain(tmp_path):
    ship_modes = ['Standard Class', 'Second Class', 'Same Day', 'First Class']
    test_output_path = os.path.join(tmp_path, "orders.hyper")
    create_hyper_from_csv('test'+os.sep+'orders.csv', test_output_path, table_name='orders')
    assert check_domain(test_output_path, 'Ship Mode', ship_modes, table_name='orders')
    assert not check_domain(test_output_path, 'Ship Mode', ['apple', 'banana'], table_name='orders')


def test_get_table_names():
    example = os.path.join('test', 'orders.hyper')
    assert get_default_table_and_schema(example)['table'] == 'orders'
    assert get_default_table_and_schema(example)['schema'] == 'public'


def test_check_range(tmp_path):
    test_output_path = os.path.join(tmp_path, "orders.hyper")
    create_hyper_from_csv('test'+os.sep+'orders.csv', test_output_path, table_name='orders')
    assert check_range(hyper_path=test_output_path, field="Discount", min_value=0, max_value=1, table_name='orders')
    assert not check_range(hyper_path=test_output_path, field="Discount", min_value=0, max_value=0.5, table_name='orders')


def test_get_hyper_columns(tmp_path):
    example = os.path.join('test', 'orders.hyper')
    columns = get_hyper_columns(example, 'orders', 'public')
    expected = ['Row ID', 'Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 'Segment', 'Country/Region', 'City', 'State/Province', 'Postal Code', 'Region', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Sales', 'Quantity', 'Discount', 'Profit']
    for column in columns:
        assert column in expected


def test_subset_columns(tmp_path):
    example = os.path.join('test', 'orders.hyper')
    hyper_path = os.path.join(tmp_path, "orders.hyper")
    shutil.copy(example, hyper_path)
    columns_to_keep = ['Order Date', 'Ship Date', 'Ship Mode','Sales']
    subset_columns(columns_to_keep, hyper_path, table_name='orders', schema_name='public')
    columns = get_hyper_columns(hyper_path, 'orders', 'public')
    for column in columns:
        assert column in columns_to_keep
    assert len(columns) == 4
