import logging

logger = logging.getLogger(__name__)

"""
Base API for an extract from a metadata repository
"""


class RepositoryItem:
    """
    A metadata item in a collection
    """
    def __init__(self,
                 name=None,
                 description=None,
                 formula=None,
                 groups=None,
                 default_format=None,
                 semantic_role=None,
                 domain=None,
                 range=None
                 ):
        self.name = name
        self.description = description
        self.formula = formula
        self.groups = groups
        self.range = range
        self.hierarchies = []
        self.physical_column_name = None
        self.default_format = default_format
        self.semantic_role = semantic_role
        self.domain = domain


class Hierarchy:
    """
    A hierarchy, or drill-down path, of related items
    """
    def __init__(self, name):
        self.name = name
        self.items = []

    def set_members(self, members: [str]) -> None:
        logger.debug("Setting members of hierarchy")
        level = 0
        for member in members:
            level += 10
            item = HierarchyItem(name=member, level=level)
            self.items.append(item)

    def get_members(self) -> [str]:
        members = []
        self.items.sort(key=self.sort_on_levels)
        for item in self.items:
            members.append(item.name)
        return members

    def sort_on_levels(self, item) -> int:
        """
        Sort method for hierarchies
        :param item:
        :return:
        """
        return item.level


class HierarchyItem:
    """
    An item in a hierarchy
    """
    def __init__(self, name=None, level=0):
        self.name = name
        self.level = level


class Collection:
    """
    A collection of related metadata items
    """
    def __init__(self, name=None):
        self.name = name
        self.items = {}

    def get_metadata(self, name) -> RepositoryItem:
        """
        Get a single metadata item by item name
        :param name: the name of the item
        :return: the metadata item as a RepositoryItem
        """
        if name in self.items.keys():
            return self.items.get(name)
        else:
            raise ValueError(name + ' not found in collection ' + self.name)


class BaseRepository:

    def __init__(self):
        self.collections = {}
        self.__add_collection__('default')

    def __add_collection__(self, name):
        logger.debug("Adding collection "+name)
        collection = Collection(name=name)
        self.collections[name] = collection

    def __get_collection__(self, collection) -> Collection:
        if collection in self.collections:
            return self.collections[collection]
        else:
            raise ValueError(collection + ' not found in repository')

    def get_metadata(self, name, collection='default') -> RepositoryItem:
        data_collection = self.__get_collection__(collection)
        return data_collection.get_metadata(name)

    def __add_item__(self, item: RepositoryItem, collection='default') -> None:
        logger.debug("Adding item to collection " + collection)
        data_collection = self.__get_collection__(collection)
        if item is None:
            raise ValueError("No item provided")
        if item.name in data_collection.items:
            raise ValueError(item.name + ' already exists in repository')
        data_collection.items[item.name] = item

    def get_hierarchies_for_items(self, names: [str], collection='default') -> [Hierarchy]:
        data_collection = self.__get_collection__(collection)
        hierarchies = {}
        for name in names:
            item = data_collection.get_metadata(name)
            if item.hierarchies is not None:
                for hierarchy in item.hierarchies:
                    hierarchy_item = HierarchyItem(level=hierarchy.level, name=item.name)
                    if hierarchy.name in hierarchies:
                        hierarchies[hierarchy.name].items.append(hierarchy_item)
                    else:
                        hierarchies[hierarchy.name] = Hierarchy(hierarchy.name)
                        hierarchies[hierarchy.name].items.append(hierarchy_item)
        return list(hierarchies.values())

