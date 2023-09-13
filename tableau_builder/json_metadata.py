import json
import logging
import os

from tableau_builder.metadata import BaseRepository, RepositoryItem, HierarchyItem

logger = logging.getLogger(__name__)


class JsonRepository(BaseRepository):
    """
    A metadata repository that reads data from a JSON file.

    The class inherits from `BaseRepository` and implements its abstract methods. The JSON file must contain a
    'datasource' object with a 'fields' array, where each object represents a field in the metadata. The object
    must have a 'fieldName' and a 'description', and may have optional 'groups', 'formula', and 'hierarchies'
    properties.

    The `JsonRepository` constructor takes a `repository_path` argument that specifies the path to the JSON file.
    If the path is not specified or does not exist, a `ValueError` is raised. The metadata in the file is loaded
    using the `json` module and parsed into `RepositoryItem` objects.
    """

    def __init__(self, repository_path=None):
        super().__init__()
        if repository_path is None or not os.path.exists(repository_path):
            raise ValueError("No valid repository path specified")

        with open(repository_path) as file:
            metadata = json.load(file)

        collection_name = 'default'

        if 'collection' not in metadata:
            raise ValueError("The metadata file is invalid")

        if 'name' in metadata['collection']:
            collection_name = metadata['collection']['name']
            self.__add_collection__(collection_name)

        for field in metadata['collection']['items']:
            groups = None
            formula = None
            default_format = None
            domain = None
            _range = None
            if 'groups' in field:
                groups = field['groups']

            if 'formula' in field:
                formula = field['formula']

            if 'default_format' in field:
                default_format = field['default_format']

            if 'domain' in field:
                domain = field['domain']

            if 'range' in field:
                _range = field['range']

            item = RepositoryItem(
                name=field['name'],
                description=field['description'],
                groups=groups,
                formula=formula,
                default_format=default_format,
                domain=domain,
                range=_range
            )
            if 'hierarchies' in field:
                for hierarchy in field['hierarchies']:
                    hierarchy_item = HierarchyItem(name=hierarchy['hierarchy'], level=hierarchy['level'])
                    item.hierarchies.append(hierarchy_item)

            if 'physical_column_name' in field:
                item.physical_column_name = field['physical_column_name']

            # Add to default collection
            self.__add_item__(item)
            # Add to specified collection
            self.__add_item__(item, collection=collection_name)

        logger.debug("Json repository initialized")
