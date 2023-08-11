import os

import pytest
import pandas as pd

from tableau_builder.json_metadata import JsonRepository


@pytest.fixture
def csv_path(tmp_path):
    csv_path = tmp_path / "test.csv"
    csv_data = "col1,col2\n1,a\n2,b\n3,c"
    csv_path.write_text(csv_data)
    return str(csv_path)


@pytest.fixture
def excel_path(tmp_path):
    excel_path = tmp_path / "test.xlsx"
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    df.to_excel(excel_path, index=False)
    return str(excel_path)


@pytest.fixture
def json_repository():
    return JsonRepository(repository_path='test' + os.sep + 'metadata.json')
