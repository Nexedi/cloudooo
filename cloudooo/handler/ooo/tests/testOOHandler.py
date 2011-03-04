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

import magic
from os import path
from base64 import encodestring, decodestring
from cloudooo.handler.tests.handlerTestCase import HandlerTestCase, make_suite
from cloudooo.handler.ooo.handler import Handler
from cloudooo.handler.ooo.application.openoffice import openoffice
import os
from lxml import etree
from zipfile import ZipFile

OPENOFFICE = True


class TestHandler(HandlerTestCase):
  """Test OOO Handler and manipulation of OOo Instance"""

  _file_path_list = []

  def _save_document(self, document_output_url, data):
    """Create document in file system"""
    new_file = open(document_output_url, "w")
    new_file.write(data)
    new_file.close()
    self._file_path_list.append(document_output_url)

  def _assert_document_output(self, document, expected_mimetype):
    """Check if the document was created correctly"""
    mime = magic.Magic(mime=True)
    mimetype = mime.from_buffer(document)
    self.assertEquals(mimetype, expected_mimetype)

  def tearDown(self):
    """Cleanup temp files
    """
    while self._file_path_list:
      file_path = self._file_path_list.pop()
      if os.path.exists(file_path):
        os.remove(file_path)
    HandlerTestCase.tearDown(self)

  def testConvertOdtToDoc(self):
    """Test convert ODT to DOC"""
    data = encodestring(open("data/test.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    doc_exported = handler.convert("doc")
    self._assert_document_output(doc_exported, "application/vnd.ms-office")

  def testConvertDocToOdt(self):
    """Test convert DOC to ODT"""
    data = encodestring(open("data/test.doc").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'doc')
    doc_exported = handler.convert("odt")
    self._assert_document_output(doc_exported,
                          "application/vnd.oasis.opendocument.text")

  def testGetMetadata(self):
    """Test getMetadata"""
    data = encodestring(open("data/test.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    metadata = handler.getMetadata()
    self.assertEquals(metadata.get('MIMEType'),
                      'application/vnd.oasis.opendocument.text')
    handler.document.restoreOriginal()
    metadata = handler.getMetadata(True)
    self.assertNotEquals(metadata.get('Data'), '')

  def testSetMetadata(self):
    """Test setMetadata"""
    data = encodestring(open("data/test.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    new_data = handler.setMetadata({"Title": "cloudooo Test -"})
    new_handler = Handler(self.tmp_url,
                            new_data,
                            'odt')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "cloudooo Test -")
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    new_data = handler.setMetadata({"Title": "Namie's working record"})
    new_handler = Handler(self.tmp_url,
                            new_data,
                            'odt')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "Namie's working record")

  def testConvertWithOpenOfficeStopped(self):
    """Test convert with openoffice stopped"""
    openoffice.stop()
    data = encodestring(open("data/test.doc").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'doc')
    doc_exported = handler.convert("odt")
    self._assert_document_output(doc_exported,
                          "application/vnd.oasis.opendocument.text")

  def testGetMetadataWithOpenOfficeStopped(self):
    """Test getMetadata with openoffice stopped"""
    openoffice.stop()
    data = encodestring(open("data/test.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt')
    metadata = handler.getMetadata()
    self.assertEquals(metadata.get('Title'), 'title')
    self.assertEquals(metadata.get('MIMEType'),
              'application/vnd.oasis.opendocument.text')

  def testSetMetadataWithOpenOfficeStopped(self):
    """Test setMetadata with openoffice stopped"""
    openoffice.stop()
    data = encodestring(open("data/test.doc").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'doc')
    new_data = handler.setMetadata({"Title": "cloudooo Test -"})
    new_handler = Handler(self.tmp_url,
                            new_data,
                            'doc')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "cloudooo Test -")

  def testRefreshOdt(self):
    """Test refresh argument"""
    # Check when refreshing is disabled
    data = encodestring(open("data/test_fields.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt',
                        refresh=False)
    doc_exported = handler.convert("odt")
    document_output_url = path.join(self.tmp_url, "testExport.odt")
    self._save_document(document_output_url, doc_exported)
    zip_handler = ZipFile(document_output_url)
    content_tree = etree.fromstring(zip_handler.read('content.xml'))
    self.assertFalse(content_tree.xpath('//text:variable-get[text() = "DISPLAY ME"]',
                                       namespaces=content_tree.nsmap))

    # Check when refreshing is enabled
    data = encodestring(open("data/test_fields.odt").read())
    handler = Handler(self.tmp_url,
                        decodestring(data),
                        'odt',
                        refresh=True)
    doc_exported = handler.convert("odt")
    document_output_url = path.join(self.tmp_url, "testExport.odt")
    self._save_document(document_output_url, doc_exported)
    zip_handler = ZipFile(document_output_url)
    content_tree = etree.fromstring(zip_handler.read('content.xml'))
    self.assertTrue(content_tree.xpath('//text:variable-get[text() = "DISPLAY ME"]',
                                       namespaces=content_tree.nsmap))


def test_suite():
  return make_suite(TestHandler)
