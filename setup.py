from distutils.core import setup

setup(
    name='EvePrices',
    version='0.0.1',
    author='Alexander Blair (Feanos)',
    author_email='alex@snipanet.com',
    packages=['eveprices'],
    scripts=[],
    url='http://snipanet.com',
    license='LICENSE.txt',
    description='Eve-Online Price Aggrigator in Python',
    long_description=open('README.md').read(),
    install_requires=[
        "pylibmc",
        "xmltodict",
    ],
)