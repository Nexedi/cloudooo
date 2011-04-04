from setuptools import setup, find_packages

name = "cloudooo.handler.pdf"
version = '0.1'

def read(name):
  return open(name).read()

long_description=(read('README.txt')
                  + '\n' +
                  read('CHANGES.txt')
                 )

install_requires = ["zope.interface",
                    "cloudooo",
                    "python-magic", # required for unit tests only
                    ]

setup(
    name = name,
    version = version,
    author = "Gabriel M. Monnerat",
    author_email = "gabriel@tiolive.com",
    description = "Python Package to handler PDF documents",
    long_description=long_description,
    license = "GPLv3",
    keywords = "python xpdf",
    classifiers=[
      "Programming Language :: Python :: 2.6",
      "Natural Language :: English",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    packages = find_packages('src'),
    url = 'http://svn.erp5.org/repos/public/erp5/trunk/utils/cloudooo.handler.pdf',
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
    namespace_packages = ["cloudooo", "cloudooo.handler"],
    entry_points="""
    [console_scripts]
    runPDFHandlerUnitTest = cloudooo.handler.pdf.tests.runPDFHandlerUnitTest:run
    """,
    )
