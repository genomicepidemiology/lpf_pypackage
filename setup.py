from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

from lpf.version import __version__

setup(
    name='lpf_pypackage',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=__version__,
    packages=find_packages(),
    data_files=[],
    include_package_data=True,
    url='https://https://https://github.com/genomicepidemiology/LPF_package',
    license='',
    install_requires=(),
    author='Malte B. Hallgren',
    scripts=['bin/lpf'],
    author_email='malhal@food.dtu.dk',
    description='LPF - Local Pathogen Finder'
)
