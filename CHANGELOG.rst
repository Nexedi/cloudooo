1.2.4 (unreleased)
==================
  - Move to git and reorganize the code.

1.2.3 (2011-04-01)
==================
  - Eggify handlers
  - Configuration file tells to cloudooo which handler must be loaded
  - Update interface (not implemented yet)

1.2.2 (2011-02-07)
==================
  - No longer use Xvfb.

1.2.1 (2011-01-21)
==================
  - Improve ERP5 compatibility.

1.2.0 (2011-01-19)
==================
  - Support LibreOffice3.3rc3.

1.1.0 (2011-01-13)
===================
  - Refactor runCloudOOoUnitTest.py to control better the daemon process
  - Use argparse instead of optparse
  - Refactor tests to use boolean asserts to validate True or False.
  - Use python-magic to validate the output documents according to mimetype.
  - Change folder structure of cloudooo to put handler, mimemapper, helpers
    related to handler in same folder than handler.
  - Refactor code to use json instead of jsonpickle.
  - Add getTableItem, getTableItemList and getTableMatrix for OOGranulate
  - Add getParagraphItemList and getParagraphItem for OOGranulate
  - Add getImageItemList and getImage for OOGranulate
  - Add OdfDocument
  - Add granulate interface.

1.0.9
=====
  - use pkg_resources to get helper scripts.
  - move internal scripts to helper folder.
  - removed cloudooo as dependency of internal scripts.
  - modified way that the filters of OpenOffice.org are passed.

1.0.8
=====
  - Remove all attributes that works with cloudooo script paths.
  - Use all scripts according to your python eggs.
  - Fixed problem when a spreadsheet will be converted to html.

1.0.7
=====
  - Remove entry points, treat those as ordinary files.
  - Search all script files using pkg_resources.
