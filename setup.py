from distutils.core import setup

setup(
        name='chube',
        version='0.1.12',
        author='Exosite',
        author_email='danslimmon@exosite.com',
        packages=['chube'],
        scripts=['bin/chuber.py'],
        url='http://pypi.python.org/pypi/chube/',
        license='LICENSE.txt',
        description='Object-oriented bindings for the Linode API',
        long_description=open('README.md').read(),
        install_requires=[
            "linode-python >= 1.0",
            "PyYAML >= 3.10",
            "pycurl >= 7.10"
        ],
)
