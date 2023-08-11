import os

from tableau_builder.tableau import Tableau


def test_tableau():
    tableau = Tableau()
    tableau.set_csv_location('test/orders.csv')
    tableau.add_measure('Sales')
    tableau.add_dimension('Ship Mode')
    tableau.hide_other_fields()
    tableau.save("test"+os.sep+"test_tableau.tds")


def test_tableau_minimal_csv():
    tableau = Tableau()
    tableau.set_csv_location('test/orders.csv')
    tableau.save("test"+os.sep+"test_tableau_min.tds")