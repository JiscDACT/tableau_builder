from tableau_builder.connection import Federation


def test_csv_connection(csv_path):
    # Test connecting to CSV file and retrieving columns
    fed = Federation()
    fed.connect_to_csv(csv_path)
    assert fed.get_columns() == ['col1', 'col2']


def test_excel_connection(excel_path):
    # Test connecting to Excel file and retrieving columns
    fed = Federation()
    fed.connect_to_excel(excel_path)
    print(fed.get_columns())
    assert fed.get_columns() == ['col1', 'col2']

