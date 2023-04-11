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

from xmlrpclib import Fault
from cloudooo.tests.cloudoooTestCase import TestCase
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
                                              source_mimetype)[1]
        data_output = data_output['data']
        file_type = self._getFileType(data_output)
        if file_type.endswith(": empty"):
          fault_list.append((source_format, extension, file_type))
      except Fault as err:
        fault_list.append((source_format, extension, err.faultString))
    if fault_list:
      template_message = 'input_format: %r\noutput_format: %r\n traceback:\n%s'
      message = '\n'.join([template_message % fault for fault in fault_list])
      self.fail('Failed Conversions:\n' + message)


