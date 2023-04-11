##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Gabriel M. Monnerat <gabriel@tiolive.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

import mimetypes
import tempfile
from os.path import join, exists, curdir, abspath
from os import listdir, remove, chdir
from zope.interface import implementer
from zipfile import ZipFile, is_zipfile
from shutil import rmtree
from cloudooo.interfaces.file import IFile


@implementer(IFile)
class File(object):
  """File is used to manipulate one temporary file
  stored into the filesystem.
  """

  def __init__(self, base_folder_url, data, source_format):
    """Create an file into file system and store the URL.
    Keyword arguments:
    base_folder_url -- Full path to create a temporary folder
    data -- Content of the document
    source_format -- Document Extension
    """
    self.base_folder_url = base_folder_url
    self.directory_name = self._createDirectory()
    self.original_data = data
    self.source_format = source_format
    self.url = self.load()

  def _createDirectory(self):
     return tempfile.mkdtemp(dir=self.base_folder_url)

  def load(self):
    """Creates one Temporary Document and write data into it.
    Return the url for the document.
    """
    # creates only the url of the file.
    file_path = tempfile.mktemp(suffix=".%s" % self.source_format,
                                dir=self.directory_name)
    # stores the data in temporary file
    open(file_path, 'wb').write(self.original_data)
    # If is a zipfile is need extract all files from whitin the compressed file
    if is_zipfile(file_path):
      zipfile = ZipFile(file_path)
      zip_filename_list = zipfile.namelist()
      if 'mimetype' not in zip_filename_list and \
          '[Content_Types].xml' not in zip_filename_list:
        zipfile_path = file_path
        zipfile.extractall(path=self.directory_name)
        zipfile.close()
        filename_list = listdir(self.directory_name)
        if 'index.html' in filename_list:
          file_path = join(self.directory_name, 'index.html')
        else:
          mimetype_list = ['text/html', 'application/xhtml+xml']
          for filename in filename_list:
            if mimetypes.guess_type(filename)[0] in mimetype_list:
              file_path = join(self.directory_name, filename)
              break
        if zipfile_path != file_path:
          remove(zipfile_path)
    return file_path

  def getContent(self, zip=False):
    """Open the file and returns the content.
    Keyword Arguments:
    zip -- Boolean attribute. If True"""
    if zip:
      current_dir_url = abspath(curdir)
      chdir(self.directory_name)
      zip_path = tempfile.mktemp(suffix=".zip", dir=self.directory_name)
      file_list = listdir(self.directory_name)
      zipfile = ZipFile(zip_path, 'w')
      try:
        for file in iter(file_list):
          zipfile.write(file)
      finally:
        zipfile.close()
      opened_zip = open(zip_path, 'r').read()
      remove(zip_path)
      chdir(current_dir_url)
      return opened_zip
    else:
      return open(self.url, 'r').read()

  def getUrl(self):
    """Returns full path."""
    return self.url

  def restoreOriginal(self):
    """Remake the document with the original document"""
    self.trash()
    self.directory_name = self._createDirectory()
    self.url = self.load()

  def reload(self, url=None):
    """If the first document is temporary and another document is created. Use
    reload to load the new document.

    Keyword Arguments:
    url -- Full path of the new document(default None)
    """
    if self.url != url and url is not None:
      remove(self.url)
      self.url = url

  def trash(self):
    """Remove the file in file system."""
    if exists(self.directory_name):
      rmtree(self.directory_name)
      self.url = None

  def __del__(self):
    self.trash()
