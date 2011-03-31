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
                    "cloudooo"]

setup(
    name = name,
    version = version,
    author = "Gabriel M. Monnerat",
    author_email = "gabriel@tiolive.com",
    description = "Python Package to handler PDF documents",
    long_description=long_description,
    license = "GPL",
    keywords = "python xpdf",
    classifiers=[
      "Programming Language :: Python :: 2.6",
      "Natural Language :: English",
    ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
    namespace_packages = ["cloudooo", "cloudooo.handler"],
    entry_points="""
    [console_scripts]
    runPDFHandlerUnitTest = cloudooo.handler.pdf.tests.runPDFHandlerUnitTest:run
    """,
    )
