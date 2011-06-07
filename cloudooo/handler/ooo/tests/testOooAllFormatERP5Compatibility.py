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

from xmlrpclib import Fault
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite
from base64 import encodestring

class TestAllFormatsERP5Compatibility(TestCase):
  """
  Test XmlRpc Server using ERP5 compatibility API.
  Needs cloudooo server started
  """

  def testTextFormats(self):
    """Test all text formats"""
    self.runTestForType('data/test.odt', 'odt', 'application/vnd.oasis.opendocument.text')

  def testPresentationFormats(self):
    """Test all presentation formats"""
    self.runTestForType('data/test.odp', 'odp', 'application/vnd.oasis.opendocument.presentation')

  def testDrawingFormats(self):
    """Test all drawing formats"""
    self.runTestForType('data/test.odg', 'odg', 'application/vnd.oasis.opendocument.graphics')

  def testSpreadSheetFormats(self):
    """Test all spreadsheet formats"""
    self.runTestForType('data/test.ods', 'ods', 'application/vnd.oasis.opendocument.spreadsheet')

  def runTestForType(self, filename, source_format, source_mimetype):
    """Generic test"""
    extension_list = self.proxy.getAllowedTargetItemList(source_mimetype)[1]['response_data']
    fault_list = []
    for extension, format in extension_list:
      try:
        data_output = self.proxy.run_generate(filename,
                                              encodestring(
                                              open(filename).read()),
                                              None,
                                              extension,
                                              source_mimetype)[1]['data']
        file_type = self._getFileType(data_output)
        if file_type.endswith(": empty"):
          fault_list.append((source_format, extension, file_type))
      except Fault, err:
        fault_list.append((source_format, extension, err.faultString))
    if fault_list:
      template_message = 'input_format: %r\noutput_format: %r\n traceback:\n%s'
      message = '\n'.join([template_message % fault for fault in fault_list])
      self.fail('Failed Conversions:\n' + message)


def test_suite():
  return make_suite(TestAllFormatsERP5Compatibility)
