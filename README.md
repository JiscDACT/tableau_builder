# Tableau dataset builder

A package for programmatically creating Tableau data source (.tds) and packaged data source (.tdsx) files.

## Method 1: Using a JSON manifest

The package turns a JSON structure representing a dataset into a .tds or .tdsx output.

The JSON model consists of:

- The link to the data source file (CSV or Excel)
- A link to additional metadata (optional)
- A list of measures
- A list of dimensions
- groups of fields to represent as folders
- hierarchies of related dimensions

There is an example JSON file in the `example` folder.

Below is a minimal example, using the sample data file and
JSON model:

~~~~ python
from tableau_metadata.dataset import create_tdsx

create_tdsx(
    metadata_file='example' + os.sep + 'metadata.json',
    dataset_file='example' + os.sep + 'dataset.json',
    data_file='example' + os.sep + 'orders.csv',
    output_file='output' + os.sep + 'test_create_tdsx'
)
~~~~

This will create a packaged data source from the example.

## Method 2: Using the API to build a data source

You can also build data sources directly using the Tableau class.

The following is a minimal example of creating a .tds:

~~~~ python
    tableau = Tableau()
    tableau.set_csv_location('example/orders.csv')
    tableau.add_measure('Sales')
    tableau.add_dimension('Ship Mode')
    tableau.hide_other_fields()
    tableau.save("output"+os.sep+"test_tableau.tds")
~~~~

## Method 3: Convert a CSV directly to a .tdsx

The simplest possible approach is to directly convert a
CSV file into a Tableau Packaged Data Source in one step.
This will include all the fields in the CSV without any
additional metadata.

~~~~ python
    create_tdsx_from_csv(data_file='orders.csv', output_file='datasource')
~~~~