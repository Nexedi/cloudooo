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

from xmlrpc.client import Fault
from cloudooo.tests.cloudoooTestCase import TestCase
from base64 import encodebytes


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

  def runTestForType(self, filename:str, source_format:str, source_mimetype:str) -> None:
    """Generic test"""
    extension_list = self.proxy.getAllowedTargetItemList(source_mimetype)[1]['response_data']
    with open(filename, 'rb') as f:
      encoded_data = encodebytes(f.read()).decode()

    for extension, _ in extension_list:
      with self.subTest(extension):
        _, data_output, fault = self.proxy.run_generate(filename,
                                              encoded_data,
                                              None,
                                              extension,
                                              source_mimetype)
        self.assertFalse(fault)
        data_output = data_output['data']
        file_type = self._getFileType(data_output)
        self.assertNotIn(": empty", file_type)
        if source_format != extension:
          # when no filter exist for destination format, the document is not converted
          # but silently returned in source format, the assertion below should detect
          # this.
          self.assertNotEqual(source_mimetype, file_type)

