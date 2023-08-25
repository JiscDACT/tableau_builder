# <_.fcp.SchemaViewerObjectModel.false...folder name='Shipping' role='dimensions'>
#   <folder-item name='[Ship Date]' type='field' />
#   <folder-item name='[Ship Mode]' type='field' />
# </_.fcp.SchemaViewerObjectModel.false...folder>

from lxml import etree


class FolderItem:
    def __init__(self, name='[Item]', item_type='field'):
        self.name = name
        self.item_type = item_type
        if self.item_type == 'field' and not str.startswith(self.name, '['):
            self.name = '[' + self.name + ']'

    def to_xml(self):
        return etree.Element('folder-item', name=self.name, type=self.item_type)


class Folder:
    def __init__(self, name, role='dimensions'):
        if name is None:
            raise ValueError("Folder must have a name")
        self.name = name
        self.role = role
        self.folder_items = []

    def add_field(self, field_name: str) -> None:
        folder_item = FolderItem(name='['+field_name+']')
        self.folder_items.append(folder_item)

    def to_xml(self) -> etree.Element:
        element = etree.Element('_.fcp.SchemaViewerObjectModel.false...folder', name=self.name, role=self.role)

        for item in self.folder_items:
            element.append(item.to_xml())

        return element


class Folders:

    def __init__(self):
        self.folders = []

    def append(self, folder) -> None:
        self.folders.append(folder)

    def to_xml(self) -> etree.Element:
        element = etree.Element('_.fcp.SchemaViewerObjectModel.true...folders-common')
        for folder in self.folders:
            folder_element = etree.SubElement(element, 'folder', name=folder.name)
            for item in folder.folder_items:
                folder_element.append(item.to_xml())

        return element



