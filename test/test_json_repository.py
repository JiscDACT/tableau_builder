import os

from tableau_builder.json_metadata import JsonRepository

TEST_META_PATH = 'test' + os.sep + 'metadata.json'


def test_json_repository():
    json_repository = JsonRepository(repository_path=TEST_META_PATH)
    assert json_repository.get_metadata('Order Identifier') is not None
    assert json_repository.get_metadata('Order Identifier').name == 'Order Identifier'


def test_hierarchies():
    json_repository = JsonRepository(repository_path=TEST_META_PATH)
    hierarchy = json_repository.get_hierarchies_for_items(['City', 'Region'])
    print(hierarchy)
