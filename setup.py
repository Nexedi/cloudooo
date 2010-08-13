from setuptools import setup, find_packages

version = '1.0.4'

setup(name='cloudooo',
      version=version,
      description="XML-RPC openoffice document convertion server",
      long_description=open("README").read(),
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
      unoconverter.py = cloudooo.bin.unoconverter:main
      unomimemapper.py = cloudooo.bin.unomimemapper:main
      openoffice_tester.py = cloudooo.bin.openoffice_tester:main
      """,
      )
