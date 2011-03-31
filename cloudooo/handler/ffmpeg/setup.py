from setuptools import setup, find_packages

name = "cloudooo.handler.ffmpeg"
version = '0.1'

def read(name):
  return open(name).read()

long_description=(read('README.txt')
                  + '\n' +
                  read('CHANGES.txt')
                 )

install_requires = ["zope.interface",
                    "cloudooo",]

setup(
    name = name,
    version = version,
    author = "Gabriel M. Monnerat",
    author_email = "gabriel@tiolive.com",
    description = "Python Package to handle Videos",
    long_description=long_description,
    license = "GPL",
    keywords = "python ffmpeg",
    classifiers=[
      "Programming Language :: Python :: 2.6",
      "Natural Language :: English",
    ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    namespace_packages = ["cloudooo", "cloudooo.handler"],
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    runFFMPEGHandlerUnitTest = cloudooo.handler.ffmpeg.tests.runFFMPEGHandlerUnitTest:run
    """,
    )
