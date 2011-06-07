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

from cloudooo.tests.cloudoooTestCase import TestCase, make_suite

class TestAllFormats(TestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

  def testTextFormats(self):
    """Test all text formats"""
    self.runTestForType('data/test.odt', 'odt', 'text')

  def testPresentationFormats(self):
    """Test all presentation formats"""
    self.runTestForType('data/test.odp', 'odp', 'presentation')

  def testDrawingFormats(self):
    """Test all drawing formats"""
    self.runTestForType('data/test.odg', 'odg', 'drawing')

  def testSpreadSheetFormats(self):
    """Test all spreadsheet formats"""
    self.runTestForType('data/test.ods', 'ods', 'spreadsheet')

  def testWebFormats(self):
    """Test all web formats"""
    self.runTestForType('data/test.html', 'html', 'web')

  def testGlobalFormats(self):
    """Test all global formats"""
    self.runTestForType('data/test.sxg', 'sxg', 'global')

  def runTestForType(self, input_url, source_format, document_type):
    """Generic test for converting all formats"""
    request = {'document_type': document_type}
    extension_list = self.proxy.getAllowedExtensionList(request)
    fault_list = []
    for extension in extension_list:
        self._testConvertFile(input_url, source_format, extension[0], None)

def test_suite():
  return make_suite(TestAllFormats)
