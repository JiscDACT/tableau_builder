import os
import shutil
import tempfile

DATA_FOLDER = 'Data'
TABLEAU_PACKAGED_DATASOURCE_EXTENSION = '.tdsx'


def package_tds(
        tds_file,
        data_file='example.xls',
        output_file='datasource',
) -> None:
    """
    Creates a new Tableau packaged data source (.tdsx) from a data source (.tds) and saves it in the location specified
    :param tds_file: path to the TDS file
    :param data_file: path to .csv or .xls
    :param output_file: Name of the output file. Don't include the extension as this is added automatically.
    :return:None
    """
    data_file_filename = os.path.basename(data_file)
    with tempfile.TemporaryDirectory() as archive_folder:
        os.makedirs(archive_folder + os.sep + DATA_FOLDER)
        # Copy the TDS into the archive folder
        shutil.copy(tds_file, os.path.join(archive_folder, os.path.basename(tds_file)))
        # Copy the data into the archive/Data folder
        shutil.copy(data_file, os.path.join(archive_folder, DATA_FOLDER, data_file_filename))
        # Zip the folder and save it as output_file.zip
        shutil.make_archive(output_file, 'zip', archive_folder)
        # Rename it output_file.tdsx
        shutil.move(output_file + '.zip', output_file + TABLEAU_PACKAGED_DATASOURCE_EXTENSION)
        # Delete the archive folder
        shutil.rmtree(archive_folder)