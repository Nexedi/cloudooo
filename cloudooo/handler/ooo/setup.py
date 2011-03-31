import sys
from setuptools import setup, find_packages

name = "cloudooo.handler.ooo"
version = '0.1'

def read(name):
  return open(name).read()

long_description=(read('README.txt')
                  + '\n' +
                  read('CHANGES.txt')
                 )

install_requires = ["zope.interface",
                    "psutil>=0.2.0",
                    "lxml",
                    "cloudooo"]

if sys.version_info < (2, 5):
  install_require_list.append('simplejson')

setup(
    name = name,
    version = version,
    author = "Gabriel M. Monnerat",
    author_email = "gabriel@tiolive.com",
    description = "Python Package to handler OpenOffice.org Documents",
    long_description=long_description,
    license = "GPL",
    keywords = "Python OpenOffice.org",
    classifiers= [
      "Programming Language :: Python :: 2.6",
      "Natural Language :: English",
    ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ["cloudooo", "cloudooo.handler"],
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    runOOoHandlerUnitTest = cloudooo.handler.ooo.tests.runOOoHandlerUnitTest:run
    """
    )
