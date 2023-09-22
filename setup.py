from setuptools import setup

setup(
    name='tableau_builder',
    version='0.15',
    packages=['tableau_builder'],
    url='https://github.com/JiscDACT/tableau-builder',
    license='',
    author='scottw',
    author_email='scott.wilson@jisc.ac.uk',
    description='Programmatically build Tableau packages',
    long_description="Programmatically build Tableau packages",
    include_package_data=True,
    package_data={
        # If any package contains *.ini files, include them
        '': ['*.ini']
    },
    install_requires=['pandas', 'lxml', 'openpyxl']
)