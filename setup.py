from setuptools import setup, find_packages
import sys

version = '1.2.5-dev'

def read(name):
    return open(name).read()

long_description = (read('README.txt') + '\n' + read('CHANGES.txt'))

install_requires = [
          # -*- Extra requirements: -*-
          'zope.interface',
          'PasteDeploy',
          'PasteScript',
          'WSGIUtils',
          'psutil>=3.0.0',
          'lxml',
          'python-magic',
          'argparse',
          'erp5.util'
          ]

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
      url = 'http://git.erp5.org/gitweb/cloudooo.git',
      license='GPLv3',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      [paste.app_factory]
      main = cloudooo.paster_application:application
      [console_scripts]
      cloudooo_tester = cloudooo.bin.cloudooo_tester:main
      echo_cloudooo_conf = cloudooo.bin.echo_cloudooo_conf:main
      runCloudoooUnitTest = cloudooo.tests.runHandlerUnitTest:run
      """,
      )
