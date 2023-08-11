from lxml import etree


class Hierarchy:

    def __init__(self, name='hierarchy', members=None):
        if members is None:
            members = []
        self.name = name
        self.members = members

    def to_xml(self) -> etree.Element:
        element = etree.Element('drill-path', name=self.name)
        for member in self.members:
            field = etree.SubElement(element, 'field')
            field.text = member.get_name()
        return element
