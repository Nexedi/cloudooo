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
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest
import magic
from StringIO import StringIO
from base64 import decodestring
from os import path
from zipfile import ZipFile
from cloudooo.handler.ooo.document import FileSystemDocument
from cloudoooTestCase import make_suite


class TestFileSystemDocument(unittest.TestCase):
  """Test to class FileSystemDocument"""

  def setUp(self):
    """Create data to tests and instantiated a FileSystemDocument"""
    self.tmp_url = '/tmp'
    self.data = decodestring("cloudooo Test")
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
    open(document_test_url, 'wb').write(decodestring("Test Document"))
    self.fsdocument.reload(document_test_url)
    self.assertEquals(path.exists(old_document_url), False)
    self.assertNotEquals(self.fsdocument.original_data,
        self.fsdocument.getContent())
    old_document_url = self.fsdocument.getUrl()
    self.fsdocument.restoreOriginal()
    self.assertEquals(path.exists(old_document_url), False)
    self.assertNotEquals(old_document_url, self.fsdocument.getUrl())
    self.assertTrue(path.exists(self.fsdocument.getUrl()))
    self.assertEquals(self.fsdocument.getContent(), self.data)

  def testgetContent(self):
    """Test if returns the data correctly"""
    self.assertEquals(self.fsdocument.getContent(), self.data)

  def testgetUrl(self):
    """Check if the url is correct"""
    url = self.fsdocument.getUrl()
    self.assertTrue(path.exists(url))

  def testLoadDocumentFile(self):
    """Test if the document is created correctly"""
    url = self.fsdocument.getUrl()
    tmp_document = open(url, 'r').read()
    self.assertEquals(self.data, tmp_document)
    self.fsdocument.trash()
    self.assertEquals(path.exists(url), False)

  def testReload(self):
    """Change url and check if occurs correctly"""
    old_document_url = self.fsdocument.getUrl()
    document_filename = "document"
    document_test_url = path.join(self.fsdocument.directory_name,
                                               document_filename)
    open(document_test_url, 'wb').write(self.data)
    self.fsdocument.reload(document_test_url)
    url = self.fsdocument.getUrl()
    self.assertEquals(path.exists(old_document_url), False)
    self.assertEquals(self.fsdocument.getContent(), self.data)
    self.fsdocument.trash()
    self.assertEquals(path.exists(url), False)

  def testZipDocumentList(self):
    """Tests if the zip file is returned correctly"""
    open(path.join(self.fsdocument.directory_name, 'document2'), 'w').write('test')
    zip_file = self.fsdocument.getContent(True)
    mime = magic.Magic(mime=True)
    mimetype = mime.from_buffer(zip_file)
    self.assertEquals(mimetype, 'application/zip')
    ziptest = ZipFile(StringIO(zip_file), 'r')
    self.assertEquals(len(ziptest.filelist), 2)
    for file in ziptest.filelist:
      if file.filename.endswith("document2"):
        self.assertEquals(file.file_size, 4)
      else:
        self.assertEquals(file.file_size, 9)

  def testSendZipFile(self):
    """Tests if the htm is extrated from zipfile"""
    zip_input_url = 'data/test.zip'
    data = open(zip_input_url).read()
    zipdocument = FileSystemDocument(self.tmp_url, data, 'zip')
    mime = magic.Magic(mime=True)
    mimetype = mime.from_buffer(zipdocument.getContent(True))
    self.assertEquals(mimetype, "application/zip")
    mimetype = mime.from_buffer(zipdocument.getContent())
    self.assertEquals(mimetype, "text/html")
    zipfile = ZipFile(StringIO(zipdocument.getContent(True)))
    self.assertEquals(sorted(zipfile.namelist()),
                sorted(['logo.gif', 'test.htm']))


def test_suite():
  return make_suite(TestFileSystemDocument)
