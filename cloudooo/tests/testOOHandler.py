##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
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
from os import path
from subprocess import Popen, PIPE
from base64 import encodestring, decodestring
from cloudoooTestCase import cloudoooTestCase
from cloudooo.handler.oohandler import OOHandler
from cloudooo.application.openoffice import openoffice
from cloudoooTestCase import make_suite

class TestOOHandler(cloudoooTestCase):
  """Test OOHandler and manipulation of OOo Instance"""

  def _save_document(self, document_output_url, data):
    """Create document in file system"""
    open(document_output_url, "w").write(data)

  def _assert_document_output(self, document_output_url, msg):
    """Check if the document was created correctly"""
    stdout, stderr = Popen("file -b %s" % document_output_url,
                          shell=True,
                          stdout=PIPE).communicate()
    self.assertEquals(msg in stdout,
                      True,
                      "\nStdout: %sMsg: %s" % (stdout, msg))

  def testConvertOdtToDoc(self):
    """Test convert ODT to DOC"""
    data = encodestring(open("data/test.odt").read())
    handler = OOHandler(self.tmp_url,
                        decodestring(data),
                        'odt')
    doc_exported = handler.convert("doc")
    document_output_url = path.join(self.tmp_url, "testExport.doc")
    self._save_document(document_output_url, doc_exported)
    msg = 'Microsoft Office Document'
    self._assert_document_output(document_output_url, msg)

  def testConvertDocToOdt(self):
    """Test convert DOC to ODT"""
    data = encodestring(open("data/test.doc").read())
    handler = OOHandler(self.tmp_url,
                        decodestring(data),
                        'doc')
    doc_exported = handler.convert("odt")
    document_output_url = path.join(self.tmp_url, "testConvert.odt")
    self._save_document(document_output_url, doc_exported)
    msg = 'OpenDocument Text\n'
    self._assert_document_output(document_output_url, msg)
    
  def testGetMetadata(self):
    """Test getMetadata"""
    data = encodestring(open("data/test.odt").read())
    handler = OOHandler(self.tmp_url,
                        decodestring(data),
                        'odt')
    metadata = handler.getMetadata()
    self.assertEquals(metadata.get('Data'), '')
    self.assertEquals(metadata.has_key('Data'), True)
    self.assertEquals(metadata.get('MIMEType'),
                      'application/vnd.oasis.opendocument.text')
    handler.document.restoreOriginal() 
    metadata = handler.getMetadata(True)
    self.assertNotEquals(metadata.get('Data'), '')

  def testSetMetadata(self):
    """Test setMetadata"""
    data = encodestring(open("data/test.odt").read())
    handler = OOHandler(self.tmp_url,
                        decodestring(data),
                        'odt')
    new_data = handler.setMetadata({"Title": "cloudooo Test -"})
    new_handler = OOHandler(self.tmp_url,
                            new_data,
                            'odt')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "cloudooo Test -")
    handler = OOHandler(self.tmp_url,
                        decodestring(data),
                        'odt')
    new_data = handler.setMetadata({"Title": "Namie's working record"})
    new_handler = OOHandler(self.tmp_url,
                            new_data,
                            'odt')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "Namie's working record")

  def testConvertWithOpenOfficeStopped(self):
    """Test convert with openoffice stopped"""
    openoffice.stop()
    data = encodestring(open("data/test.doc").read())
    handler = OOHandler(self.tmp_url,
                        decodestring(data),
                        'doc')
    doc_exported = handler.convert("odt")
    document_output_url = path.join(self.tmp_url, "testConvert.odt")
    self._save_document(document_output_url, doc_exported)
    msg = 'OpenDocument Text\n'
    self._assert_document_output(document_output_url, msg)
  
  def testGetMetadataWithOpenOfficeStopped(self):
    """Test getMetadata with openoffice stopped"""
    openoffice.stop()
    data = encodestring(open("data/test.odt").read())
    handler = OOHandler(self.tmp_url,
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
    handler = OOHandler(self.tmp_url,
                        decodestring(data),
                        'doc')
    new_data = handler.setMetadata({"Title": "cloudooo Test -"})
    new_handler = OOHandler(self.tmp_url,
                            new_data,
                            'doc')
    metadata = new_handler.getMetadata()
    self.assertEquals(metadata.get('Title'), "cloudooo Test -")

def test_suite():
  return make_suite(TestOOHandler)

if __name__ == "__main__":
  from cloudoooTestCase import startFakeEnvironment, stopFakeEnvironment
  startFakeEnvironment()
  suite = unittest.TestLoader().loadTestsFromTestCase(TestOOHandler)
  unittest.TextTestRunner(verbosity=2).run(suite)
  stopFakeEnvironment()
