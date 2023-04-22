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

import unittest
import magic
from io import BytesIO
from base64 import decodebytes
from os import path
from zipfile import ZipFile
from cloudooo.handler.ooo.document import FileSystemDocument


class TestFileSystemDocument(unittest.TestCase):
  """Test to class FileSystemDocument"""

  def setUp(self):
    """Create data to tests and instantiated a FileSystemDocument"""
    self.tmp_url = '/tmp'
    self.data = decodebytes(b"cloudooo Test")
    self.fsdocument = FileSystemDocument(self.tmp_url, self.data, 'txt')

  def tearDown(self):
    """Remove the file in file system"""
    if self.fsdocument.getUrl() is not None:
      self.fsdocument.trash()

  def testRestoreOriginal(self):
    """Test if changing the document and call remake, the document back to
    original state"""
    old_document_url = self.fsdocument.getUrl()
    document_filename = "document"
    document_test_url = path.join(self.fsdocument.directory_name,
                                  document_filename)
    with open(document_test_url, 'wb') as f:
      f.write(decodebytes(b"Test Document"))
    self.fsdocument.reload(document_test_url)
    self.assertEqual(path.exists(old_document_url), False)
    self.assertNotEqual(self.fsdocument.original_data,
        self.fsdocument.getContent())
    old_document_url = self.fsdocument.getUrl()
    self.fsdocument.restoreOriginal()
    self.assertEqual(path.exists(old_document_url), False)
    self.assertNotEqual(old_document_url, self.fsdocument.getUrl())
    self.assertTrue(path.exists(self.fsdocument.getUrl()))
    self.assertEqual(self.fsdocument.getContent(), self.data)

  def testgetContent(self):
    """Test if returns the data correctly"""
    self.assertEqual(self.fsdocument.getContent(), self.data)

  def testgetUrl(self):
    """Check if the url is correct"""
    url = self.fsdocument.getUrl()
    self.assertTrue(path.exists(url))

  def testLoadDocumentFile(self):
    """Test if the document is created correctly"""
    url = self.fsdocument.getUrl()
    with open(url, 'rb') as f:
      tmp_document = f.read()
    self.assertEqual(self.data, tmp_document)
    self.fsdocument.trash()
    self.assertEqual(path.exists(url), False)

  def testReload(self):
    """Change url and check if occurs correctly"""
    old_document_url = self.fsdocument.getUrl()
    document_filename = "document"
    document_test_url = path.join(self.fsdocument.directory_name,
                                               document_filename)
    with open(document_test_url, 'wb') as f:
      f.write(self.data)
    self.fsdocument.reload(document_test_url)
    url = self.fsdocument.getUrl()
    self.assertEqual(path.exists(old_document_url), False)
    self.assertEqual(self.fsdocument.getContent(), self.data)
    self.fsdocument.trash()
    self.assertEqual(path.exists(url), False)

  def testZipDocumentList(self):
    """Tests if the zip file is returned correctly"""
    with open(path.join(self.fsdocument.directory_name, 'document2'), 'w') as f:
      f.write('test')
    zip_file = self.fsdocument.getContent(True)
    mime = magic.Magic(mime=True)
    mimetype = mime.from_buffer(zip_file)
    self.assertEqual(mimetype, 'application/zip')
    ziptest = ZipFile(BytesIO(zip_file), 'r')
    self.assertEqual(len(ziptest.filelist), 2)
    for file in ziptest.filelist:
      if file.filename.endswith("document2"):
        self.assertEqual(file.file_size, 4)
      else:
        self.assertEqual(file.file_size, 9)

  def testSendZipFile(self):
    """Tests if the htm is extrated from zipfile"""
    with open('./data/test.zip', 'rb') as f:
      data = f.read()
    zipdocument = FileSystemDocument(self.tmp_url, data, 'zip')
    mime = magic.Magic(mime=True)
    mimetype = mime.from_buffer(zipdocument.getContent(True))
    self.assertEqual(mimetype, "application/zip")
    mimetype = mime.from_buffer(zipdocument.getContent())
    self.assertEqual(mimetype, "text/html")
    zipfile = ZipFile(BytesIO(zipdocument.getContent(True)))
    self.assertEqual(sorted(zipfile.namelist()),
                sorted(['logo.gif', 'test.htm']))


