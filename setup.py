from setuptools import setup, find_packages
from os import path
import sys

version = '1.2.3'

folder_path = path.abspath(path.dirname(__file__)) + "/cloudooo"

long_description = "%s\n%s" % (open(path.join(folder_path, "README.txt")).read(),
                               open(path.join(folder_path, "CHANGES.txt")).read())
install_requires = [
          # -*- Extra requirements: -*-
          'zope.interface',
          'PasteDeploy',
          'PasteScript',
          'WSGIUtils',
          'psutil>=0.2.0',
         ]

test_requires = [
    'python-magic',
    ]

if sys.version_info < (2, 7):
  install_requires.append('argparse')

setup(name='cloudooo',
      version=version,
      description="XML-RPC document conversion server",
      long_description=long_description,
      classifiers=[
        "Topic :: System :: Networking",
        "Topic :: System :: Operating System Kernels :: Linux",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Programming Language :: Python :: 2.6",
        "Natural Language :: English",
        "Framework :: Paste"],
      keywords='xmlrpc openoffice wsgi paste python',
      author='Gabriel M. Monnerat',
      author_email='gabriel@tiolive.com',
      url = 'http://svn.erp5.org/repos/public/erp5/trunk/utils/cloudooo',
      license='GPLv3',
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      test_requires=test_requires,
      entry_points="""
      [paste.app_factory]
      main = cloudooo.paster_application:application
      [console_scripts]
      cloudooo_tester = cloudooo.bin.cloudooo_tester:main
      echo_cloudooo_conf = cloudooo.bin.echo_cloudooo_conf:main
      """,
      )
