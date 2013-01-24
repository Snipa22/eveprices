from distutils.core import setup

setup(
    name='EvePrices',
    version='0.0.1',
    author='Alexander Blair (Feanos)',
    author_email='alex@snipanet.com',
    packages=['eveprices'],
    scripts=['bin/eveprices.py'],
    url='http://snipanet.com',
    license='LICENSE.txt',
    description='Eve-Online Price Aggrigator in Python',
    long_description=open('README.txt').read(),
    install_requires=[
        "pylibmc",
        "xmltodict",
    ],
)