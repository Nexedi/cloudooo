from setuptools import setup, find_packages
from os import path

version = '1.0.9'

folder_path = path.abspath(path.dirname(__file__)) + "/cloudooo"

long_description = "%s\n%s" % (open(path.join(folder_path, "README.txt")).read(), 
		               open(path.join(folder_path, "CHANGES.txt")).read()) 
setup(name='cloudooo',
      version=version,
      description="XML-RPC openoffice document convertion server",
      long_description=long_description,
      classifiers=["Topic :: System :: Networking",
        "Topic :: System :: Operating System Kernels :: Linux",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Programming Language :: Python :: 2.6",
        "Natural Language :: English",
        "Framework :: Paste"],
      keywords='xmlrpc openoffice wsgi paste python',
      author='Gabriel M. Monnerat',
      author_email='gabriel@tiolive.com',
      url='https://svn.erp5.org/repos/public/erp5/trunk/utils/cloudooo',
      license='GPL 2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'zope.interface',
          'PasteDeploy',
          'PasteScript',
          'WSGIUtils',
          'jsonpickle',
          'psutil',
      ],
      entry_points="""
      [paste.app_factory]
      main = cloudooo.cloudooo:application
      [console_scripts]
      cloudooo_tester = cloudooo.bin.cloudooo_tester:main
      """,
      )
