from lxml import etree
from lxml.etree import Element


class Column:

    def __init__(self, name='field', role='dimension', type='nominal', datatype='string', semantic_role=None,
                 hidden=False, description='', default_format=None):
        self.name = name
        self.role = role
        self.type = type
        self.datatype = datatype
        self.semantic_role = semantic_role
        self.hidden = hidden
        self.description = description
        self.default_format = default_format

    def get_name(self) -> str:
        """
        Gets the name in its referencable form
        :return: the reference name for the column
        """
        return '[' + self.name + ']'

    def to_xml(self) -> etree.Element:
        element = etree.Element('column', datatype=self.datatype, name=self.get_name(), role=self.role, type=self.type)
        if self.semantic_role is not None:
            element.set('semantic-role', self.semantic_role)
        if self.hidden:
            element.set('hidden', 'true')
        if self.type is not None:
            element.set('type', self.type)
        if self.description:
            desc = etree.SubElement(element, 'desc')
            formatted_text = etree.SubElement(desc, 'formatted-text')
            run = etree.SubElement(formatted_text, 'run')
            run.text = self.description
        if self.default_format is not None:
            element.set("default-format", self.default_format)
        return element


class CalculatedColumn(Column):
    def __init__(self,
                 name='calculation',
                 role='measure',
                 type='quantitative',
                 datatype='real',
                 semantic_role=None,
                 hidden=False,
                 description='',
                 formula='',
                 default_format=None
                 ):
        super().__init__(name=name, role=role, type=type, datatype=datatype, semantic_role=semantic_role, hidden=hidden,
                         description=description, default_format=default_format)
        self.caption = name
        self.formula = formula

    def to_xml(self) -> etree.Element:
        element: Element = super().to_xml()
        element.set("caption", self.caption)
        if self.type is not None:
            element.set('type', self.type)
        calculation: Element = etree.Element('calculation', formula=self.formula)
        element.insert(0, calculation)

        calculation.set('class', 'tableau')
        return element
