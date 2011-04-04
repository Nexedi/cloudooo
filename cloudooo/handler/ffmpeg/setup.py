from setuptools import setup, find_packages

name = "cloudooo.handler.ffmpeg"
version = '0.1'


def read(name):
  return open(name).read()

long_description = (read('README.txt') + '\n' + read('CHANGES.txt'))

install_requires = ["zope.interface",
                    "cloudooo",
                    "python-magic", # required for unit tests only
                    ]

setup(
  name = name,
  version = version,
  author = "Gabriel M. Monnerat",
  author_email = "gabriel@tiolive.com",
  description = "Python Package to handle Videos",
  long_description=long_description,
  license = "GPLv3",
  keywords = "python ffmpeg",
  classifiers=[
    "Programming Language :: Python :: 2.6",
    "Natural Language :: English",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "License :: OSI Approved :: GNU General Public License (GPL)",
  ],
  packages = find_packages('src'),
  package_dir = {'': 'src'},
  url = 'http://svn.erp5.org/repos/public/erp5/trunk/utils/cloudooo.handler.ffmpeg',
  include_package_data = True,
  namespace_packages = ["cloudooo", "cloudooo.handler"],
  install_requires=install_requires,
  entry_points="""
  [console_scripts]
  runFFMPEGHandlerUnitTest = cloudooo.handler.ffmpeg.tests.runFFMPEGHandlerUnitTest:run
  """,)
