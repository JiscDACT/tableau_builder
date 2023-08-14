import os

from tableau_builder.tableau import Tableau


def test_tableau():
    if not os.path.exists('output'):
        os.makedirs('output')
    tableau = Tableau()
    tableau.set_csv_location('test/orders.csv')
    tableau.add_measure('Sales')
    tableau.add_dimension('Ship Mode')
    tableau.hide_other_fields()
    tableau.save("output"+os.sep+"test_tableau.tds")


def test_tableau_minimal_csv():
    if not os.path.exists('output'):
        os.makedirs('output')
    tableau = Tableau()
    tableau.set_csv_location('test/orders.csv')
    tableau.save("output"+os.sep+"test_tableau_min.tds")