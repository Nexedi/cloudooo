##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
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
from os.path import join
from cloudooo.tests.cloudoooTestCase import TestCase, make_suite


class TestServer(TestCase):
  """Test XmlRpc Server. Needs cloudooo server started"""

  def ConversionScenarioList(self):
    return [
      (join('data', 'test.xlsx'), "xlsx", "xlsy", "application/zip"),
      (join('data', 'test.xlsy'), "xlsy", "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
      (join('data', 'test_with_image.docx'), "docx", "docy", "application/zip"),
      (join('data', 'test_with_image.docy'), "docy", "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ]

  def testConvertOnlyOfficeToFrom(self):
    """Converts xlsx,docx to their y format and y to x"""
    self.runConversionList(self.ConversionScenarioList())

  def FaultConversionScenarioList(self):
    return [
      # Test to verify if server fail when a empty string is sent
      ('', '', ''),
      # Try convert one xlsx for a invalid format
      (open(join('data', 'test.xlsx')).read(), 'xlsx', 'xyz'),
    ]

