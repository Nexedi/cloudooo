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

import unittest
from cloudooo.handler.ooo.filter import Filter
from cloudooo.handler.tests.handlerTestCase import make_suite


class TestFilter(unittest.TestCase):
  """Test filter and your interface"""

  def setUp(self):
    """Instatiated Filter with properties"""
    extension = 'pdf'
    filter = 'writer_pdf_Export'
    mimetype = 'application/pdf'
    document_type = "text"
    preferred = True
    sort_index = 1000
    self.filter = Filter(extension, filter, mimetype, document_type,
        preferred=preferred, sort_index=sort_index)

  def testFilter(self):
    """Tests filter gets"""
    self.assertEquals(self.filter.getExtension(), 'pdf')
    self.assertEquals(self.filter.getName(), 'writer_pdf_Export')
    self.assertEquals(self.filter.getMimetype(), 'application/pdf')
    self.assertEquals(self.filter.getSortIndex(), 1000)
    self.assertTrue(self.filter.isPreferred())


def test_suite():
  return make_suite(TestFilter)
