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

from cloudooo.tests.cloudoooTestCase import TestCase

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
    for extension in extension_list:
        self._testConvertFile(input_url, source_format, extension[0], None)

