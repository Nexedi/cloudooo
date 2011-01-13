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

from xmlrpclib import ServerProxy, Fault
from base64 import encodestring, decodestring
from cloudoooTestCase import CloudoooTestCase, make_suite
import magic

file_detector = magic.Magic()
DAEMON = True

class TestAllFormats(CloudoooTestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

  def afterSetUp(self):
    """Create connection with cloudooo server"""
    self.proxy = ServerProxy("http://%s:%s/RPC2" % (self.hostname,
                                                    self.cloudooo_port))

  def testTextFormats(self):
    """Test all text formats"""
    self.runTestForType('odt', 'text', 'data/test.odt')

  def testPresentationFormats(self):
    """Test all presentation formats"""
    self.runTestForType('odp', 'presentation', 'data/test.odp')

  def testDrawingFormats(self):
    """Test all drawing formats"""
    self.runTestForType('odg', 'drawing', 'data/test.odg')

  def testSpreadSheetFormats(self):
    """Test all spreadsheet formats"""
    self.runTestForType('ods', 'spreadsheet', 'data/test.ods')

  def testWebFormats(self):
    """Test all web formats"""
    self.runTestForType('html', 'web', 'data/test.html')

  def testGlobalFormats(self):
    """Test all global formats"""
    self.runTestForType('sxg', 'global', 'data/test.sxg')

  def runTestForType(self, source_format, document_type, filename):
    """Generic test"""
    data = open(filename, 'r').read()
    request = {'document_type': document_type}
    extension_list = self.proxy.getAllowedExtensionList(request)
    fault_list = []
    for extension in extension_list:
      try:
        data_output = self.proxy.convertFile(encodestring(data),
                                             source_format,
                                             extension[0])
        magic_result = file_detector.from_buffer(decodestring(data_output))
        file_is_empty = magic_result.endswith(": empty")
        if file_is_empty:
          fault_list.append((source_format, extension[0], magic_result))
      except Fault, err:
        fault_list.append((source_format, extension[0], err.faultString))
    if fault_list:
      template_message = 'input_format: %r\noutput_format: %r\n traceback:\n%s'
      message = '\n'.join([template_message % fault for fault in fault_list])
      self.fail('Failed Conversions:\n' + message)


def test_suite():
  return make_suite(TestAllFormats)

