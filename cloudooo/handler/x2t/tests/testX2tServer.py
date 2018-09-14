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

