from setuptools import setup

setup(
    name='temponet',
    version='0.0.1',
    description='Offers planning capabilities via simple temporal network.',
    author='Alexandre Angleraud',
    author_email='alexandre.angleraud@tuni.fi',
    download_url='https://github.com/Zorrander/temponet/archive/v0.0.1.tar.gz',
    license='New BSD License',
    test_suite="tests",
    install_requires=[
     'networkx'
    ],
    packages=[
     'simple_net'
    ]
)
