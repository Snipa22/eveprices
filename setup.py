from distutils.core import setup

setup(
    name='EvePrices',
    version='0.0.2',
    author='Alexander Blair (Impala59)',
    author_email='alex@snipanet.com',
    packages=['eveprices'],
    scripts=[],
    url='http://snipanet.com',
    license='LICENSE.txt',
    description='Eve-Online Price Aggregator in Python',
    long_description=open('README.md').read(),
    install_requires=[
        "couchbase",
        "xmltodict",
    ],
)