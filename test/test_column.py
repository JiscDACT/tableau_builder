from lxml import etree

from tableau_builder.column import Column, CalculatedColumn


def test_column_name():
    col = Column(name='test')
    assert col.get_name() == '[test]'


def test_calculated_column_formula():
    calc_col = CalculatedColumn(formula='SUM([test])')
    assert etree.tostring(calc_col.to_xml()) == b'<column datatype="real" name="[calculation]" role="measure" type="quantitative" caption="calculation"><calculation formula="SUM([test])" class="tableau"/></column>'


def test_column_description():
    col = Column(description='This is a test description.')
    expected_xml = b'<column datatype="string" name="[field]" role="dimension" type="nominal"><desc><formatted-text><run>This is a test description.</run></formatted-text></desc></column>'
    assert etree.tostring(col.to_xml()) == expected_xml


def test_calculated_column_type():
    calc_col = CalculatedColumn(type='nominal')
    assert etree.tostring(calc_col.to_xml()) == b'<column datatype="real" name="[calculation]" role="measure" type="nominal" caption="calculation"><calculation formula="" class="tableau"/></column>'


def test_column_semantic_role():
    col = Column(semantic_role='city')
    expected_xml = b'<column datatype="string" name="[field]" role="dimension" type="nominal" semantic-role="city"/>'
    assert etree.tostring(col.to_xml()) == expected_xml


def test_column_format():
    col = Column(name='Percentage', default_format='p0%', datatype='real', type="quantitative")
    expected_xml = b'<column datatype="real" name="[Percentage]" role="dimension" type="quantitative" default-format="p0%"/>'
    assert etree.tostring(col.to_xml()) == expected_xml


def test_calculated_column_hidden():
    calc_col = CalculatedColumn(hidden=True)
    assert etree.tostring(calc_col.to_xml()) == b'<column datatype="real" name="[calculation]" role="measure" type="quantitative" hidden="true" caption="calculation"><calculation formula="" class="tableau"/></column>'
